---
layout: user-manual
project: atomix
menu: user-manual
title: DistributedLock
---

The [`DistributedLock`][DistributedLock] primitive is a distributed implementation of Java's [`Lock`][Lock]. The primary difference between `DistributedLock` and [`AtomicLock`][AtomicLock] is that while `DistributedLock` is an implementation of Java's [`Lock`][Lock] interface, the `AtomicLock` API provides monotonically increasing, globally unique lock instance identifiers that can be used to determine ordering of multiple concurrent lock holders.

`DistributedLock`s are designed to account for failures within the cluster. When a lock holder crashes or becomes disconnected from the partition by which the lock's state is controlled, the lock will be released and granted to the next waiting process.

The current implementation of `DistributedLock` is fair and will grant the lock to processes in the order in which their lock requests arrive.

## Configuration

The [`DistributedLock`][DistributedLock] can be configured programmatically using the [`DistributedLockBuilder`][DistributedLockBuilder]. To create a new lock builder, use the `lockBuilder` method, passing the name of the lock to construct:

```java
DistributedLockBuilder lockBuilder = atomix.lockBuilder("my-lock");
```

The lock can be configured with a [protocol][primitive-protocols] to use to replicate changes. Since `DistributedLock` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Additionally, when using partitioned protocols, the lock will be replicated only within a single partition for consistency.

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

DistributedLock lock = atomix.lockBuilder("my-lock")
  .withProtocol(protocol)
  .build();
```

{:.callout .callout-warning}
It's important that distributed locks can tolerate network partitions without split brain, so it is strongly recommended that users configure at least one [Raft partition group][partition-groups] to use for distributed locking.

Distributed locks can also be configured in configuration files. To configure a distributed lock primitive, use the `lock` primitive type:

`atomix.conf`

```hocon
primitives.my-lock {
  type: lock
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured lock, use the `getLock` method:

```java
DistributedLock lock = atomix.getLock("my-lock");
```

The lock's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`DistributedLock`][DistributedLock] supports most of the same operations as Java's core [`Lock`][Lock]. The specific consistency guarantees of read and write operations are dependent on the configured protocol.

```java
Lock lock = atomix.lockBuilder("my-lock")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();


lock.lock();
try {
  ...
} finally {
  lock.unlock();
}
```

The lock also supports timed methods:

```java
if (lock.tryLock(10, TimeUnit.SECONDS)) {
  ...
}
```

{:.callout .callout-info}
Because of the nature of distributed systems, it's possible for a client to temporarily acquire a lock after a `tryLock` attempt times out. However, the `DistributedLock` implementation will immediately release the lock once it's acquired.

As with all Atomix primitives, an asynchronous analogue of the lock API - [`AsyncDistributedLock`][AsyncDistributedLock] - can be retrieved by calling the `async()` method:

```java
AsyncDistributedLock asyncLock = atomic.getLock("my-lock").async();

asyncLock.lock().thenAccept(lockId -> {
  ...
  lock.unlock().thenRun(() -> {
    
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

### Monitoring the Lock State

Because the lock service will release locks when a lock holder becomes disconnected from the locked partition, scenarios exist where a client can believe itself to hold a lock after the lock has already been granted to another process. As mentioned, the most effective way to guard against multiple concurrent lock holders is by using the lock ID provided by the `lock()` and `tryLock()` methods, but that's not always conducive to the architecture of a system. Instead, lock clients can monitor the lock for disconnections to detect when the lock session may be expired.

```java
DistributedLock lock = atomix.getLock("my-lock");
lock.addStateChangeListener(state -> {
  if (state == PrimitiveState.SUSPENDED) {
    
  }
});
```

State change listeners are called with a [`PrimitiveState`][PrimitiveState] enum. The enum defines three values:
* `CONNECTED` - Indicates that the instance is connected to the underlying partition and is able to send keep-alive requests
* `SUSPENDED` - Indicates that the instance has not been able to send kee-alive requests for long enough for its session to have been expired by the partition, possibly resulting in the lock being granted to another process 
* `CLOSED` - Indicates that the underlying partition client has been closed and the lock will be granted to another process

The safest policy is to assume once a `SUSPENDED` or `CLOSED` event is received, the lock has been lost.

## Cleanup

While a lock is in use, Atomix may consume some network, memory, and disk resources to manage the lock. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
lock.close();
```

{% include common-links.html %}
