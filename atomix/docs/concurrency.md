---
layout: docs
project: atomix
menu: docs
title: Distributed Concurrency
pitch: Primitives for distributed concurrency
---

## DistributedLock

The [`DistributedLock`][DistributedLock] resources provides an asynchronous API similar to that of the JDK's [`Lock`][JdkLock].

To create a [`DistributedLock`][DistributedLock], use the `Atomix.getLock` method:

```java
atomix.getLock("foo").thenAccept(lock -> {
  // Do something with the lock
});
```

The [`DistributedLock`][DistributedLock] API is asynchronous and returns [`CompletableFuture`][CompletableFuture] for all methods:

```java
lock.lock().thenRun(() -> {
  // Do some stuff and then...
  lock.unlock();
});
```

To block and wait for the lock to be acquired instead, call `join()` or `get()` on the returned [`CompletableFuture`][CompletableFuture]s:

```java
lock.lock().join();

// Do some stuff

lock.unlock().join();
```

{% include common-links.html %}