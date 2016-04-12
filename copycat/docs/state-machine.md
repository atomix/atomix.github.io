---
layout: docs
project: copycat
menu: docs
title: State Machines
first-section: state-machine
---

{:.no-margin-top}
State machines are the application layer of a Copycat cluster. Clients submit state machine operations, and Copycat logs and replicates operations and applies them to state machines in strict order on all servers. The state of a state machine is the sum of its ordered inputs. When a state machine operation is committed through the Raft cluster, it's applied to the replicated state machine, and the state machine's output (return value) is sent back to the client as a response.

{:.callout .callout-danger}
Important: State machines must be deterministic

## Creating a state machine

State machines are defined by simply extending the base [`StateMachine`][StateMachine] class.

```java
public class MapStateMachine extends StateMachine {
  private Map<Object, Object> map = new HashMap<>();
}
```

## Defining state machine operations

State machine operations are instances of the [`Operation`][Operation] interface that are submitted to the cluster by clients where they're logged and replicated before being applied to the state machine. Once a state machine operation is committed, it is applied on the state machine on each server in the cluster.

State machines may accept two types of operations: commands and queries. Commands represent operations that modify the state of a state machine, and queries represent operations which read but do not modify the system's state. This distinction is necessary for performance operations.

### State machine commands

Commands are state machine operations that modify the system's state. When submitted to a Copycat cluster, commands are always proxied to the cluster leader where they're logged and replicated to a majority of the cluster before being committed and applied to the state machine.

Commands are defined by implementing the [`Command`][Command] interface. [`Command`][Command] takes a single generic argument that defines the output (return value) of the command implementation.

```java
public class Put implements Command<Object> {
  public Object key;
  public Object value;

  public Put() {
  }

  public Put(Object key, Object value) {
    this.key = key;
    this.value = value;
  }
}
```

In this case, the `PutCommand` outputs an `Object` (the previous value).

The base [`Operation`][Operation] interface implements Java's [`Serializable`][Serializable], so all operations can be serialized without any custom serialization logic. However, Java serialization is slow and innefficient and is therefore not recommended for production. Users should implement [`CatalystSerializable`][CatalystSerializable], provide a custom [`TypeSerializer`][TypeSerializer], or use one of the generic serialization framework plugins like Kryo or Jackson for the best performance.

### State machine queries

Queries are state machine operations that read but *do not modify* system state. When submitted to a Copycat cluster, queries may be handled differently depending on the query's [`ConsistencyLevel`][Query.ConsistencyLevel]. Some queries may only be applied on the leader, and others may only be applied on followers. Queries will *never* be applied on all servers, and for that reason it's critical that queries never monofy the state of a state machine.

Queries are defined by implementing the [`Query`][Query] interface. As with commands, the `Query` interface takes a single generic argument that defines the query output (return value) type.

```java
public class Get implements Query<Object> {
  public Object key;

  public Get() {
  }

  public Get(Object key) {
    this.key = key;
  }
}
```

{:.callout .callout-danger}
Important: Queries should *never* modify the state of a state machine. Copycat cannot guarantee consistency for improperly implemented state machine operations.

The base [`Operation`][Operation] interface implements Java's [`Serializable`][Serializable], so all operations can be serialized without any custom serialization logic. However, Java serialization is slow and innefficient and is therefore not recommended for production. Users should implement [`CatalystSerializable`][CatalystSerializable], provide a custom [`TypeSerializer`][TypeSerializer], or use one of the generic serialization framework plugins like Kryo or Jackson for the best performance.

## Implementing state machine operations

Commands and queries define the interface between a client and the state machine, and methods on the state machine define the behavior and output of an operation submitted to the cluster. Operations are single-argument `public` methods on the [`StateMachine`][StateMachine] implementation that take a single [`Commit`][Commit] argument. The generic argument to the [`Commit`][Commit] defines the operation expected by the method. Copycat will infer operation methods based on the generic argument.

Remember, [`Command`][Command]s are operations that modify the state of the state machine. In the case of the `MapStateMachine`, the `Put` operation is a command since it writes an entry in the map:

```java
public class MapStateMachine extends StateMachine {
  private Map<Object, Object> map = new HashMap<>();

  public Object put(Commit<Put> commit) {
    try {
      return map.put(commit.operation().key, commit.operation().value);
    } finally {
      commit.release();
    }
  }
}
```

The return value of the operation method is the response that will be sent back to the client. In the case of the `Put` command, we send the previous value returned by the `Map` interface. Once the [`Commit`][Commit] is no longer needed, we `release` the commit to allow Copycat to recycle the object and compact the commit from the underlying log if necessary.

{:.callout .callout-warning}
Important: [`Commit`][Commit]s must be `release`d once no longer needed by the state machine. Failure to release a commit will result in the replicated log growing unbounded.

[`Query`][Query] operations are implemented in the same way as [`Command`][Command]s. To implement a query operation, add a `public` method to the [`StateMachine`][StateMachine] class taking a single [`Commit`][Commit] object.

```java
public class MapStateMachine extends StateMachine {
  private Map<Object, Object> map = new HashMap<>();

  public Object get(Commit<Get> commit) {
    try {
      return map.get(commit.operation().key);
    } finally {
      commit.release();
    }
  }
}
```

As with all other operation implementations, query [`Commit`][Commit]s must be `release`d once the operation is complete.

### The Commit object

As demonstrated above, operations submitted to the cluster are applied to state machines wrapped in a [`Commit`][Commit] object. The commit object provides some useful information that can be used to associate operations with clients or approximate the progression of real-time and logical time in the cluster. The [`Commit`][Commit] object exposes the following properties:

* `index()` - The index of the commit in the underlying Raft replicated log. This index is guaranteed to be unique and monotonically increasing, and all state machines are guaranteed to see the same operation for the same commit index.
* `time()` - The approximate wall-clock time at which the operation was committed. This time is written to the underlying log by the leader when the operation is first logged. Commit times are guaranteed to be monotonically increasing.
* `session()` - The [`Session`][Session] that submitted the operation. This can be used to [send session event messages](#publishing-session-events) to the client.

### Scheduling callbacks

State machines support deterministic scheduling of time-based callbacks for altering the state of a state machine on a schedule. For example, a map state machine can implement expiring keys by through the state machine scheduler. To schedule callbacks within the state machine, use the [`StateMachineExecutor`][StateMachineExecutor]'s [`schedule(Duration)`][StateMachineExecutor.schedule] method:

```java
public class MapStateMachine extends StateMachine {
  private Map<Object, Object> map = new HashMap<>();

  public Object putWithTtl(Commit<PutWithTtl> commit) {
    map.put(commit.operation().key, commit);
    executor.schedule(Duration.ofMillis(commit.operation().ttl, () -> {
      map.remove(commit.operation().key);
      commit.release();
    });
  }
}
```

When a state machine schedules a callback, the callback will be executed after *approximately* the given duration. Scheduled callbacks are dependent on writes to the underlying Raft log and therefore are not very precise, but they suffice for many use cases.

{:.callout .callout-danger}
State machines should never schedule callbacks using Java's `Timer`. Only use the `StateMachineExecutor` for deterministic time-based scheduling.

## Working with client sessions

Each [`Command`][Command] and [`Query`][Query] submitted to the cluster is submitted by a client through its [`Session`][Session]. All operations applied to a state machine have contain a [`ServerSession`][ServerSession] which acts as a server-side reference to the client that submitted the operation. Furthermore, state machines can listen for changes in session states to react to clients connecting to and disconnecting from the cluster, and event messages can be sent to clients via a [`ServerSession`][ServerSession].

### Listening for session state changes

To listen for changes in session states, implement the [`SessionListener`][SessionListener] interface. When the [`SessionListener`][SessionListener] interface is implemented by a [`StateMachine`][StateMachine], Copycat will automatically notify the state machine each time a session is created or destroyed.

The [`SessionListener`][SessionListener] interface requires four methods:

* `register(ServerSession)` - called when a new session is registered by a client
* `unregister(ServerSession)` - called when a session is unregistered by a client
* `expire(ServerSession)` - called when a session is expired by the cluster
* `close(ServerSession)` - called after a session is either unregistered by a client or expired by the leader

```java
public class MapStateMachine extends StateMachine implements SessionListener {
  private Map<Object, Object> map = new HashMap<>();
  private Set<ServerSession> sessions = new HashSet<>();

  @Override
  public void register(ServerSession session) {
    sessions.add(session);
  }

  @Override
  public void unregister(ServerSession session) {
  }

  @Override
  public void expire(ServerSession session) {
  }

  @Override
  public void close(ServerSession session) {
    sessions.remove(session);
  }
}
```

As with normal state machine operations, session events are guaranteed to occur at the same logical time on all servers.

### Publishing session events

Up until now, the documentation has described how state machines can react to command and query requests from clients. But for more complex use cases, state machines often may need to communicate directly with clients as well. For example, a lock state machine implemented purely through commands would require the client to periodically poll the cluster to determine if it has acquired a lock. A more optimal model is for the cluster to notify the client when the is acquires a lock. Copycat provides the ability for state machines to push arbitrary messages to clients via the [`ServerSession`][ServerSession] through its session events framework.

State machines can publish any number of event messages to any client in response to a [`Command`][Command] being applied to the state machine. To publish an event message to a client, use the [`publish(String, Object)`][ServerSession.publish] method:

```java
public class MapStateMachine extends StateMachine {
  private Map<Object, Object> map = new HashMap<>();
  private Set<ServerSession> listeners = new HashSet<>();

  public void listen(Commit<Listen> commit) {
    listeners.add(commit.session());
    commit.release();
  }

  public Object put(Commit<Put> commit) {
    try {
      Object oldValue = map.put(commit.operation().key, commit.operation().value);
      listeners.forEach(session -> {
        session.publish("change", new MapEntryEvent(commit.operation().key, oldValue, commit.operation().value));
      });
      return oldValue;
    } finally {
      commit.release();
    }
  }
}
```

When an event message is published to a client through its session, the message will be pushed to the client by the server to which the client is connected. As with all other state machine operations, though, it's critical that all state machines perform the same behaviors. While only the server to which the client is connected actually sends event messages to the client, Copycat internally stores event messages published on all servers in memory until they're acknowledged by the client. This allows events to be resent to the client in the event of a server failure or in the event the client simply switches servers.

{:.callout .callout-warning}
State machines can only publish session events within [`Command`][Command] methods. Attempting to publish a session event within a [`Query`][Query] method will result in an exception.

Clients handle event messages by registering event listeners via [`CopycatClient`][CopycatClient]'s [`onEvent(String, Consumer)`][CopycatClient.onEvent] method:

```java
client.onEvent("change", event -> {
  ...
});
```

Internally, Copycat servers and clients coordinate with one another to ensure events are received on the client in the order in which they were published by the state machine, and events are sequenced with responses. In the example above, the client that submits the `Put` operation will first see its request complete, and after the request completes it will receive the `MapEntryEvent`.

## State machine snapshots

One of the most critical aspects of implementing state machines in practice is supporting log compaction. As [`Command`][Command]s are written to the Raft log and applied to the state machine, the size of the underlying [`Log`][Log] on disk can grow without bound. In order to allow Copycat to reduce the size of the log, it is the responsibility of [`StateMachine`][StateMachine] implementations to facilitate the persistence of the state machine state outside of the context of the log. Typically, this is done by implementing snaphot support.

To implement support for snapshotting a state machine, implement the [`Snapshottable`][Snapshottable] interface. When implementing [`Snapshottable`][Snapshottable], state machines must implement two simple methods:

* `snapshot(SnapshotWriter)` - writes a snapshot of the state machine state to disk
* `install(SnapshotReader)` - reads a snapshot of the state machine state from disk

### Storing snapshots

For [`Snapshottable`][Snapshottable] state machines, as the underlying [`Log`][Log] grows, Copycat will periodically call the [`snapshot(SnapshotWriter)`][Snapshottable.snapshot] to request a snapshot of the state machine's state. The provided [`SnapshotWriter`][SnapshotWriter] must be used by the state machine to write snapshottable state to disk.

```java
public class MapStateMachine extends StateMachine implements Snapshottable {
  private Map<Object, Object> map = new HashMap<>();

  @Override
  public void snapshot(SnapshotWriter writer) {
    writer.writeObject(map);
  }
}
```

The [`SnapshotWriter`][SnapshotWriter] supports serialization of objects within the state machine via the `writeObject` method. When writing serializable objects to the snapshot, the server's configured [`Serializer`][Serializer] is used, so state machines must ensure that serializable types are properly registered.

*When* the [`snapshot(SnapshotWriter)`][Snapshottable.snapshot] method will be called is unspecified. Copycat determines when to take snapshots based on the size of the log and the size of individual segments within the log.

### Installing snapshots

To support restoration of snapshots from disk or over the network, [`Snapshottable`][Snapshottable] state machines implement the [`install(SnapshotReader)`][Snapshottable.install] method. When called, state machines should restore all snapshottable state from the provided [`SnapshotReader`].

```java
public class MapStateMachine extends StateMachine implements Snapshottable {
  private Map<Object, Object> map = new HashMap<>();

  @Override
  public void install(SnapshotReader reader) {
    map = reader.readObject();
  }
}
```

The [`install(SnapshotReader)`][Snapshottable.install] will typically be called each time the server starts to recover the system's state. However, it can be called at other times as well. For example, if a server falls too far behind the leader, the leader may compact its [`Log`][Log] and replicate a snapshot in lieu of log entries. State machines should not make any assumptions about when snapshots will be installed.

## Incremental compaction

Underlying Copycat's snapshot support is an incremental log compaction algorithm. Snapshots provide only an abstraction over the incremental compaction algorithm. But state machines may also use the incremental compaction process directly by explicitly managing the [`Commit`][Commit]s applied to the state machine.

### Compaction modes

To support incremental compaction, state machines must explicitly define how each [`Command`][Command] supported by the state machine should be compacted from the log by specifying the command's [`CompactionMode`][Command.CompactionMode]. Typically, compaction methods are indicated by command types. For example, commands applied to state machines that implement the [`Snapshottable`][Snapshottable] interface automatically default to the `SNAPSHOT` compaction mode, indicating that commands can be removed after a snapshot is taken.

* `DEFAULT` - Based on the interface of the [`StateMachine`][StateMachine] implementation. If the state machine implements [`Snapshottable`][Snapshottable], the compaction mode is `SNAPSHOT`, else it is `SEQUENTIAL`.
* `SNAPSHOT` - Indicates that the operation is stored in a snapshot.
* `RELEASE` - Indicates that the operation can be compacted once `release`d by the state machine.
* `QUORUM` - Indicates that the operation can be compacted once stored on a majority of servers and `release`d by the state machine.
* `FULL` - Indicates that the operation can be compacted once stored on all servers and `release`d by the state machine.
* `SEQUENTIAL` - Indicates that the operation can only be compacted once stored on all servers and `release`d by the state machine, and the operation must be compacted sequentially.
* `EXPIRING` - Indicates that the operation is an expiring command. Expiring commands can only be compacted once stored on all servers and `release`d by the state machine, and the operation must be compacted sequentially.
* `TOMBSTONE` - Indicates that the operation is a tombstone. Tombstones can only be compacted once stored on all servers and `release`d by the state machine, and the operation must be compacted sequentially.
* `UNKNOWN` - Indicates that the operation compaction mode is unknown. Copycat will use the strictest (and most inefficient) compaction mode.

For state machines that implement incremental compaction, commands typically fall into one of two types of compaction - `RELEASE` and `TOMBSTONE` - where commands that alter the state machine's state are marked with the `RELEASE` compaction mode and commands that delete state machine state are marked with the `TOMBSTONE` compaction mode. To read more about why compaction modes matter see the [log compaction documentation][log-compaction].

To define the [`CompactionMode`][Command.CompactionMode] for a [`Command`][Command], override the `mode()` method in the [`Command`][Command] implementation:

```java
public class Put implements Command<Object> {
  public Object key;
  public Object value;

  public Put() {
  }

  public Put(Object key, Object value) {
    this.key = key;
    this.value = value;
  }

  @Override
  public CompactionMode mode() {
    return CompactionMode.RELEASE;
  }
}
```

### Tracking commit liveness

Incremental compaction works by tracking the liveness of individual [`Commit`][Commit]s applied to a state machine. When incremental compaction is used, it is the responsibility of the [`StateMachine`][StateMachine] implementation to hold references to commits as long as they contribute to the state machine's state. Once a [`Commit`][Commit] is superseded or removed by another [`Commit`][Commit], the state machine releases it by calling the `release()` method, making it available for compaction.

```java
public class MapStateMachine extends StateMachine implements Snapshottable {
  private Map<Object, Commit<Put>> map = new HashMap<>();

  public Object put(Commit<Put> commit) {
    return map.put(commit.operation().key, commit);
  }

  public Object get(Commit<Get> commit) {
    try {
      return map.get(commit.operation().key);
    } finally {
      commit.release();
    }
  }
}
```

### Handling tombstones

Tombstones are [`Command`][Command]s that *remove* state machine state. It's particularly critical that state machines that support incremental compaction appropriately mark tombstone commands as such with the `TOMBSTONE` [`CompactionMode`][Command.CompactionMode]:

```java
public class Remove implements Command<Object> {
  public Object key;

  public Remove() {
  }

  public Remove(Object key) {
    this.key = key;
  }

  @Override
  public CompactionMode mode() {
    return CompactionMode.TOMBSTONE;
  }
}
```

When a tombstone is applied to a state machine, *after* the state that the tombstone deletes has been removed and released, the tombstone [`Command`][Command] itself can be released:

```java
public class MapStateMachine extends StateMachine implements Snapshottable {
  private Map<Object, Commit<Put>> map = new HashMap<>();

  public Object put(Commit<Put> commit) {
    return map.put(commit.operation().key, commit);
  }

  public Object get(Commit<Get> commit) {
    try {
      return map.get(commit.operation().key);
    } finally {
      commit.release();
    }
  }

  public Object remove(Commit<Remove> commit) {
    try {
      Commit<Put> removed = map.remove(commit.operation().key);
      if (removed != null) {
        Object result = removed.command().value;
        removed.release();
        return result;
      }
      return null;
    } finally {
      commit.release();
    }
  }
}
```

When a tombstone command is released by a state machine, Copycat will take care to ensure the command is retained in the [`Log`][Log] as long as is necessary to ensure it's applied on all servers.

{% include common-links.html %}
