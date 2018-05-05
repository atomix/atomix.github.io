---
layout: user-manual
project: atomix
menu: user-manual
title: Defining the Primitive Type
---

The first step to creating a custom distributed primitive is defining the primitive type. To create a new type, implement the [`PrimitiveType`][PrimitiveType] interface:

```java
public class DistributedSemaphoreType implements PrimitiveType<DistributedSemaphoreBuilder, DistributedSemaphoreConfig, DistributedSemaphore> {
    @Override
    public String id() {
        return "semaphore";
    }
}
```

The [`PrimitiveType`][PrimitiveType] interface provides all the classes relevant to managing the distributed primitive, e.g. builders, configuration, and state machine. The interface requires three generic arguments:
* The `DistributedPrimitiveBuilder` class
* The `DistributedPrimitiveConfig` class
* The base `DistributedPrimitive` interface constructed by the builder

## Synchronous and Asynchronous Primitive APIs

Atomix primitives are almost always developed with a pair of APIs: synchronous and asynchronous. Typically, synchronous (blocking) implementations wrap their asynchronous counterpart. Synchronous interface extend the [`SyncPrimitive`][SyncPrimitive] interface and asynchronous interfaces extend the [`AsyncPrimitive`][AsyncPrimitive] interface. The convention is to prepend the `Async*` prefix to the asynchronous version of the primitive API:

```java
public interface DistributedLock extends SyncPrimitive {
  long lock();
  Optional<Long> tryLock();
  Optional<Long> tryLock(Duration timeout);
  void unlock();
    
  @Override
  AsyncDistributedLock async();
}
```

Asynchronous interface should use Java 8's [`CompletableFuture`][CompletableFuture] for parity with the rest of the Atomix primitive API:

```java
public interface AsyncDistributedLock extends AsyncPrimitive {
    CompletableFuture<Long> lock();
    CompletableFuture<Optional<Long>> tryLock(Duration timeout);
    CompletableFuture<Void> unlock();
    
    @Override
    DistributedLock sync();
}
```

It's also convention to override the `sync()` and `async()` methods to return the correct counterpart interface.

{% include common-links.html %}
