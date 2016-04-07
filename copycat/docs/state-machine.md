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

Commands are defined by implementing the [`Command`][Command] interface. `Command` takes a single generic argument that defines the output (return value) of the command implementation.

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

The base `Operation` interface implements Java's `Serializable`, so all operations can be serialized without any custom serialization logic. However, Java serialization is slow and innefficient and is therefore not recommended for production. Users should implement `CatalystSerializable`, provide a custom `TypeSerializer`, or use one of the generic serialization framework plugins like Kryo or Jackson for the best performance.

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

The base `Operation` interface implements Java's `Serializable`, so all operations can be serialized without any custom serialization logic. However, Java serialization is slow and innefficient and is therefore not recommended for production. Users should implement `CatalystSerializable`, provide a custom `TypeSerializer`, or use one of the generic serialization framework plugins like Kryo or Jackson for the best performance.

## Implementing state machine operations

Commands and queries define the interface between a client and the state machine, and methods on the state machine define the behavior and output of an operation submitted to the cluster. Operations are single-argument `public` methods on the `StateMachine` implementation that take a single `Commit` argument. The generic argument to the `Commit` defines the operation expected by the method. Copycat will infer operation methods based on the generic argument.

Remember, `Command`s are operations that modify the state of the state machine. In the case of the `MapStateMachine`, the `Put` operation is a command since it writes an entry in the map:

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

The return value of the operation method is the response that will be sent back to the client. In the case of the `Put` command, we send the previous value returned by the `Map` interface. Once the `Commit` is no longer needed, we `release` the commit to allow Copycat to recycle the object and compact the commit from the underlying log if necessary.

{:.callout .callout-warning}
Important: `Commit`s must be `release`d once no longer needed by the state machine. Failure to release a commit will result in the replicated log growing unbounded.

`Query` operations are implemented in the same way as `Command`s. To implement a query operation, add a `public` method to the `StateMachine` class taking a single `Commit` object.

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

As with all other operation implementations, query `Commit`s must be `release`d once the operation is complete.

### The Commit object

As demonstrated above, operations submitted to the cluster are applied to state machines wrapped in a `Commit` object. The commit object provides some useful information that can be used to associate operations with clients or approximate the progression of real-time and logical time in the cluster. The `Commit` object exposes the following properties:

* `index()` - The index of the commit in the underlying Raft replicated log. This index is guaranteed to be unique and monotonically increasing, and all state machines are guaranteed to see the same operation for the same commit index.
* `time()` - The approximate wall-clock time at which the operation was committed. This time is written to the underlying log by the leader when the operation is first logged. Commit times are guaranteed to be monotonically increasing.
* `session()` - The [`Session`][Session] that submitted the operation. This can be used to [send session event messages](#publishing-session-events) to the client.

### Scheduling callbacks

```java
public class PutWithTtl implements Command<Object> {
  public Object key;
  public Object value;
  public long ttl;

  public PutWithTtl() {
  }

  public PutWithTtl(Object key, Object value, long ttl) {
    this.key = key;
    this.value = value;
    this.ttl = ttl;
  }

  @Override
  public CompactionMode mode() {
    return CompactionMode.EXPIRING;
  }
}
```

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

## Working with client sessions

...

### Listening for session state changes

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

### Publishing session events

```java
public class MapEntryEvent {
  public Object key;
  public Object oldValue;
  public Object newValue;

  public MapEntryEvent(Object key, Object oldValue, Object newValue) {
    this.key = key;
    this.oldValue = oldValue;
    this.newValue = newValue;
  }
}
```

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

```java
client.onEvent("change", event -> {
  ...
});
```

## State machine snapshots

...

### Storing snapshots

```java
public class MapStateMachine extends StateMachine implements Snapshottable {
  private Map<Object, Object> map = new HashMap<>();

  @Override
  public void snapshot(SnapshotWriter writer) {
    writer.writeObject(map);
  }
}
```

### Installing snapshots

```java
public class MapStateMachine extends StateMachine implements Snapshottable {
  private Map<Object, Object> map = new HashMap<>();

  @Override
  public void install(SnapshotReader reader) {
    map = reader.readObject();
  }
}
```

## Incremental compaction

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

### Compaction modes

* `DEFAULT` - Based on the interface of the `StateMachine` implementation. If the state machine implements `Snapshottable`, the compaction mode is `SNAPSHOT`, else it is `SEQUENTIAL`.
* `SNAPSHOT` - Indicates that the operation is stored in a snapshot.
* `RELEASE` - Indicates that the operation can be compacted once `release`d by the state machine.
* `QUORUM` - Indicates that the operation can be compacted once stored on a majority of servers and `release`d by the state machine.
* `FULL` - Indicates that the operation can be compacted once stored on all servers and `release`d by the state machine.
* `SEQUENTIAL` - Indicates that the operation can only be compacted once stored on all servers and `release`d by the state machine, and the operation must be compacted sequentially.
* `EXPIRING` - Indicates that the operation is an expiring command. Expiring commands can only be compacted once stored on all servers and `release`d by the state machine, and the operation must be compacted sequentially.
* `TOMBSTONE` - Indicates that the operation is a tombstone. Tombstones can only be compacted once stored on all servers and `release`d by the state machine, and the operation must be compacted sequentially.
* `UNKNOWN` - Indicates that the operation compaction mode is unknown. Copycat will use the strictest (and most inefficient) compaction mode.

### Tracking commit liveness

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

{% include common-links.html %}
