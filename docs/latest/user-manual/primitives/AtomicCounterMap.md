---
layout: user-manual
project: atomix
menu: user-manual
title: AtomicCounterMap
---

The [`AtomicCounterMap`][AtomicCounterMap] primitive is a distributed implementation of Guava's `AtomicLongMap`.

## Configuration

The [`AtomicCounterMap`][AtomicCounterMap] can be configured programmatically using the [`AtomicCounterMapBuilder`][AtomicCounterMapBuilder]. To create a new counter map builder, use the `atomicCounterMapBuilder` method, passing the name of the counter map to construct:

```java
AtomicCounterMapBuilder<String> counterMapBuilder = atomix.<String>atomicCounterMapBuilder("my-counter-map");
```

The counter can be configured with a `PrimitiveProtocol` to use to replicate changes. Since `AtomicCounterMap` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

When using partitioned protocols like the ones above, the counter map will be partitioned and replicated among all partitions in the configured [partition group][partition-groups].

```java
AtomicCounterMap<String> counterMap = atomix.<String>atomicCounterMapBuilder("my-counter-map")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();
```

The generic parameter in the counter map configuration is the map key type. To support non-standard key types, the protocol must be configured with a custom serializer:

```java
Serializer serializer = Serializer.using(Namespace.builder()
  .register(Namespaces.BASIC)
  .register(MemberId.class)
  .build());

AtomicCounterMapBuilder<MemberId> counterMap = atomix.<String>atomicCounterMapBuilder("my-counter-map")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .withSerializer(serializer)
    .build())
  .build();
```

Atomic counter maps can also be configured in configuration files. To configure an atomic counter map primitive, use the `atomic-counter-map` primitive type:

`atomix.conf`

```hocon
primitives.my-counter-map {
  type: atomic-counter-map
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured counter map, use the `getAtomicCounterMap` method:

```java
AtomicCounterMap<String> counterMap = atomix.getAtomicCounterMap("my-counter-map");
```

The counter's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`AtomicCounterMap`][AtomicCounterMap] supports most of the same operations as Guava's `AtomicLongMap`. Operations resembled keyed [`AtomicLong`][AtomicLong] operations. All operations performed on the atomic counter map are, as suggested, guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
AtomicCounterMap<String> counterMap = atomix.<String>atomicCounterMapBuilder("my-counter-map")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

long value = counterMap.incrementAndGet("foo");
if (counter.compareAndSet("foo", value, 1)) {
  ...
}
```

As with all Atomix primitives, an asynchronous analogue of the counter map API - [`AsyncAtomicCounterMap`][AsyncAtomicCounterMap] - can be retrieved by calling the `async()` method:

```java
AsyncAtomicCounterMap<String> asyncCounterMap = counterMap.async();

asyncCounterMap.incrementAndGet("foo").thenAccept(value -> {
  asyncCounterMap.compareAndSet("foo", value, 1).thenAccept(() -> {
    ...
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

## Cleanup

While a counter is in use, Atomix may consume some network, memory, and disk resources to manage the map. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
counterMap.close();
```

{% include common-links.html %}
