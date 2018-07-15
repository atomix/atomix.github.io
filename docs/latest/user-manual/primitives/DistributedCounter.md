---
layout: user-manual
project: atomix
menu: user-manual
title: DistributedCounter
---

The [`DistributedCounter`][DistributedCounter] primitive is a distributed counter with an API similar to that of Java's [`AtomicLong`][AtomicLong]. However, `DistributedCounter` differs from [`AtomicCounter`][AtomicCounter] in that it does not provide strong consistency guarantees and therefore supports eventually consistent protocols, in particular gossip via CRDT counters.

## Configuration

The [`DistributedCounter`][DistributedCounter] can be configured programmatically using the [`DistributedCounterBuilder`][DistributedCounterBuilder]. To create a new counter builder, use the `counterBuilder` method, passing the name of the counter to construct:

```java
DistributedCounterBuilder counterBuilder = atomix.counterBuilder("my-counter");
```

The counter can be configured with a `PrimitiveProtocol` to use to replicate changes. `DistributedCounter` is not considered a consistent primitive and thus supports both strongly consistent and eventually consistent protocols:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]
* [`CrdtProtocol`][CrdtProtocol]

Additionally, when using partitioned protocols, the counter will be replicated only within a single partition for consistency.

```java
DistributedCounter counter = atomix.counterBuilder("my-counter")
  .withProtocol(CrdtCounter.instance())
  .build();
```

Distributed counters can also be configured in configuration files. To configure a distributed counter primitive, use the `counter` primitive type:

`atomix.conf`

```hocon
primitives.my-counter {
  type: counter
  protocol {
    type: crdt
  }
}
```

To get an instance of the pre-configured counter, use the `getCounter` method:

```java
DistributedCounter counter = atomix.getCounter("my-counter");
```

The counter's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`DistributedCounter`][DistributedCounter] supports most of the same operations as Java's core `AtomicLong`. The consistency guarantees of operations on the counter are entirely dependent upon the configured protocol. The `DistributedCounter` interface provides no guarantees.

```java
DistributedCounter counter = atomix.counterBuilder("my-counter")
  .withProtocol(CrdtCounter.instance())
  .build();

long oldValue = counter.incrementAndGet();
long newValue = counter.addAndGet(10);
```

As with all Atomix primitives, an asynchronous analogue of the counter API - [`AsyncDistributedCounter`][AsyncDistributedCounter] - can be retrieved by calling the `async()` method:

```java
AsyncDistributedCounter asyncCounter = counter.async();

asyncCounter.incrementAndGet().thenAccept(oldValue -> {
  asyncCounter.addAndGet(10).thenAccept(newValue -> {
    ...
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

## Cleanup

While a counter is in use, Atomix may consume some network, memory, and disk resources to manage the counter. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
counter.close();
```

{% include common-links.html %}
