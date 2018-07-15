---
layout: user-manual
project: atomix
menu: user-manual
title: AtomicValue
---

The [`AtomicValue`][AtomicValue] primitive is a distributed implementation of Java's [`AtomicReference`][AtomicReference].

## Configuration

The [`AtomicValue`][AtomicValue] can be configured programmatically using the [`AtomicValueBuilder`][AtomicValueBuilder]. To create a new value builder, use the `atomicValueBuilder` method, passing the name of the value to construct:

```java
AtomicValueBuilder valueBuilder = atomix.atomicValueBuilder("my-value");
```

The value can be configured with a `PrimitiveProtocol` to use to replicate changes. Since `AtomicValue` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Additionally, when using partitioned protocols, the value will be replicated only within a single partition for consistency.

```java
AtomicValue<String> value = atomix.<String>atomicValueBuilder("my-value")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();
```

The generic parameter in the value configuration is the value type. By default, arbitrary value types may be used. However, when non-standard types are used, class names will be serialized with values, and the thread context class loader will be used to load classes from names. To avoid serializing class names, register a value type via `withValueType`. Class-based serialization can also be disabled via `withRegistrationRequired()`.

```java
AtomicValue<Foo> value = atomix.<Foo>atomicValueBuilder("my-value")
  .withProtocol(protocol)
  .withValueType(Foo.class)
  .build();
```

Atomic values can also be configured in configuration files. To configure an atomic value primitive, use the `atomic-value` primitive type:

`atomix.conf`

```hocon
primitives.my-value {
  type: atomic-value
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured value, use the `getAtomicValue` method:

```java
AtomicValue<String> value = atomix.getAtomicValue("my-value");
```

The value's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`AtomicValue`][AtomicValue] supports most of the same operations as Java's core `AtomicLong`. All operations performed on the atomic value are, as suggested, guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
AtomicValue<String> value = atomix.<String>atomicValueBuilder("my-value")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

long value = value.incrementAndGet();
if (value.compareAndSet(value, 1)) {
  ...
}
```

As with all Atomix primitives, an asynchronous analogue of the value API - [`AsyncAtomicValue`][AsyncAtomicValue] - can be retrieved by calling the `async()` method:

```java
AsyncAtomicValue asyncValue = value.async();

asyncValue.incrementAndGet().thenAccept(value -> {
  asyncValue.compareAndSet(value, 1).thenAccept(() -> {
    ...
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

### Event Notifications

[`AtomicValue`][AtomicValue] supports publishing event notifications to client listeners. This allows clients to react to insert and remove operations on the value. To add a listener to a value, simply register the listener via `addListener`:

```java
value.addListener(event -> {
  ...
});
```

Atomix guarantees that events will be received in the order in which they occurred inside replicated state machines, and event listeners will be called on an Atomix event thread. Users can optionally provide a custom executor on which to call the event listener:

```java
Executor executor = Executors.newSingleThreadExecutor();
value.addListener(event -> {
  ...
}, executor);
```

{:.callout .callout-warning}
Custom executors can change the ordering of events. It's recommended that single thread executors be used to preserve order. Multi-threaded executors cannot provide the same guarantees as are provided by Atomix event threads or single thread executors.

The event listener will be called with an [`AtomicValueEvent`][AtomicValueEvent] instance. The event contains both the previous value and the updated value for all updates. The previous value can be read via `oldValue()` and the updated value via `newValue()`.

```java
String oldValue = event.oldValue();
String newValue = event.newValue();
```

The Atomix thread model allows for event listeners to make blocking calls on primitives within event threads. So, in response to an update event, an event listener can e.g. call `set` on the same value:

```java
// Rewrite the old value after an update
value.addListener(event -> {
  value.set(event.oldValue());
});
```

When performing blocking operations (any operation on a synchronous primitive) within an event threads, additional events and futures will be completed on a background thread pool. This means ordering guarantees are inherently relaxed when event threads are blocked.

## Cleanup

While a value is in use, Atomix may consume some network, memory, and disk resources to manage the value. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
value.close();
```

{% include common-links.html %}
