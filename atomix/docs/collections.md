---
layout: docs
project: atomix
menu: docs
title: Distributed Collections
first-section: distributed-collections
---

{:.no-margin-top}
The `atomix-collections` module provides a set of asynchronous, distributed collection-like [resources]. The resources provided by the collections module do not implement JDK collection interfaces because Atomix's APIs are asynchronous, but their methods are equivalent to their blocking counterparts and can easily be wrapped in blocking collection interfaces.

### DistributedMap

The [`DistributedMap`][DistributedMap] resources provides an asynchronous API similar to that of `java.util.Map`.

To create a [`DistributedMap`][DistributedMap], use the [`Atomix#getMap(String)`][Atomix.getMap] method:

```java
atomix.<String, String>getMap("foo-map").thenAccept(map -> {
  // Do something with the map
});
```

Once the map has been created, the methods closely mimic those of `java.util.Map`. [`DistributedMap`][DistributedMap] returns [`CompletableFuture`][CompletableFuture] for all methods:

```java
map.put("foo", "Hello world!").thenRun(() -> {
  map.get("foo").thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```

To block and wait for results instead, call `join()` or `get()` on the returned [`CompletableFuture`][CompletableFuture]s:

```java
map.put("foo", "Hello world!").join();
assert map.get("foo").join().equals("Hello world!");
```

#### Expiring Keys

[`DistributedMap`][DistributedMap] supports configurable TTLs for map keys. To set a TTL on a key, simply pass a `Duration` when adding a key to the map:

```java
map.put("foo", "Hello world!", Duration.ofSeconds(1)).thenRun(() -> {
  System.out.println("Key added with TTL");
});
```

Note that TTL timers are deterministically controlled by the cluster leader and are approximate representations of wall clock time that *should not be relied upon for accuracy*.

#### Events

[`DistributedMap`][DistributedMap] also supports events that indicate when a map has changed:

```java
map.onAdd(event -> {
  System.out.println("Added " + event.entry());
});

map.onRemove(event -> {
  System.out.println("Removed " + event.entry());
});

map.onUpdate(event -> {
  System.out.println("Updated " + event.entry());
});
```

### DistributedMultiMap

The [`DistributedMultiMap`][DistributedMultiMap] resources provides a map-like API for storing multiple values for each key in a map.

To create a [`DistributedMultiMap`][DistributedMultiMap], use the [`Atomix#getMultiMap(String)`][Atomix.getMultiMap] method:

```java
atomix.<String, String>getMultiMap("foo-map").thenAccept(map -> {
  // Do something with the multimap
});
```

Multi-maps store `Collection`s of values rather than single values.

```java
map.put("foo", "Hello world!").join();
map.put("foo", "Hello world again!").join();

Collection<String> values = map.get("foo").join();
assert values.contains("Hello world!");
assert values.contains("Hello world again!");
```

### DistributedSet

The [`DistributedSet`][DistributedSet] resources provides an asynchronous API similar to that of `java.util.Set`.

To create a [`DistributedSet`][DistributedSet], use the [`Atomix#getSet(String)`][Atomix.getSet] method:

```java
atomix.<String>getSet("foo-set").thenAccept(set -> {
  // Do something with the set
});
```

Once the set has been created, the methods closely mimic those of `java.util.Set`. [`DistributedSet`][DistributedSet] returns [`CompletableFuture`][CompletableFuture] for all methods:

```java
set.add("Hello world!").thenRun(() -> {
  set.contains("Hello world!").thenAccept(result -> {
    assert result;
  });
});
```

#### Expiring Values

[`DistributedSet`][DistributedSet] supports configurable TTLs for set values. To set a TTL on a value, simply pass a `Duration` when adding a value to the set:

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

The [`DistributedQueue`][DistributedQueue] resources provides an asynchronous API similar to that of `java.util.Queue`.

To create a [`DistributedQueue`][DistributedQueue], use the [`Atomix#getQueue(String)`][Atomix.getQueue] method:

```java
atomix.<String>getQueue("foo-queue").thenAccept(queue -> {
  // Do something with the queue
});
```

Once the set has been created, the methods closely mimic those of `java.util.Queue`. [`DistributedQueue`][DistributedQueue] returns [`CompletableFuture`][CompletableFuture] for all methods:

```java
queue.add("Hello world!").thenRun(() -> {
  queue.poll().thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```

{% include common-links.html %}