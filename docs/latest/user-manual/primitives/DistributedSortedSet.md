---
layout: user-manual
project: atomix
menu: user-manual
title: DistributedSortedSet
---

The [`DistributedSortedSet`][DistributedSortedSet] primitive is an implementation of Java's [`SortedSet`][SortedSet] collection. Sorted sets can be configured for replication using a variety of [protocols][primitive-protocols] ranging from strongly consistent consensus to eventually consistent gossip protocols.

[`DistributedSortedSet`][DistributedSortedSet] is an extension of [`DistributedSet`][DistributedSet] and supports event-based notifications of changes to the set. Clients can listen for add/remove events by registering event listeners on a distributed set.

Finally, [`DistributedSortedSet`][DistributedSortedSet] supports lazy iteration and Java 8's [`Stream`][Stream]s.

## Configuration

The [`DistributedSortedSet`][DistributedSortedSet] can be configured programmatically using the [`DistributedSortedSetBuilder`][DistributedSortedSetBuilder]. To create a new set builder, use the `sortedSetBuilder` method, passing the name of the set to construct:

```java
DistributedSortedSetBuilder<String> sortedSetBuilder = atomix.<String>sortedSetBuilder("my-set");
```

The set can be configured with a [protocol][primitive-protocols] to use to replicate changes. `DistributedSortedSet` supports both strongly consistent and eventually consistent replication protocols:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]
* [`AntiEntropyProtocol`][AntiEntropyProtocol]
* [`CrdtProtocol`][CrdtProtocol]

Distributed sets are not ordered, so they are partitioned among all partitions in a [partition group][partition-groups].

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

SortedSet<String> set = atomix.<String>sortedSetBuilder("my-set")
  .withProtocol(protocol)
  .build();
```

The generic parameter in the set configuration is the element type. Sorted sets currently require a `Comparable` element type that's supported by Atomix's default serializer, e.g. `String`, `Integer`, `Duration`, etc. This is necessary to ensure the set's elements can be ordered after replication.

Sets support caching. When caching is enabled, the set will transparently listen for change events and update a local cache. To enable caching, use `withCacheEnabled()`:

```java
SortedSet<String> set = atomix.<String>sortedSetBuilder("my-set")
  .withProtocol(protocol)
  .withCacheEnabled()
  .withCacheSize(1000)
  .build();
```

A set can also be constructed in read-only mode using `withReadOnly()`:

```java
SortedSet<String> set = atomix.<String>sortedSetBuilder("my-set")
  .withProtocol(protocol)
  .withReadOnly()
  .build();
```

Sets can be configured in configuration files. To configure an set primitive, use the `sorted-set` primitive type:

`atomix.conf`

```hocon
primitives.my-set {
  type: sorted-set
  cache.enabled: true
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured set, use the `getSortedSet` method:

```java
SortedSet<String> set = atomix.getSortedSet("my-set");
```

The set's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`DistributedSortedSet`][DistributedSortedSet] is an implementation of [`SortedSet`][SortedSet] and supports a majority of the interface's methods. All operations performed on the set are guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
SortedSet<String> set = atomix.<String>sortedSetBuilder("my-set")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

set.add("c");
set.add("x");

SortedSet<String> subSet = set.subSet("b", "y");

String first = subSet.first();
String last = subSet.last();
```

### Asynchronous Operations

As with all Atomix primitives, an asynchronous analogue of the set API - [`AsyncDistributedSortedSet`][AsyncDistributedSortedSet] - can be retrieved by calling the `async()` method:

```java
// Get a synchronous DistributedSortedSet
DistributedSortedSet<String> set = atomix.getSortedSet("my-set");

// Get the underlying asynchronous DistributedSortedSet
AsyncDistributedSortedSet<String> asyncSet = set.async();

asyncSet.add("foo").thenRun(() -> {
  AsyncDistributedSortedSet<String> subSet = set.subSet("b", "y");
  subSet.first().thenAccept(first -> {
    ...
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

### Event Notifications

[`DistributedSortedSet`][DistributedSortedSet] supports publishing event notifications to client listeners. This allows clients to react to insert, update, and remove operations on the set. To add a listener to a set, simply register the listener via `addListener`:

```java
set.addListener(event -> {
  ...
});
```

When state machine-based protocols (i.e. Raft or primary-backup) are used, Atomix guarantees that events will be received in the order in which they occurred inside replicated state machines, and event listeners will be called on an Atomix event thread. For eventually consistent protocols (i.e. anti-entropy or CRDT), the guarantees of set events are specific to each protocol implementation.

Users can optionally provide a custom executor on which to call the event listener:

```java
Executor executor = Executors.newSingleThreadExecutor();
set.addListener(event -> {
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

The Atomix thread model allows for event listeners to make blocking calls on primitives within event threads. So, in response to an update event, an event listener can e.g. call `add` on the same set:

```java
// re-add entries that are removed from the set
set.addListener(event -> {
  if (event.type() == DistributedCollectionEvent.Type.REMOVE) {
    set.add(event.element());
  }
});
```

When performing blocking operations (any operation on a synchronous primitive) within an event threads, additional events and futures will be completed on a background thread pool. This means ordering guarantees are inherently relaxed when event threads are blocked.

### Iterators

[`DistributedSortedSet`][DistributedSortedSet] supports lazy iterators:

```java
for (String value : set) {
  ...
}
```

Iterators are implemented by lazily fetching batches of set elements from the partition as the elements are iterated. Once a primitive iterator has been created, it must either be exhausted or explicitly `close()`d to ensure the resources used to track the iterator state is cleaned up.

```java
Iterator<String> iterator = set.iterator();

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
AsyncIterator<String> asyncIterator = set.async().iterator();
```

### Streams

The implementation of lazy iterators also allows the set to support Java 8 [`Stream`][Stream]s:

```java
Set<String> fooValues = set.stream()
  .filter(value -> value.contains("foo"))
  .collect(Collectors.toSet());
```

## Cleanup

While a set is in use, Atomix may consume some network, memory, and disk resources to manage the set. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
set.close();
```

{% include common-links.html %}
