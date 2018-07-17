---
layout: user-manual
project: atomix
menu: user-manual
title: DistributedMap
---

[`DistributedMap`][DistributedMap] is a distributed implementation of Java's [`Map`][Map] utility. In contrast to [`AtomicMap`][AtomicMap], the `DistributedMap` API does not guarantee consistency and therefore can be replicated using eventually consistent [protocols][primitive-protocols].

[`DistributedMap`][DistributedMap] supports event-based notifications of changes to the map. Clients can listen for inserted/updated/removed entries by registering event listeners on an atomic map.

Finally, [`DistributedMap`][DistributedMap] supports key set, values, and entry set views that are iterable and support Java 8 streams.

## Configuration

The [`DistributedMap`][DistributedMap] can be configured programmatically using the [`DistributedMapBuilder`][DistributedMapBuilder]. To create a new map builder, use the `mapBuilder` method, passing the name of the map to construct:

```java
DistributedMapBuilder<String, String> mapBuilder = atomix.<String, String>mapBuilder("my-map");
```

The map can be configured with a [protocol][primitive-protocols] to use to replicate changes. `DistributedMap` does not require strong consistency and therefore supports more replication protocol than [`AtomicMap`][AtomicMap]:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]
* [`AntiEntropyProtocol`][AntiEntropyProtocol]

When using partitioned protocols like `MultiRaftProtocol` and `MultiPrimaryProtocol`, the map will be partitioned and replicated among all partitions in the configured [partition group][partition-groups].

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

Map<String, String> map = atomix.<String, String>mapBuilder("my-map")
  .withProtocol(protocol)
  .build();
```

The generic parameters in the map configuration are the map key and value types. By default, arbitrary key and value types may be used. However, when non-standard types are used, class names will be serialized with map entries, and the thread context class loader will be used to load classes from names. To avoid serializing class names, register a key and value type via `withKeyType` and `withValueType`. Class-based serialization can also be disabled via `withRegistrationRequired()`.

```java
Map<String, MemberId> map = atomix.<String, MemberId>mapBuilder("my-map")
  .withProtocol(protocol)
  .withKeyType(String.class)
  .withValueType(MemberId.class)
  .build();
```

Atomic maps support caching. When caching is enabled, the map will transparently listen for change events and update a local cache. To enable caching, use `withCacheEnabled()`:

```java
Map<String, String> map = atomix.<String, String>mapBuilder("my-map")
  .withProtocol(protocol)
  .withCacheEnabled()
  .withCacheSize(1000)
  .build();
```

A map can also be constructed in read-only mode using `withReadOnly()`:

```java
Map<String, String> map = atomix.<String, String>mapBuilder("my-map")
  .withProtocol(protocol)
  .withReadOnly()
  .build();
```

Atomic maps can also be configured in configuration files. To configure an atomic map primitive, use the `atomic-map` primitive type:

`atomix.conf`

```hocon
primitives.my-map {
  type: atomic-map
  cache.enabled: true
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured map, use the `getMap` method:

```java
Map<String, String> map = atomix.getMap("my-map");
```

The map's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`DistributedMap`][DistributedMap] supports most of the same operations as Java's core `Map`. All operations performed on the atomic map are, as suggested by the name, guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
Map<String, String> map = atomix.<String, String>mapBuilder("my-map")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

map.put("foo", "bar");
```

### Atomic Operations

Atomic operations can be performed on a `DistributedMap` using the various `compute` methods:

```java
Map<String, String> map = atomix.getMap("my-map");

map.put("foo", "hello");

map.compute("foo", (key, value) -> {
  return value + " world";
})
```

Protocol implementations must guarantee `compute` methods are atomic. For partitioned maps, when `compute`, `computeIfAbsent`, or `computeIfPresent` is used, the map will transparently perform optimistic locking and retries internally.

{:.callout .callout-warning}
Map `compute` methods should be used conservatively. Maps that experience high lock contention can quickly overload a partition from optimistic lock retries.

### Asynchronous Operations

As with all Atomix primitives, an asynchronous analogue of the map API - [`AsyncDistributedMap`][AsyncDistributedMap] - can be retrieved by calling the `async()` method:

```java
DistributedMap<String, String> map = atomix.getMap("my-map");
AsyncDistributedMap<String, String> asyncMap = map.async();

asyncMap.get("foo").thenAccept(value -> {
  asyncMap.replace("foo", value, value + "world").thenAccept(succeeded -> {
    System.out.println("Replace successful!");
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

### Event Notifications

[`DistributedMap`][DistributedMap] supports publishing event notifications to client listeners. This allows clients to react to insert, update, and remove operations on the map. To add a listener to a map, simply register the listener via `addListener`:

```java
map.addListener(event -> {
  ...
});
```

Atomix guarantees that events will be received in the order in which they occurred inside replicated state machines, and event listeners will be called on an Atomix event thread. Users can optionally provide a custom executor on which to call the event listener:

```java
Executor executor = Executors.newSingleThreadExecutor();
map.addListener(event -> {
  ...
}, executor);
```

{:.callout .callout-warning}
Custom executors can change the ordering of events. It's recommended that single thread executors be used to preserve order. Multi-threaded executors cannot provide the same guarantees as are provided by Atomix event threads or single thread executors.

The event listener will be called with an [`MapEvent`][MapEvent] instance. Each event in Atomix has an associated type which can be read via the `type()` method. To determine the type of modification that took place, use a switch statement:

```java
switch (event.type()) {
  case INSERT:
    ...
    break;
  case UPDATE:
    ...
    break;
  case REMOVE:
    ...
    break;
}
```

The [`MapEvent`][MapEvent] provides both the previous value and the updated value for all updates. The previous value can be read via `oldValue()` and the updated value via `newValue()`.

```java
String value;
if (event.type() == MapEvent.Type.REMOVE) {
  value = event.oldValue();
} else {
  value = event.newValue();
}
```

The Atomix thread model allows for event listeners to make blocking calls on primitives within event threads. So, in response to an update event, an event listener can e.g. call `put` on the same map:

```java
// Recreate entries that are removed from the map
map.addListener(event -> {
  if (event.type() == MapEvent.Type.REMOVE) {
    map.put(event.key(), event.newValue());
  }
});
```

When performing blocking operations (any operation on a synchronous primitive) within an event threads, additional events and futures will be completed on a background thread pool. This means ordering guarantees are inherently relaxed when event threads are blocked.

### Map Views

The [`DistributedMap`][DistributedMap] primitive supports views that are common to Java maps:
* `keySet()` returns a `DistributedSet` primitive which implements [`java.util.Set`][Set]
* `values()` returns a `DistributedCollection` primitive which implements [`java.util.Collection`][Collection]
* `entrySet()` returns a `DistributedSet` primitive which implements [`java.util.Set`][Set]

The collections are views of the `DistributedMap`'s state, so changes to the map will be reflected in the key set, values, or entry set and vice versa.

```java
map.put("foo", "bar");

assert map.keySet().contains("foo");

map.keySet().remove("foo");

assert !map.containsKey("foo");
```

When using the [`AsyncDistributedMap`][AsyncDistributedMap] API, asynchronous analogues of the view primitives will be returned instead.

```java
map.put("foo", "bar");

map.async().keySet().remove("foo").thenRun(() -> {
  assert !map.containsKey("foo");
});
```

### Iterators

All [`DistributedMap`][DistributedMap] views support lazy iterators:

```java
for (String key : map.keySet()) {
  ...
}
```

Iterators are implemented by lazily fetching batches of keys/values/entries from each partition as the items are iterated. Once a primitive iterator has been created, it must either be exhausted or explicitly `close()`d to ensure the resources used to track the iterator state is cleaned up.

```java
Iterator<String> keyIterator = map.keySet().iterator();

try {
  String key = keyIterator.next();
} finally {
  iterator.close();
}
```

{:.callout .callout-warning}
Failing to exhaust or explicitly close frequently created primitive iterators may cause a memory leak.

Just as with typical synchronous primitives, the iterators provided for Atomix primitives are backed by an asynchronous implementation called [`AsyncIterator`][AsyncIterator], and the asynchronous backing iterator can be retrieved via the `async()` method:

```java
AsyncIterator<String> asyncIterator = map.values().iterator().async();
// or...
AsyncIterator<String> asyncIterator = map.async().values().iterator();
```

### Streams

The implementation of lazy iterators for map views also allows the map to support Java 8 [`Stream`][Stream]s:

```java
Set<String> fooKeys = map.entrySet().stream()
  .filter(entry -> entry.getValue().equals("foo"))
  .map(entry -> entry.getKey())
  .collect(Collectors.toSet());
```

## Cleanup

While a map is in use, Atomix may consume some network, memory, and disk resources to manage the map. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
map.close();
```

{% include common-links.html %}
