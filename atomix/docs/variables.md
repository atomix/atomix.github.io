---
layout: docs
project: atomix
menu: docs
title: Distributed Variables
first-section: distributed-variables
---

{:.no-margin-top}
The `atomix-variables` module provides a set of distributed atomic variables modeled on Java's [`java.util.concurrent.atomic`][JdkAtomic] package. The resources provided by the variables module do not implement JDK atomic interfaces because Atomix's APIs are asynchronous, but their methods are equivalent to their blocking counterparts and can easily be wrapped in blocking interfaces.

### DistributedValue

The [`DistributedValue`][DistributedValue] resource provides an asynchronous API similar to that of the JDK's [AtomicReference].

To create a [`DistributedValue`][DistributedValue], use the `Atomix.getValue` method:

```java
atomix.<String>getValue("test-value").thenAccept(value -> {
  // Do something with the value
});
```

The [`DistributedValue`][DistributedValue] API is asynchronous and returns [`CompletableFuture`][CompletableFuture] for all methods:

```java
value.set("Hello world!").thenRun(() -> {
  value.get().thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```

#### Expiring Value

[`DistributedValue`][DistributedValue] supports configurable TTLs for values. To set a TTL on the value, simply pass a `Duration` when setting the value:

```java
value.set("Hello world!", Duration.ofSeconds(1)).thenRun(() -> {
  System.out.println("Value set with TTL of 1 second");
});
```

Note that TTL timers are deterministically controlled by the cluster leader and are approximate representations of wall clock time that *should not be relied upon for accuracy*.

### DistributedLong

The [`DistributedLong`][DistributedLong] resource extends [`DistributedValue`][DistributedValue] to provide atomic methods for incrementing and decrementing a 64-bit number. The [`DistributedLong`][DistributedLong] interface closely mimics that of Java's [`AtomicLong`][AtomicLong].

To create a [`DistributedLong`][DistributedLong], use the `getLong` method:

```java
atomix.getLong("test-long").thenAccept(value -> {
  // Do something with the value
});
```

[`DistributedLong`][DistributedLong] returns [`CompletableFuture`][CompletableFuture] for all methods:

```java
value.incrementAndGet().thenAccept(result1 -> {
  value.getAndDecrement().thenAccept(result2 -> {
    assert result1 == result2;
  });
});
```

{% include common-links.html %}