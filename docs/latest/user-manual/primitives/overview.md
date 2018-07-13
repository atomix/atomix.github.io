---
layout: user-manual
project: atomix
menu: user-manual
title: Overview
---

Distributed primitives are high-level objects that can be used to store/replicate data and coordinate state changes within an Atomix-based distributed system. They are designed to solve a variety of common distributed systems challenges in a simple API with a low barrier to entry.

In general, there are two categories of distributed primitives:
* Data primitives - simple data structures for replicating state
  * `AtomicValue`
  * `AtomicCounter`
  * `AtomicMap`
  * `AtomicMultimap`
  * `DistributedSet`
  * `DistributedMap`
  * etc
* Coordination primitives - objects for coordinating state changes across nodes
  * `LeaderElection`
  * `DistributedLock`
  * `DistributedSemaphore`
  * `WorkQueue`
  * etc

At a low level, distributed primitives are modelled as replicated state machines backed by several different [replication protocols][primitive-protocols]. Primitives can be configured for different consistency levels, fault tolerance, replication factors, etc, based on their use case. Additionally, primitives can be accessed via the Atomix [agent][agent] REST API.

## Constructing Distributed Primitives

Distributed primitives can be constructed in a several ways. As with other areas of the Atomix API, the most common way to build a distributed primitive using the Java API is through builders. Primitive builders are created by calling the `*Builder` methods on the [`Atomix`][Atomix] object interface:

```java
AtomicMap<String, String> map = atomix.atomicMapBuilder("my-map")
  .withNullValues()
  .withCacheEnabled()
  .withCacheSize(100)
  .build();
```

Note that when using primitive builders, a [primitive protocol][primitive-protocols] must be provided.

In addition to primitive builders, multiton primitive instances can be retrieved via getters on the [`Atomix`][Atomix] instance:

```java
AtomicMap<String, String> map = atomix.getAtomicMap("my-map");
```

When retrieving multiton primitives via getters, the first time the getter is called on a node the primitive instance will be created. Note that primitives created via this API must be configured in the Atomix [configuration][configuration] when the instance is constructed.

## Synchronous and Asynchronous Primitives

All distributed primitives have both a synchronous (blocking) API and an asynchronous (non-blocking) counterpart API. Builders and getters will always return the blocking version of the API - e.g. `AtomicMap` - and underlying that API will be an asynchronous version - e.g. `AsyncAtomicMap` - which can be retrieved by simply calling the `async()` method:

```java
AsyncAtomicMap<String, String> map = atomix.atomicMapBuilder("my-map")
  .withNullValues()
  .withCacheEnabled()
  .withCacheSize(100)
  .build()
  .async();
```

Asynchronous APIs use [`CompletableFuture`][CompletableFuture]s to provide promises for method return calls.

{% include common-links.html %}
