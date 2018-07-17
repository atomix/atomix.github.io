---
layout: user-manual
project: atomix
menu: user-manual
title: DistributedMultiset
---

The [`DistributedMultiset`][DistributedMultiset] primitive is an implementation of Guava's `Multiset` collection. Distributed multisets can be configured for replication using a variety of [protocols][primitive-protocols] ranging from strongly consistent consensus to eventually consistent gossip protocols.

[`DistributedMultiset`][DistributedMultiset] is an extension of [`DistributedCollection`][DistributedCollection] and supports event-based notifications of changes to the multiset. Clients can listen for add/remove events by registering event listeners on a distributed multiset.

Finally, [`DistributedMultiset`][DistributedMultiset] supports lazy iteration and Java 8's [`Stream`][Stream]s.

## Configuration

The [`DistributedMultiset`][DistributedMultiset] can be configured programmatically using the [`DistributedMultisetBuilder`][DistributedMultisetBuilder]. To create a new multiset builder, use the `multisetBuilder` method, passing the name of the multiset to construct:

```java
DistributedMultisetBuilder<String> multisetBuilder = atomix.<String>multisetBuilder("my-multiset");
```

The multiset can be configured with a [protocol][primitive-protocols] to use to replicate changes. `DistributedMultiset` supports both strongly consistent and eventually consistent replication protocols:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]
* [`AntiEntropyProtocol`][AntiEntropyProtocol]
* [`CrdtProtocol`][CrdtProtocol]

Distributed multisets are not ordered, so they are partitioned among all partitions in a [partition group][partition-groups].

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

Multiset<String> multiset = atomix.<String>multisetBuilder("my-multiset")
  .withProtocol(protocol)
  .build();
```

The generic parameter in the value configuration is the element type. By default, arbitrary element types may be used. However, when non-standard types are used, class names will be serialized with elements, and the thread context class loader will be used to load classes from names. To avoid serializing class names, register an element type via `withElementType`. Class-based serialization can also be disabled via `withRegistrationRequired()`.

```java
Multiset<Foo> multiset = atomix.<Foo>multisetBuilder("my-multiset")
  .withProtocol(protocol)
  .withElementType(Foo.class)
  .build();
```

Multisets support caching. When caching is enabled, the multiset will transparently listen for change events and update a local cache. To enable caching, use `withCacheEnabled()`:

```java
Multiset<String> multiset = atomix.<String>multisetBuilder("my-multiset")
  .withProtocol(protocol)
  .withCacheEnabled()
  .withCacheSize(1000)
  .build();
```

A multiset can also be constructed in read-only mode using `withReadOnly()`:

```java
Multiset<String> multiset = atomix.<String>multisetBuilder("my-multiset")
  .withProtocol(protocol)
  .withReadOnly()
  .build();
```

Multisets can be configured in configuration files. To configure an multiset primitive, use the `multiset` primitive type:

`atomix.conf`

```hocon
primitives.my-multiset {
  type: multiset
  cache.enabled: true
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured multiset, use the `getMultiset` method:

```java
Multiset<String> multiset = atomix.getMultiset("my-multiset");
```

The multiset's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`DistributedMultiset`][DistributedMultiset] implements `Multiset` and the default implementation supports most operations. All operations performed on the multiset are guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
Multiset<String> multiset = atomix.<String>multisetBuilder("my-multiset")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

if (multiset.add("foo")) {
  ...
}
```

### Asynchronous Operations

As with all Atomix primitives, an asynchronous analogue of the multiset API - [`AsyncDistributedMultiset`][AsyncDistributedMultiset] - can be retrieved by calling the `async()` method:

```java
// Get a synchronous DistributedMultiset
DistributedMultiset<String> multiset = atomix.getMultiset("my-multiset");

// Get the underlying asynchronous DistributedMultiset
AsyncDistributedMultiset<String> asyncMultiset = multiset.async();

asyncMultiset.add("foo").thenAccept(succeeded -> {
  ...
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

### Event Notifications

[`DistributedMultiset`][DistributedMultiset] supports publishing event notifications to client listeners. This allows clients to react to insert, update, and remove operations on the multiset. To add a listener to a multiset, simply register the listener via `addListener`:

```java
multiset.addListener(event -> {
  ...
});
```

When state machine-based protocols (i.e. Raft or primary-backup) are used, Atomix guarantees that events will be received in the order in which they occurred inside replicated state machines, and event listeners will be called on an Atomix event thread. For eventually consistent protocols (i.e. anti-entropy or CRDT), the guarantees of multiset events are specific to each protocol implementation.

Users can optionally provide a custom executor on which to call the event listener:

```java
Executor executor = Executors.newSingleThreadExecutor();
multiset.addListener(event -> {
  ...
}, executor);
```

{:.callout .callout-warning}
Custom executors can change the ordering of events. It's recommended that single thread executors be used to preserve order. Multi-threaded executors cannot provide the same guarantees as are provided by Atomix event threads or single thread executors.

The event listener will be called with an [`DistributedCollectionEvent`][DistributedCollectionEvent] instance. Each event in Atomix has an associated type which can be read via the `type()` method. To determine the type of modification that took place, use a switch statement:

```java
switch (event.type()) {
  case ADD:
    ...
    break;
  case REMOVE:
    ...
    break;
}
```

The [`DistributedCollectionEvent`][DistributedCollectionEvent] provides the added/removed element.

```java
String value = event.element();
```

The Atomix thread model allows for event listeners to make blocking calls on primitives within event threads. So, in response to an update event, an event listener can e.g. call `add` on the same multiset:

```java
// re-add entries that are removed from the multiset
multiset.addListener(event -> {
  if (event.type() == DistributedCollectionEvent.Type.REMOVE) {
    multiset.add(event.element());
  }
});
```

When performing blocking operations (any operation on a synchronous primitive) within an event threads, additional events and futures will be completed on a background thread pool. This means ordering guarantees are inherently relaxed when event threads are blocked.

### Iterators

[`DistributedMultiset`][DistributedMultiset] supports lazy iterators:

```java
for (String value : multiset) {
  ...
}
```

Iterators are implemented by lazily fetching batches of multiset elements from the partition as the elements are iterated. Once a primitive iterator has been created, it must either be exhausted or explicitly `close()`d to ensure the resources used to track the iterator state is cleaned up.

```java
Iterator<String> iterator = multiset.iterator();

try {
  String value = iterator.next();
} finally {
  iterator.close();
}
```

{:.callout .callout-warning}
Failing to exhaust or explicitly close frequently created primitive iterators may cause a memory leak.

Just as with typical synchronous primitives, the iterators provided for Atomix primitives are backed by an asynchronous implementation called [`AsyncIterator`][AsyncIterator], and the asynchronous backing iterator can be retrieved via the `async()` method:

```java
AsyncIterator<String> asyncIterator = multiset.async().iterator();
```

### Streams

The implementation of lazy iterators also allows the multiset to support Java 8 [`Stream`][Stream]s:

```java
Set<String> fooValues = multiset.stream()
  .filter(value -> value.contains("foo"))
  .collect(Collectors.toSet());
```

## Cleanup

While a multiset is in use, Atomix may consume some network, memory, and disk resources to manage the multiset. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
multiset.close();
```

{% include common-links.html %}
