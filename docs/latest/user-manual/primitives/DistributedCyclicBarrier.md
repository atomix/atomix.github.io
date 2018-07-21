---
layout: user-manual
project: atomix
menu: user-manual
title: DistributedCyclicBarrier
---

The [`DistributedCyclicBarrier`][DistributedCyclicBarrier] primitive is a distributed implementation of Java's [`CyclicBarrier`][CyclicBarrier].

## Configuration

The [`DistributedCyclicBarrier`][DistributedCyclicBarrier] can be configured programmatically using the [`DistributedCyclicBarrierBuilder`][DistributedCyclicBarrierBuilder]. To create a new cyclic barrier builder, use the `cyclicBarrierBuilder` method, passing the name of the barrier to construct:

```java
DistributedCyclicBarrierBuilder cyclicBarrierBuilder = atomix.cyclicBarrierBuilder("my-barrier");
```

The barrier can be configured with a [protocol][primitive-protocols] to use to replicate changes. Since `DistributedCyclicBarrier` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Additionally, when using partitioned protocols, the barrier will be replicated only within a single partition for consistency.

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

DistributedCyclicBarrier barrier = atomix.cyclicBarrierBuilder("my-barrier")
  .withProtocol(protocol)
  .build();
```

{:.callout .callout-warning}
It's important that distributed barriers can tolerate network partitions without split brain, so it is strongly recommended that users configure at least one [Raft partition group][partition-groups] to use for barriers.

Distributed barriers can also be configured in configuration files. To configure a distributed barrier primitive, use the `cyclic-barrier` primitive type:

`atomix.conf`

```hocon
primitives.my-barrier {
  type: cyclic-barrier
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured barrier, use the `getCyclicBarrier` method:

```java
DistributedCyclicBarrier barrier = atomix.getCyclicBarrier("my-barrier");
```

The barrier's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`DistributedCyclicBarrier`][DistributedCyclicBarrier] supports most of the same operations as Java's core [`CyclicBarrier`][CyclicBarrier]. The specific consistency guarantees of read and write operations are dependent on the configured protocol.

As with all Atomix primitives, an asynchronous analogue of the barrier API - [`AsyncDistributedCyclicBarrier`][AsyncDistributedCyclicBarrier] - can be retrieved by calling the `async()` method:

```java
AsyncDistributedCyclicBarrier asyncBarrier = atomic.getCyclicBarrier("my-barrier").async();

asyncBarrier.await().thenRun(() -> {
  ...
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

## Cleanup

While a barrier is in use, Atomix may consume some network, memory, and disk resources to manage the barrier. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
barrier.close();
```

{% include common-links.html %}
