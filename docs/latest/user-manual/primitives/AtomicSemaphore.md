---
layout: user-manual
project: atomix
menu: user-manual
title: AtomicSemaphore
---

The [`AtomicSemaphore`][AtomicSemaphore] primitive is a distributed implementation of Java's [`Semaphore`][Semaphore]. The primary difference between `AtomicSemaphore` and [`DistributedSemaphore`][DistributedSemaphore] is that while `DistributedSemaphore` is an implementation of Java's [`Semaphore`][Semaphore] API, the `AtomicSemaphore` API provides monotonically increasing, globally unique semaphore instance identifiers that can be used to determine ordering of multiple concurrent semaphore permits.

*That's right!* Even though Atomix semaphores can be replicated using a proven consensus algorithm like Raft, linearizability only tells us that a semaphore was acquired some time between a request and response, not necessarily that it still holds the permit. There's still no way to guarantee that two nodes do not _believe_ themselves to hold the same permit at the same time. And one way to determine which of two permit acquirers is more recent is to use the type of fencing token provided by `AtomicSemaphore`.

`AtomicSemaphore`s are designed to account for failures within the cluster. When a semaphore instance crashes or becomes disconnected from the partition by which the semaphore's state is controlled, the permit will be released and granted to the next waiting process.

The current implementation of `AtomicSemaphore` is fair and will grant the semaphore to processes in the order in which their acquire requests arrive.

## Configuration

The [`AtomicSemaphore`][AtomicSemaphore] can be configured programmatically using the [`AtomicSemaphoreBuilder`][AtomicSemaphoreBuilder]. To create a new semaphore builder, use the `atomicSemaphoreBuilder` method, passing the name of the semaphore to construct:

```java
AtomicSemaphoreBuilder semaphoreBuilder = atomix.atomicSemaphoreBuilder("my-semaphore");
```

The semaphore can be configured with a [protocol][primitive-protocols] to use to replicate changes. Since `AtomicSemaphore` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Additionally, when using partitioned protocols, the semaphore will be replicated only within a single partition for consistency.

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

AtomicSemaphore semaphore = atomix.atomicSemaphoreBuilder("my-semaphore")
  .withProtocol(protocol)
  .build();
```

{:.callout .callout-warning}
It's important that distributed semaphores can tolerate network partitions without split brain, so it is strongly recommended that users configure at least one [Raft partition group][partition-groups] to use for semaphores.

Atomic semaphores can also be configured in configuration files. To configure an atomic semaphore primitive, use the `atomic-semaphore` primitive type:

`atomix.conf`

```hocon
primitives.my-semaphore {
  type: atomic-semaphore
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured semaphore, use the `getAtomicSemaphore` method:

```java
AtomicSemaphore semaphore = atomix.getAtomicSemaphore("my-semaphore");
```

The semaphore's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`AtomicSemaphore`][AtomicSemaphore] supports most of the same operations as Java's core [`Semaphore`][Semaphore]. The specific consistency guarantees of read and write operations are dependent on the configured protocol.

```java
AtomicSemaphore semaphore = atomix.atomicSemaphoreBuilder("my-semaphore")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

Version version = semaphore.acqiure();
try {
  ...
} finally {
  semaphore.release();
}
```

A fencing token - the permit ID - is returned by the `acquire()` method once the permit has been acquired:

```java
Version permitId = semaphore.acquire();
```

This value is guaranteed to be a monotinically increasing, globally unique identifier. These semantics ensure that permit acquisitions can be ordered across nodes. For example, if node A acquires a permit with version 10, and node B acquires a permit on the same semaphore with version 11, and both nodes try to operate on node C at the same time, node C will know that the permit with version 11 is more recent than the permit with version 10, and considering the atomicity guarantees of the semaphore, that must necessarily indicate the node A no longer holds the permit and can thus be ignored.

The semaphore also supports timed methods:

```java
Optional<Version> result = semaphore.tryAcquire(Duration.ofSeconds(10));
```

When using `tryAcquire` methods, an `Optional` will be returned. If the attempt is successful, the `Optional` will be completed with the permit ID. If it fails, the `Optional` value will not be present.

```java
if (result.isPresent()) {
  // Acquire succeeded!
} else {
  // Acquire failed :-(
}
```

{:.callout .callout-info}
Because of the nature of distributed systems, it's possible for a client to temporarily acquire a permit after a `tryAcquire` attempt times out. However, the `AtomicSemaphore` implementation will immediately release the permit once it's acquired.

As with all Atomix primitives, an asynchronous analogue of the semaphore API - [`AsyncAtomicSemaphore`][AsyncAtomicSemaphore] - can be retrieved by calling the `async()` method:

```java
AsyncAtomicSemaphore asyncSemaphore = semaphore.async();

asyncSemaphore.acquire().thenAccept(permitId -> {
  ...
  asyncSemaphore.release().thenRun(() -> {
    ...
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

### Monitoring the Semaphore State

Because the semaphore service will release permits when a permit holder becomes disconnected from the partition, scenarios exist where a client can believe itself to hold a permit after the permit has already been granted to another process. As mentioned, the most effective way to guard against multiple concurrent permit holders is by using the permit ID provided by the `acquire()` and `tryAcquire()` methods, but that's not always conducive to the architecture of a system. Instead, semaphore clients can monitor the semaphore for disconnections to detect when the semaphore session may be expired.

```java
semaphore.addStateChangeListener(state -> {
  if (state == PrimitiveState.SUSPENDED) {
    
  }
});
```

State change listeners are called with a [`PrimitiveState`][PrimitiveState] enum. The enum defines three values:
* `CONNECTED` - Indicates that the instance is connected to the underlying partition and is able to send keep-alive requests
* `SUSPENDED` - Indicates that the instance has not been able to send kee-alive requests for long enough for its session to have been expired by the partition, possibly resulting in permit(s) being granted to another process 
* `CLOSED` - Indicates that the underlying partition client has been closed and the permit(s) will be granted to another process

The safest policy is to assume once a `SUSPENDED` or `CLOSED` event is received, the permits have been lost.

## Cleanup

While a semaphore is in use, Atomix may consume some network, memory, and disk resources to manage the semaphore. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
semaphore.close();
```

{% include common-links.html %}
