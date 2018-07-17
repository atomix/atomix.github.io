---
layout: user-manual
project: atomix
menu: user-manual
title: DistributedNavigableMap
---

The [`DistributedNavigableMap`][DistributedNavigableMap] primitive is a distributed implementation of Java's [`NavigableMap`][NavigableMap]. Navigable maps are stored only in a single partition in order to maintain order for iteration.

## Configuration

The [`DistributedNavigableMap`][DistributedNavigableMap] can be configured programmatically using the [`DistributedNavigableMapBuilder`][DistributedNavigableMapBuilder]. To create a new map builder, use the `navigableMapBuilder` method, passing the name of the map to construct:

```java
DistributedNavigableMapBuilder<String, String> navigableMapBuilder = atomix.<String, String>navigableMapBuilder("my-navigable-map");
```

The map can be configured with a [protocol][primitive-protocols] to use to replicate changes. Since `DistributedNavigableMap` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Sorted maps are stored in a single partition whether or not the configured protocol is of a [partition group][partition-groups] with more than one partition. This is necessary to preserve order within the map.

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

NavigableMap<String, String> navigableMap = atomix.<String, String>navigableMapBuilder("my-navigable-map")
  .withProtocol(protocol)
  .build();
```

The generic parameters in the map configuration are the map key and value types. By default, arbitrary key and value types may be used. However, when non-standard types are used, class names will be serialized with map entries, and the thread context class loader will be used to load classes from names. To avoid serializing class names, register a key and value type via `withKeyType` and `withValueType`. Class-based serialization can also be disabled via `withRegistrationRequired()`.

```java
NavigableMap<String, MemberId> map = atomix.<String, MemberId>navigableMapBuilder("my-navigable-map")
  .withProtocol(protocol)
  .withKeyType(String.class)
  .withValueType(MemberId.class)
  .build();
```

Atomic maps support caching. When caching is enabled, the map will transparently listen for change events and update a local cache. To enable caching, use `withCacheEnabled()`:

```java
NavigableMap<String, String> navigableMap = atomix.<String, String>navigableMapBuilder("my-navigable-map")
  .withProtocol(protocol)
  .withCacheEnabled()
  .withCacheSize(1000)
  .build();
```

A map can also be constructed in read-only mode using `withReadOnly()`:

```java
NavigableMap<String, String> navigableMap = atomix.<String, String>navigableMapBuilder("my-navigable-map")
  .withProtocol(protocol)
  .withReadOnly()
  .build();
```

Atomic maps can also be configured in configuration files. To configure an atomic map primitive, use the `navigable-map` primitive type:

`atomix.conf`

```hocon
primitives.my-navigable-map {
  type: navigable-map
  cache.enabled: true
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured map, use the `getNavigableMap` method:

```java
NavigableMap<String, String> navigableMap = atomix.getNavigableMap("my-navigable-map");
```

The map's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`DistributedNavigableMap`][DistributedNavigableMap] implements [`NavigableMap`][NavigableMap] and the default implementation supports the majority of its methods. All operations performed on the atomic map are guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
NavigableMap<String, String> navigableMap = atomix.<String, String>navigableMapBuilder("my-navigable-map")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

navigableMap.put("foo", "bar");
navigableMap.put("bar", "baz");

String floorKey = navigableMap.floorKey("foo");
Map.Entry<String, String> lowerEntry = navigableMap.lowerEntry("foo");
```

Beyond the additional [`NavigableMap`][NavigableMap] methods, all other functions of [`DistributedNavigableMap`][DistributedNavigableMap] are documented in the [`AtomicMap`][AtomicMap] documentation.

## Navigable Map Views

The [`DistributedNavigableMap`][DistributedNavigableMap] primitive supports ordered views of keys and entries:
* `navigableKeySet()` - a [`DistributedNavigableSet`][DistributedNavigableSet] of keys
* `subMap` - returns a [`DistributedNavigableMap`][DistributedNavigableMap] of a subset of the entries in the map
* `headMap` - returns a [`DistributedNavigableMap`][DistributedNavigableMap] of a subset of the entries at the head the map
* `tailMap` - returns a [`DistributedNavigableMap`][DistributedNavigableMap] of a subset of the entries at the tail of the map

Each of the views support lazy iteration and Java 8's [`Stream`][Stream]s.

```java
NavigableMap<String, Integer> navigableMap = ...

navigableMap.put("a", 1);
navigableMap.put("b", 2);
navigableMap.put("c", 3);

// Prints 3, 2, 1
navigableMap.navigableKeySet().descendingSet().forEach(key -> {
  System.out.println(navigableMap.get(key));
});
```

## Cleanup

While a map is in use, Atomix may consume some network, memory, and disk resources to manage the map. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
map.close();
```

{% include common-links.html %}
