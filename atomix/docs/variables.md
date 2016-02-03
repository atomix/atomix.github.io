---
layout: docs
project: atomix
menu: docs
title: Distributed Variables
pitch: Simple distributed atomic variables
first-section: distributed-variables
---

## Distributed variables

The `atomix-variables` module provides a set of distributed atomic variables modeled on Java's `java.util.concurrent.atomic` package. The resources provided by the atomic module do not implement JDK atomic interfaces because Atomix's APIs are asynchronous, but their methods are equivalent to their blocking counterparts and so atomic resources can be easily wrapped in blocking interfaces.

If your project does not depend on `atomix-all`, you must add the `atomix-variables` dependency in order to access the atomic classes:

```
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix-variables</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

### DistributedValue

The [DistributedValue][DistributedValue] resource provides an asynchronous API similar to that of `java.util.concurrent.atomic.AtomicReference`.

To create a `DistributedValue`, use the `Atomix.getValue` method:

```java
atomix.<String>getValue("test-value").thenAccept(value -> {
  // Do something with the value
});
```

Once the value has been created, the methods closely mimic those of `java.util.concurrent.atomic.AtomicReference`. `DistributedValue` returns `CompletableFuture` for all methods:

```java
value.set("Hello world!").thenRun(() -> {
  value.get().thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```

#### Expiring value

`DistributedValue` supports configurable TTLs for values. To set a TTL on the value, simply pass a `Duration` when setting the value:

```java
value.set("Hello world!", Duration.ofSeconds(1)).thenRun(() -> {
  System.out.println("Value set with TTL of 1 second");
});
```

Note that TTL timers are deterministically controlled by the cluster leader and are approximate representations of wall clock time that *should not be relied upon for accuracy*.

### DistributedLong

The [DistributedLong] resource extends [DistributedValue] to provide atomic methods for incrementing and decrementing a 64-bit number. The `DistributedLong` interface closely mimics that of Java's `java.util.concurrent.atomic.AtomicLong`.

To create a `DistributedLong`, use the `getLong` method:

```java
atomix.getLong("test-long").thenAccept(value -> {
  // Do something with the value
});
```

`DistributedLong` returns `CompletableFuture` for all methods:

```java
value.incrementAndGet().thenAccept(result1 -> {
  value.getAndDecrement().thenAccept(result2 -> {
    assert result1 == result2;
  });
});
```

{% include common-links.html %}