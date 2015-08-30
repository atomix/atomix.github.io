---
layout: content
menu: user-manual
title: Distributed resources
---

## Distributed resources

Copycat provides a number of resource implementations for common distributed systems problems. Currently, the provided resources are divided into three subsets that are represented as Maven submodules:

* [Distributed collections](#distributed-collections) - `DistributedSet`, `DistributedMap`, etc
* [Distributed atomic variables](#distributed-atomic-variables) - `DistributedAtomicValue`, etc
* [Distributed coordination tools](#distributed-coordination) - `DistributedLock`, `DistributedLeaderElection`, etc

### Distributed collections

The `copycat-collections` module provides a set of asynchronous, distributed collection-like [resources](#resources). The resources provided by the collections module do not implement JDK collection interfaces because Copycat's APIs are asynchronous, but their methods are equivalent to their blocking counterparts and so collection resources can be easily wrapped in blocking collection interfaces.

If your project does not depend on `copycat-all`, you must add the `copycat-collections` dependency in order to access the collection classes:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-collections</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

#### DistributedSet

The [DistributedSet][DistributedSet] resources provides an asynchronous API similar to that of `java.util.Set`.

To create a `DistributedSet`, pass the class to `Copycat.create(String, Class)`:

```java
copycat.<DistributedSet<String>>create("/test-set", DistributedSet.class).thenAccept(set -> {
  // Do something with the set
});
```

Once the set has been created, the methods closely mimic those of `java.util.Set`. `DistributedSet` returns `CompletableFuture` for all methods:

```java
set.add("Hello world!").thenRun(() -> {
  set.contains("Hello world!").thenAccept(result -> {
    assert result;
  });
});
```

To block and wait for results instead, call `join()` or `get()` on the returned `CompletableFuture`s:

```java
set.add("Hello world!").join();
assert set.contains("Hello world!").get();
```

##### Expiring values

`DistributedSet` supports configurable TTLs for set values. To set a TTL on a value, simply pass a `Duration` when adding a value to the set:

```java
set.add("Hello world!", Duration.ofSeconds(1)).thenAccept(succeeded -> {
  // If the add failed, the TTL will not have been set
  if (succeeded) {
    System.out.println("Value added with TTL");
  } else {
    System.out.println("Value add failed");
  }
});
```

Note that TTL timers are deterministically controlled by the cluster leader and are approximate representations of wall clock time that *should not be relied upon for accuracy*.

##### Ephemeral values

In addition to supporting time-based state changes, `DistributedSet` also supports session-based changes via a configurable [PersistenceMode](#persistence-mode). When a value is added to the set with `PersistenceMode.EPHEMERAL`, the value will disappear once the session that created the value is expired or closed.

```java
// Add a value with EPHEMERAL persistence
set.add("Hello world!", PersistenceMode.EPHEMERAL).thenRun(() -> {
  // Close the Copycat instance to force the value to be removed from the set
  copycat.close();
});
```

#### DistributedMap

The [DistributedMap][DistributedMap] resources provides an asynchronous API similar to that of `java.util.Map`.

To create a `DistributedMap`, pass the class to `Copycat.create(String, Class)`:

```java
copycat.<DistributedMap<String, String>>create("/test-map", DistributedMap.class).thenAccept(map -> {
  // Do something with the map
});
```

Once the map has been created, the methods closely mimic those of `java.util.Map`. `DistributedMap` returns `CompletableFuture` for all methods:

```java
map.put("foo", "Hello world!").thenRun(() -> {
  map.get("foo").thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```

To block and wait for results instead, call `join()` or `get()` on the returned `CompletableFuture`s:

```java
map.put("foo", "Hello world!").join();
assert map.get("foo").get().equals("Hello world!");
```

##### Expiring keys

`DistributedMap` supports configurable TTLs for map keys. To set a TTL on a key, simply pass a `Duration` when adding a key to the map:

```java
map.put("foo", "Hello world!", Duration.ofSeconds(1)).thenRun(() -> {
  System.out.println("Key added with TTL");
});
```

Note that TTL timers are deterministically controlled by the cluster leader and are approximate representations of wall clock time that *should not be relied upon for accuracy*.

##### Ephemeral keys

In addition to supporting time-based state changes, `DistributedMap` also supports session-based changes via a configurable [PersistenceMode](#persistence-mode). When a key is added to the map with `PersistenceMode.EPHEMERAL`, the key will disappear once the session that created the key is expired or closed.

```java
// Add a key with EPHEMERAL persistence
map.put("foo", "Hello world!", PersistenceLevel.EPHEMERAL).thenRun(() -> {
  // Close the Copycat instance to force the key to be remove from the map
  copycat.close();
});
```

### Distributed atomic variables

The `copycat-atomic` module provides a set of distributed atomic variables modeled on Java's `java.util.concurrent.atomic` package. The resources provided by the atomic module do not implement JDK atomic interfaces because Copycat's APIs are asynchronous, but their methods are equivalent to their blocking counterparts and so atomic resources can be easily wrapped in blocking interfaces.

If your project does not depend on `copycat-all`, you must add the `copycat-atomic` dependency in order to access the atomic classes:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-atomic</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

#### DistributedAtomicValue

The [DistributedAtomicValue][DistributedAtomicValue] resource provides an asynchronous API similar to that of `java.util.concurrent.atomic.AtomicReference`.

To create a `DistributedAtomicValue`, pass the class to `Copycat.create(String, Class)`:

```java
copycat.<DistributedAtomicValue<String>>create("/test-value", DistributedAtomicValue.class).thenAccept(value -> {
  // Do something with the value
});
```

Once the value has been created, the methods closely mimic those of `java.util.concurrent.atomic.AtomicReference`. `DistributedAtomicValue` returns `CompletableFuture` for all methods:

```java
value.set("Hello world!").thenRun(() -> {
  value.get().thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```

To block and wait for results instead, call `join()` or `get()` on the returned `CompletableFuture`s:

```java
value.set("Hello world!").join();
assert value.get().get().equals("Hello world!");
```

##### Expiring value

`DistributedAtomicValue` supports configurable TTLs for values. To set a TTL on the value, simply pass a `Duration` when setting the value:

```java
value.set("Hello world!", Duration.ofSeconds(1)).thenRun(() -> {
  System.out.println("Value set with TTL of 1 second");
});
```

Note that TTL timers are deterministically controlled by the cluster leader and are approximate representations of wall clock time that *should not be relied upon for accuracy*.

##### Ephemeral value

In addition to supporting time-based state changes, `DistributedAtomicValue` also supports session-based changes via a configurable [PersistenceMode](#persistence-mode). When the value is set with `PersistenceMode.EPHEMERAL`, the value will disappear once the session that created the value is expired or closed.

```java
// Set the value with EPHEMERAL persistence
value.set("Hello world!", PersistenceMode.EPHEMERAL).thenRun(() -> {
  // Close the Copycat instance to force the value to be unset
  copycat.close();
});
```

### Distributed coordination

The `copycat-coordination` module provides a set of distributed coordination tools. These tools are designed tofacilitate decision making and communication in a distributed system.

If your project does not depend on `copycat-all`, you must add the `copycat-coordination` dependency in order to access the coordination classes:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-coordination</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

#### DistributedLock

The [DistributedLock][DistributedLock] resources provides an asynchronous API similar to that of `java.util.concurrent.locks.Lock`.

To create a `DistributedLock`, pass the class to `Copycat.create(String, Class)`:

```java
copycat.create("/test-lock", DistributedLock.class).thenAccept(lock -> {
  // Do something with the lock
});
```

Once the lock has been created, the methods closely mimic those of `java.util.concurrent.locks.Lock`. `DistributedLock` returns `CompletableFuture` for all methods:

```java
lock.lock().thenRun(() -> {
  // Do some stuff and then...
  lock.unlock();
});
```

To block and wait for the lock to be acquired instead, call `join()` or `get()` on the returned `CompletableFuture`s:

```java
lock.lock().join();

// Do some stuff

lock.unlock().join();
```

#### DistributedLeaderElection

The [DistributedLeaderElection][DistributedLeaderElection] resource provides an asynchronous API for coordinating tasks among a set of clients.

[Leader election](https://en.wikipedia.org/wiki/Leader_election) is a pattern commonly used in distributed systems to coordinate some task or access to a resource among a set of processes. Copycat's `DistributedLeaderElection` handles the coordination of a leader and notifies processes when they become the leader.

To create a `DistributedLeaderElection`, pass the class to `Copycat.create(String, Class)`:

```java
copycat.create("/test-election", DistributedLeaderElection.class).thenAccept(election -> {
  // Do something with the election
});
```

Once the election has been created, register a listener callback to be called when the calling node is elected the leader:

```java
election.onElection(epoch -> {
  System.out.println("Elected leader!");
});
```

The registration of a listener via `onElection` is asynchronous. The resource will not become electable until the `CompletableFuture` returned has been completed:

```java
election.onElection(epoch -> {
  System.out.println("Elected leader!");
}).thenRun(() -> {
  System.out.println("Awaiting election!");
});
```

When a session creates a new `DistributedLeaderElection` at the `/test-election` path, the session will be queued to be elected. When a client/session disconnects from the Copycat cluster or times out, the next session awaiting the leadership role will take over the leadership and the registered `onElection` listener will be called.

The argument provided to the election listener is commonly known as an *epoch* (or in some cases a `term` as in [Raft][Raft]). The epoch is a monotonically increasing, unique `long` that is representative of a single election.

It is important to note that while from the Copycat cluster's perspective, only one client will hold the leadership at any given point in time, the same may not be true for clients. It's possible that a client can believe itself to be the leader even though its session has timed out and a new leader has been elected. Users can guard against this scenario by verifying leadership with the `isLeader(long)` method prior to critical operations in order to ensure consistency:

```java
election.onElection(epoch -> {
  // Verify that this node is still the leader
  election.isLeader(epoch).thenAccept(leader -> {
    if (leader) {
      System.out.println("Still the leader");
      // Do something important
    } else {
      System.out.println("Lost leadership!");
    }
  });
});
```

In the event that a `DistributedLeaderElection` wins an election and loses its leadership without the node crashes, it's likely that the client's session expired due to a failure to communicate with the cluster.

#### DistributedTopic

The [DistributedTopic][DistributedTopic] resource provides an asynchronous API for sending publish-subscribe messages between clients. Messages sent via a `DistributedTopic` are linearized through the client's [Session][Session]. This means messages are guaranteed to be delivered exactly once and in the order in which they were sent to all sessions that are active at the time the message is sent.

To create a `DistributedTopic`, pass the class to `Copycat.create(String, Class)`:

```java
copycat.<DistributedTopic<String>>create("/test-topic", DistributedTopic.class).thenAccept(topic -> {
  // Send and receive some messages with the topic
});
```

Once the topic has been created, users can send and receive messages. To send messages to the topic, use the `publish(T)` method:

```java
topic.publish("Hello world!");
```

To receive messages sent to the topic, register a topic listener using the `onMessage` method:

```java
topic.onMessage(message -> {
  assert message.equals("Hello world!");
});
```

When a message is sent to a topic, the message will be logged and replicated like any state change via Copycat's underlying [Raft](#raft-consensus-algorithm) implementation. Once the message is stored on a majority of servers, the message will be delivered to any client [sessions](#sessions) alive at the time the message was sent.

### Custom resources

The Copycat API is designed to facilitate operating on arbitrary user-defined resources. When a custom resource is created via `Copycat.create`, an associated state machine will be created on each Copycat replica, and operations submitted by the resource instance will be applied to the replicated state machine. In that sense, think of a `Resource` instance as a client-side object and a `StateMachine` instance as the server-side representation of that object.

To define a new resource, simply extend the base `Resource` class:

```java
public class Value extends Resource {
  @Override
  protected Class<? extends StateMachine> stateMachine() {
    return ValueStateMachine.class;
  }
}
```

The `Resource` implementation must return a `StateMachine` class that will be configured to manage the resource's state.

```java
copycat.create(Value.class).thenAccept(value -> {
  System.out.println("Value resource created!");
});
```

When a resource is created via `Copycat.create(String, Class)`, the `StateMachine` class returned by the `Resource.stateMachine()` method will be constructed on each replica in the cluster. Once the state machine has been created on a majority of the replicas, the resource will be constructed and the returned `CompletableFuture` completed.

Resource state changes are submitted to the Copycat cluster as [Command][Command] or [Query][Query] implementations. See the documentation on Raft [commands](#commands) and [queries](#queries) for specific information regarding the use cases and limitations of each type.

To submit an operation to the Copycat cluster on behalf of the resource, expose a method that forwards a `Command` or `Query` to the cluster:

```java
public class Value<T> extends Resource {
  @Override
  protected Class<? extends StateMachine> stateMachine() {
    return ValueStateMachine.class;
  }

  /**
   * Returns the value.
   */
  public CompletableFuture<T> get() {
    return submit(new Get<>());
  }

  /**
   * Sets the value.
   */
  public CompletableFuture<Void> set(T value) {
    return submit(new Set<>(value));
  }

  /**
   * Get query.
   */
  private static class Get<T> implements Query<T> {
  }

  /**
   * Set command.
   */
  private static class Set<T> implements Command<T> {
    private Object value;

    private Set() {
    }

    private Set(Object value) {
      this.value = value;
    }
  }

  /**
   * Value state machine.
   */
  private static class ValueStateMachine extends StateMachine {
    private Object value;

    @Override
    protected void configure(StateMachineExecutor executor) {
      executor.register(Get.class, this::get);
    }

    /**
     * Gets the value.
     */
    private Object get(Commit<Get> commit) {
      return value;
    }

    /**
     * Sets the value.
     */
    private void set(Commit<Set> commit) {
      this.value = commit.operation().value;
    }
  }
}
```

*Important: See [Raft state machine documentation](#state-machines) for details on cleaning commits from the log*

[Javadoc]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/
[CAP]: https://en.wikipedia.org/wiki/CAP_theorem
[Raft]: https://raft.github.io/
[Executor]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/Executor.html
[CompletableFuture]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html
[collections]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections.html
[atomic]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/atomic.html
[coordination]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination.html
[copycat]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat.html
[protocol]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol.html
[io]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io.html
[serializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer.html
[transport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport.html
[storage]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage.html
[utilities]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util.html
[Copycat]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/Copycat.html
[CopycatReplica]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/CopycatReplica.html
[CopycatClient]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/CopycatClient.html
[Resource]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/Resource.html
[Transport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/Transport.html
[LocalTransport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/LocalTransport.html
[NettyTransport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/NettyTransport.html
[Storage]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage/Storage.html
[Log]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage/Log.html
[Buffer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/Buffer.html
[BufferReader]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/BufferReader.html
[BufferWriter]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/BufferWriter.html
[Serializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/Serializer.html
[CopycatSerializable]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/CopycatSerializable.html
[TypeSerializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/TypeSerializer.html
[SerializableTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[PrimitiveTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[JdkTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[ServiceLoaderTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/ServiceLoaderTypeResolver.html
[RaftServer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/RaftServer.html
[RaftClient]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/RaftClient.html
[Session]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/session/Session.html
[Operation]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Operation.html
[Command]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Command.html
[Query]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Query.html
[Commit]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Commit.html
[ConsistencyLevel]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/ConsistencyLevel.html
[DistributedAtomicValue]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/atomic/DistributedAtomicValue.html
[DistributedSet]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections/DistributedSet.html
[DistributedMap]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections/DistributedMap.html
[DistributedLock]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedLock.html
[DistributedLeaderElection]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedLeaderElection.html
[DistributedTopic]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedTopic.html
[Builder]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/Builder.html
[Listener]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/Listener.html
[Context]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/concurrent/Context.html