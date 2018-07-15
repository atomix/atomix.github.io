---
layout: user-manual
project: atomix
menu: user-manual
title: AtomicSortedMap
---

The [`AtomicSortedMap`][AtomicSortedMap] primitive is an extension of [`AtomicMap`][AtomicMap] that provides an interface consistent with Java's [`SortedMap`][SortedMap]. Sorted maps are stored only in a single partition in order to maintain order for iteration.

## Configuration

The [`AtomicSortedMap`][AtomicSortedMap] can be configured programmatically using the [`AtomicSortedMapBuilder`][AtomicSortedMapBuilder]. To create a new map builder, use the `atomicSortedMapBuilder` method, passing the name of the map to construct:

```java
AtomicSortedMapBuilder<, String> sortedMapBuilder = atomix.<String, String>atomicSortedMapBuilder("my-sorted-map");
```

The map can be configured with a [protocol][primitive-protocols] to use to replicate changes. Since `AtomicSortedMap` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Sorted maps are stored in a single partition whether or not the configured protocol is of a [partition group][partition-groups] with more than one partition. This is necessary to preserve order within the map.

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

AtomicSortedMap<String, String> sortedMap = atomix.<String, String>atomicSortedMapBuilder("my-sorted-map")
  .withProtocol(protocol)
  .build();
```

The generic parameters in the map configuration are the map key and value types. By default, arbitrary key and value types may be used. However, when non-standard types are used, class names will be serialized with map entries, and the thread context class loader will be used to load classes from names. To avoid serializing class names, register a key and value type via `withKeyType` and `withValueType`. Class-based serialization can also be disabled via `withRegistrationRequired()`.

```java
AtomicSortedMap<String, MemberId> map = atomix.<String, MemberId>atomicSortedMapBuilder("my-sorted-map")
  .withProtocol(protocol)
  .withKeyType(String.class)
  .withValueType(MemberId.class)
  .build();
```

Atomic maps support caching. When caching is enabled, the map will transparently listen for change events and update a local cache. To enable caching, use `withCacheEnabled()`:

```java
AtomicSortedMap<String, String> sortedMap = atomix.<String, String>atomicSortedMapBuilder("my-sorted-map")
  .withProtocol(protocol)
  .withCacheEnabled()
  .withCacheSize(1000)
  .build();
```

A map can also be constructed in read-only mode using `withReadOnly()`:

```java
AtomicSortedMap<String, String> sortedMap = atomix.<String, String>atomicSortedMapBuilder("my-sorted-map")
  .withProtocol(protocol)
  .withReadOnly()
  .build();
```

Atomic maps can also be configured in configuration files. To configure an atomic map primitive, use the `atomic-map` primitive type:

`atomix.conf`

```hocon
primitives.my-sorted-map {
  type: atomic-sorted-map
  cache.enabled: true
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured map, use the `getAtomicSortedMap` method:

```java
AtomicSortedMap<String, String> sortedMap = atomix.getAtomicSortedMap("my-sorted-map");
```

The map's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`AtomicSortedMap`][AtomicSortedMap] supports most of the same operations as Java's core `Map`. All operations performed on the atomic map are, as suggested by the name, guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
AtomicSortedMap<String, String> sortedMap = atomix.<String, String>atomicSortedMapBuilder("my-sorted-map")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

sortedMap.put("foo", "bar");
sortedMap.put("bar", "baz");

String firstKey = sortedMap.firstKey();
Stirng lastKey = sortedMap.lastKey();
```

Beyond the additional `firstKey()` and `lastKey()` methods, all other functions of [`AtomicSortedMap`][AtomicSortedMap] are documented in the [`AtomicMap`][AtomicMap] documentation.

### Sorted Map Views

The [`AtomicSortedMap`][AtomicSortedMap] supports submap views which are iterable and support streams.

```java
AtomicSortedMap<String, String> subMap = sortedMap.subMap("foo", "bar");

AtomicSortedMap<String, String> headMap = sortedMap.headMap("bar");

AtomicSortedMap<String, String> tailMap = sortedMap.tailMap("foo");
```

## Cleanup

While a map is in use, Atomix may consume some network, memory, and disk resources to manage the map. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
map.close();
```

{% include common-links.html %}
