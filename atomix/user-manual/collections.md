---
layout: content
project: atomix
menu: user-manual
title: Distributed Collections
pitch: Distributed collections
first-section: distributed-collections
---

## Distributed collections

The `atomix-collections` module provides a set of asynchronous, distributed collection-like [resources]. The resources provided by the collections module do not implement JDK collection interfaces because Atomix's APIs are asynchronous, but their methods are equivalent to their blocking counterparts and so collection resources can be easily wrapped in blocking collection interfaces.

If your project does not depend on `atomix-all`, you must add the `atomix-collections` dependency in order to access the collection classes:

```
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix-collections</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

### DistributedMap

The [DistributedMap][DistributedMap] resources provides an asynchronous API similar to that of `java.util.Map`.

To create a `DistributedMap`, pass the class to `Atomix.create(String, Class)`:

```java
atomix.<DistributedMap<String, String>>create("/test-map", DistributedMap.class).thenAccept(map -> {
  // Do something with the map
});
```

Once the map has been created, the methods closely mimic those of `java.util.Map`. `DistributedMap` returns `CompletableFuture` for all methods:

```java
map.put("foo", "Hello world!").thenRun(() -> {
  map.get("foo").thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```

To block and wait for results instead, call `join()` or `get()` on the returned `CompletableFuture`s:

```java
map.put("foo", "Hello world!").join();
assert map.get("foo").get().equals("Hello world!");
```

#### Expiring keys

`DistributedMap` supports configurable TTLs for map keys. To set a TTL on a key, simply pass a `Duration` when adding a key to the map:

```java
map.put("foo", "Hello world!", Duration.ofSeconds(1)).thenRun(() -> {
  System.out.println("Key added with TTL");
});
```

Note that TTL timers are deterministically controlled by the cluster leader and are approximate representations of wall clock time that *should not be relied upon for accuracy*.

### DistributedMultiMap

The [DistributedMultiMap][DistributedMultiMap] resources provides a map-like API for storing multiple values for each key in a map.

To create a `DistributedMultiMap`, pass the class to `Atomix.create(String, Class)`:

```java
atomix.<DistributedMultiMap<String, String>>create("/multi-map", DistributedMultiMap.class).thenAccept(map -> {
  // Do something with the multimap
});
```

Multi-maps store `Collection`s of values rather than single values.

```java
map.put("foo", "Hello world!").join();
map.put("foo", "Hello world again!").join();

Collection<String> values = map.get("foo").get();
assert values.contains("Hello world!");
assert values.contains("Hello world again!");
```

### DistributedSet

The [DistributedSet][DistributedSet] resources provides an asynchronous API similar to that of `java.util.Set`.

To create a `DistributedSet`, pass the class to `Atomix.create(String, Class)`:

```java
atomix.<DistributedSet<String>>create("/test-set", DistributedSet.class).thenAccept(set -> {
  // Do something with the set
});
```

Once the set has been created, the methods closely mimic those of `java.util.Set`. `DistributedSet` returns `CompletableFuture` for all methods:

```java
set.add("Hello world!").thenRun(() -> {
  set.contains("Hello world!").thenAccept(result -> {
    assert result;
  });
});
```

#### Expiring values

`DistributedSet` supports configurable TTLs for set values. To set a TTL on a value, simply pass a `Duration` when adding a value to the set:

```java
set.add("Hello world!", Duration.ofSeconds(1)).thenAccept(succeeded -> {
  // If the add failed, the TTL will not have been set
  if (succeeded) {
    System.out.println("Value added with TTL");
  } else {
    System.out.println("Value add failed");
  }
});
```

Note that TTL timers are deterministically controlled by the cluster leader and are approximate representations of wall clock time that *should not be relied upon for accuracy*.

### DistributedQueue

The [DistributedQueue] resources provides an asynchronous API similar to that of `java.util.Queue`.

To create a `DistributedQueue`, pass the class to `Atomix.create(String, Class)`:

```java
atomix.<DistributedQueue<String>>create("/test-queue", DistributedQueue.class).thenAccept(queue -> {
  // Do something with the queue
});
```

Once the set has been created, the methods closely mimic those of `java.util.Queue`. `DistributedQueue` returns `CompletableFuture` for all methods:

```java
queue.add("Hello world!").thenRun(() -> {
  queue.poll().thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```

{% include common-links.html %}