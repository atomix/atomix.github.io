---
layout: user-manual
project: atomix
menu: user-manual
title: AtomicCounter
---

The [`AtomicCounter`][AtomicCounter] primitive is a distributed implementation of Java's [`AtomicLong`][AtomicLong].

## Configuration

The [`AtomicCounter`][AtomicCounter] can be configured programmatically using the [`AtomicCounterBuilder`][AtomicCounterBuilder]. To create a new counter builder, use the `atomicCounterBuilder` method, passing the name of the counter to construct:

```java
AtomicCounterBuilder counterBuilder = atomix.atomicCounterBuilder("my-counter");
```

The counter can be configured with a `PrimitiveProtocol` to use to replicate changes. Since `AtomicCounter` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Additionally, when using partitioned protocols, the counter will be replicated only within a single partition for consistency.

```java
AtomicCounter counter = atomix.atomicCounterBuilder("my-counter")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();
```

Atomic counters can also be configured in configuration files. To configure an atomic counter primitive, use the `atomic-counter` primitive type:

`atomix.conf`

```hocon
primitives.my-counter {
  type: atomic-counter
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured counter, use the `getAtomicCounter` method:

```java
AtomicCounter counter = atomix.getAtomicCounter("my-counter");
```

The counter's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`AtomicCounter`][AtomicCounter] supports most of the same operations as Java's core `AtomicLong`. All operations performed on the atomic counter are, as suggested, guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
AtomicCounter counter = atomix.atomicCounterBuilder("my-counter")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

long value = counter.incrementAndGet();
if (counter.compareAndSet(value, 1)) {
  ...
}
```

As with all Atomix primitives, an asynchronous analogue of the counter API - [`AsyncAtomicCounter`][AsyncAtomicCounter] - can be retrieved by calling the `async()` method:

```java
AsyncAtomicCounter asyncCounter = counter.async();

asyncCounter.incrementAndGet().thenAccept(value -> {
  asyncCounter.compareAndSet(value, 1).thenAccept(() -> {
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
