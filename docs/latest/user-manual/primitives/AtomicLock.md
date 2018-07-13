---
layout: user-manual
project: atomix
menu: user-manual
title: AtomicLock
---

The [`AtomicLock`][AtomicLock] primitive is a distributed implementation of Java's [`Lock`][Lock]. The primary difference between `AtomicLock` and [`DistributedLock`][DistributedLock] is that while `DistributedLock` is an implementation of Java's [`Lock`][Lock] interface, the `AtomicLock` API provides monotonically increasing, globally unique lock instance identifiers that can be used to determine ordering of multiple concurrent lock holders.

*That's right!* Even though Atomix locks can be replicated using a proven consensus algorithm like Raft, linearizability only tells us that a lock holder was granted the lock some time between a request and response, not necessarily that it still holds the lock. There's still no way to guarantee that two nodes do not _believe_ themselves to hold the same lock at the same time. And one way to determine which of two lock holders is more recent is to use the type of fencing token provided by `AtomicLock`.

`AtomicLock`s are designed to account for failures within the cluster. When a lock holder crashes or becomes disconnected from the partition by which the lock's state is controlled, the lock will be released and granted to the next waiting process.

The current implementation of `AtomicLock` is fair and will grant the lock to processes in the order in which their lock requests arrive.

## Configuration

The [`AtomicLock`][AtomicLock] can be configured programmatically using the [`AtomicLockBuilder`][AtomicLockBuilder]. To create a new lock builder, use the `atomicLockBuilder` method, passing the name of the lock to construct:

```java
AtomicLockBuilder lockBuilder = atomix.atomicLockBuilder("my-lock");
```

The lock can be configured with a [protocol][primitive-protocols] to use to replicate changes. Since `AtomicLock` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Additionally, when using partitioned protocols, the lock will be replicated only within a single partition for consistency.

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

AtomicLock lock = atomix.atomicLockBuilder("my-lock")
  .withProtocol(protocol)
  .build();
```

Atomic locks can also be configured in configuration files. To configure an atomic lock primitive, use the `atomic-lock` primitive type:

`atomix.conf`

```hocon
primitives.my-lock {
  type: atomic-lock
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured lock, use the `getAtomicLock` method:

```java
AtomicLock lock = atomix.getAtomicLock("my-lock");
```

The lock's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`AtomicLock`][AtomicLock] supports most of the same operations as Java's core [`Lock`][Lock]. The specific consistency guarantees of read and write operations are dependent on the configured protocol.

```java
AtomicLock lock = atomix.atomicLockBuilder("my-lock")
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

A fencing token - the lock ID - is returned by the `lock()` method once the lock has been acquired:

```java
long lockId = lock.lock();
```

This value is guaranteed to be a monotinically increasing, globally unique identifier. These semantics ensure that lock acquisitions can be ordered across nodes. For example, if node A acquires a lock with version 10, and node B acquires the same lock with version 11, and both nodes try to operate on node C at the same time, node C will know that the lock with version 11 is more recent than the lock with version 10, and considering the atomicity guarantees of the lock, that must necessarily indicate the node A no longer holds the lock and can thus be ignored.

The lock also supports timed methods:

```java
Optional<Long> result = lock.tryLock(Duration.ofSeconds(10));
```

When using `tryLock` methods, an `Optional` will be returned. If the attempt is successful, the `Optional` will be completed with the lock ID. If it fails, the `Optional` value will not be present.

```java
if (result.isPresent()) {
  // Lock succeeded!
} else {
  // Lock failed :-(
}
```

{:.callout .callout-info}
Because of the nature of distributed systems, it's possible for a client to temporarily acquire a lock after a `tryLock` attempt times out. However, the `AtomicLock` implementation will immediately release the lock once it's acquired.

As with all Atomix primitives, an asynchronous analogue of the lock API - [`AsyncAtomicLock`][AsyncAtomicLock] - can be retrieved by calling the `async()` method:

```java
AsyncAtomicLock asyncLock = lock.async();

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
