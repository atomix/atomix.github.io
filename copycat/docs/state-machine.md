---
layout: docs
project: copycat
menu: docs
title: Raft Consensus Algorithm
pitch: Sophisticated Raft Consensus implementation
first-section: state-machine
---

## State machines

State machines are the server-side representation of state based on a series of [commands](#commands) and [queries](#queries) submitted to the Raft cluster.

{:.callout .callout-danger}
Important: State machines must be deterministic

**All state machines must be deterministic**

Given the same commands in the same order, state machines must always arrive at the same state with the same output.

Non-deterministic state machines will break the guarantees of the Raft consensus algorithm. Each [server](#CopycatServer) in the cluster must have *the same state machine*. When a command is submitted to the cluster, the command will be forwarded to the leader, logged to disk or memory, and replicated to a majority of the cluster before being applied to the state machine, and the return value for a given command or query is returned to the requesting client.

State machines are created by extending the base `StateMachine` class and overriding the `configure(StateMachineExecutor)` method:

```java
public class MyStateMachine extends StateMachine {
}
```

Internally, state machines are backed by a series of entries in an underlying log. In the event of a crash and recovery, state machine commands in the log will be replayed to the state machine. This is why it's so critical that state machines be deterministic.

#### Registering operations

The `StateMachineExecutor` is a special [Context][contexts] that is responsible for applying [commands](#commands) and [queries](#queries) to the state machine. As operations are committed on each server in the cluster, the `StateMachineExecutor` will execute appropriate state machine callbacks according to the registered operations. Operations are handled by registering callbacks on the provided `StateMachineExecutor` in the `configure` method:

```java
@Override
protected void configure(StateMachineExecutor executor) {
  executor.register(SetCommand.class, this::set);
  executor.register(GetQuery.class, this::get);
}
```

Operation callbacks must accept a `Commit<T extends Operation<?>>` object for the registered operation type:

```java
private Object get(Commit<GetQuery> commit) {
  return map.get(commit.operation().key());
}
```

State machine operations can also be registered by simply creating `public` methods on the state machine class:

```java
public Object get(Commit<GetQuery> commit) {
  return map.get(commit.operation().key());
}
```

## Commands

Commands are operations that modify the state machine state. When a command operation is submitted to the Copycat cluster, the command is logged to disk or memory (depending on the `Storage` configuration) and replicated via the Raft consensus protocol. Once the command has been stored on a majority cluster members, it will be applied to the server-side [StateMachine](#state-machines) and the output will be returned to the client.

Commands are defined by implementing the `Command` interface:

```java
public class Set<T> implements Command<T> {
  private final String value;

  public Set(String value) {
    this.value = value;
  }

  /**
   * The value to set.
   */
  public String value() {
    return value;
  }
}
```

The [Command][Command] interface extends [Operation][Operation] which is `Serializable` and can be sent over the wire with no additional configuration. However, for the best performance users should implement [CopycatSerializable][CopycatSerializable] or register a [TypeSerializer][TypeSerializer] for the type. This will reduce the size of the serialized object and allow Copycat's [Serializer](#serializer) to optimize class loading internally during deserialization.

### Command consistency

By default, [commands](#commands) submitted to the Copycat cluster are guaranteed to be linearizable. Linearizable commands are sequenced to the Raft log in the order in which they were executed on the client (program order) and are guaranteed to occur some time between invocation and response. However, sequencing commands may be unnecessary overhead for clients that don't submit concurrent writes, so Copycat allows [Command][Command] implementations to specify a `ConsistencyLevel` to control how commands are handled by the cluster.

To configure the consistency level for a `Command`, simply override the default `consistency()` getter:

```java
public class Put<K, V> implements Command {

  @Override
  public ConsistencyLevel consistency() {
    return Consistency.SEQUENTIAL;
  }

}
```

The consistency level returned by the overridden `consistency()` method amounts to a *minimum consistency requirement*. In many cases, a `CAUSAL` command can actually result in `LINEARIZABLE` write depending on whether the client submits concurrent commands.

Copycat provides two consistency levels for commands:

* `Command.ConsistencyLevel.LINEARIZABLE` - Provides guaranteed linearizability by ensuring commands are written to the Raft log in the order in which they occurred on the client and events are received by clients between request and response.
* `Command.ConsistencyLevel.SEQUENTIAL` - Provides guaranteed linearizability for commands and sequential consistency for related events. Events may be received by clients at some arbitrary point in the future.
* `Command.ConsistencyLevel.NONE` - Provides no additional consistency guarantees, potentially allowing a single command to be applied to the state machine multiple times.

## Queries

In contrast to commands which perform state change operations, queries are read-only operations which do not modify the server-side state machine's state. Because read operations do not modify the state machine state, Copycat can optimize queries according to read from certain nodes according to the configuration and [may not require contacting a majority of the cluster in order to maintain consistency](#query-consistency). This means queries can significantly reduce disk and network I/O depending on the query configuration, so it is strongly recommended that all read-only operations be implemented as queries.

To create a query, simply implement the [Query][Query] interface:

```java
public class Get<T> implements Query {
}
```

As with [Command][Command], [Query][Query] extends the base [Operation][Operation] interface which is `Serializable`. However, for the best performance users should implement [CopycatSerializable][CopycatSerializable] or register a [TypeSerializer][TypeSerializer] for the type.

### Query consistency

By default, [queries](#queries) submitted to the Copycat cluster are guaranteed to be linearizable. Linearizable queries are forwarded to the leader where the leader verifies its leadership with a majority of the cluster before responding to the request. However, this pattern can be inefficient for applications with less strict read consistency requirements. In those cases, Copycat allows [Query][Query] implementations to specify a `ConsistencyLevel` to control how queries are handled by the cluster.

To configure the consistency level for a `Query`, simply override the default `consistency()` getter:

```java
public class Get<T> implements Query {

  @Override
  public ConsistencyLevel consistency() {
    return Consistency.SEQUENTIAL;
  }

}
```

The consistency level returned by the overridden `consistency()` method amounts to a *minimum consistency requirement*. In many cases, a `SEQUENTIAL` query can actually result in `LINEARIZABLE` read depending the server to which a client submits queries, but clients can only rely on the configured consistency level.

Copycat provides four consistency levels for queries:

* `Query.ConsistencyLevel.LINEARIZABLE` - Provides guaranteed linearizability by forcing all reads to go through the leader and verifying leadership with a majority of the Raft cluster prior to the completion of all operations
* `Query.ConsistencyLevel.BOUNDED_LINEARIZABLE` - Provides best-effort optimized linearizability by forcing all reads to go through the leader but allowing most queries to be executed without contacting a majority of the cluster so long as less than the election timeout has passed since the last time the leader communicated with a majority
* `Query.ConsistencyLevel.SEQUENTIAL` - Provides sequential consistency by allowing clients to read from followers and ensuring that clients see state progress monotonically
* `Query.ConsistencyLevel.CAUSAL` - Provides causal consistency which ensures that clients will always see state progress monotonically for non-overlapping queries

### Commits

As [commands](#commands) and [queries](#queries) are logged and replicated through the Raft cluster, they gain some metadata that is not present in the original operation. By the time operations are applied to the state machine, they've gained valuable information that is exposed in the [Commit][Commit] wrapper class:

* `Commit.index()` - The sequential index of the commit in the underlying `Log`. The index is guaranteed to increase monotonically as commands are applied to the state machine. However, because [queries](#queries) are not logged, they may duplicate the indices of commands.
* `Commit.time()` - The approximate `Instant` at which the commit was logged by the leader through which it was committed. The commit time is guaranteed never to decrease.
* `Commit.session()` - The [Session](#sessions) that submitted the operation to the cluster. This can be used to send events back to the client.
* `Commit.operation()` - The operation that was committed.

```java
protected Object get(Commit<GetQuery> commit) {
  return map.get(commit.operation().key());
}
```

### Sessions

Sessions are representative of a single client's connection to the cluster. For each `Commit` applied to the state machine, an associated `Session` is provided. State machines can use sessions to associate clients with state changes or even send events back to the client through the session:

```java
protected Object put(Commit<PutCommand> commit) {
  commit.session().publish("put", commit.operation().key());
  return map.put(commit.operation().key(), commit.operation().value());
}
```

The `StateMachineContext` provides a view of the local server's state at the time a [command](#command) or [query](#queries) is applied to the state machine. Users can use the context to access, for instance, the list of `Session`s currently registered in the cluster.

To get the context, call the protected `context()` getter from inside the state machine:

```java
for (Session session : context().sessions()) {
  session.publish("message", "Hello world!");
}
```

### Listening for changes in sessions

State machines can listen for clients opening new sessions with the cluster or for existing sessions being expired by the cluster or closed by the client. All state changes in server `Session`s happen deterministically - they occur at the same *logical* time on each server in the cluster, so it's safe to rely on session state changes to change the state of the state machine.

To listen for changes in client sessions, implement the `SessionListener` interface:

```java
public class MyStateMachine extends StateMachine implements SessionListener {

  @Override
  public void register(Session session) {
  }

  @Override
  public void expire(Session session) {
  }

  @Override
  public void unregister(Session session) {
  }

  @Override
  public void close(Session session) {
  }

}
```

### Commit cleaning

As commands are submitted to the cluster and applied to the Raft state machine, the underlying log grows. Without some mechanism to reduce the size of the log, the log would grow without bound and ultimately servers would run out of disk space. Raft suggests a few different approaches of handling log compaction. Copycat uses the log cleaning approach.

`Commit` objects are backed by entries in Copycat's replicated log. When a `Commit` is no longer needed by the `StateMachine`, the state machine should clean the commit from Copycat's log by calling the `close()` method:

```java
protected void remove(Commit<RemoveCommand> commit) {
  map.remove(commit.operation().key());
  commit.close();
}
```

Internally, the `close()` call will be proxied to Copycat's underlying log:

```java
log.clean(commit.index());
```

As commits are released from the state machine, entries in the underlying log will be marked for deletion. *Note that it is not safe to assume that once a commit is closed it is permanently removed from the log*. Cleaning an entry only *marks* it for deletion, and the entry won't actually be removed from the log until a background thread compacts the relevant log segment. This means in the event of a crash-recovery and replay of the log, a previously `close`ed commit may still exists. For this reason, if a commit is dependent on a prior commit, state machines should only `close` those commits if no prior related commits have been seen. (More on this later)

Once the underlying `Log` has grown large enough, and once enough commits have been cleaned from the log, a pool of background threads will carry out their task to rewrite segments of the log to remove commits (entries) for which `close()` has been called:

#### Deterministic scheduling

In addition to registering operation callbacks, the `StateMachineExecutor` also facilitates deterministic scheduling based on the Raft replicated log.

```java
executor().schedule(Duration.ofSeconds(1), () -> System.out.println("One deterministic second later"));
```

Because of the complexities of coordinating distributed systems, time does not advance at the same rate on all servers in the cluster. What is essential, though, is that time-based callbacks be executed at the same point in the Raft log on all nodes. In order to accomplish this, the leader writes an approximate `Instant` to the replicated log for each command. When a command is applied to the state machine, the command's timestamp is used to invoke any outstanding scheduled callbacks. This means the granularity of scheduled callbacks is limited by the minimum time between commands submitted to the cluster, including session register and keep-alive requests. Thus, users should not rely on `StateMachineExecutor` scheduling for accuracy.

{% include common-links.html %}