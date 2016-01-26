---
layout: content
project: catalyst
menu: docs
title: Utilities
pitch: Tools for empowering asynchronous applications
first-section: utilities
---

## Builders

Throughout the project, Catalyst often uses the [builder pattern](https://en.wikipedia.org/wiki/Builder_pattern) in lieu of constructors to provide users with a fluent interface for configuring complex objects. Builders are implementations of the [Builder][Builder] interface and in most cases are nested within the type they build. For instance, the `AtomixClient.Builder` builds a [AtomixClient][AtomixClient] instance. Additionally, builders usually have an associated static `builder()` method that can be used to retrieve a builder:

```java
CatalystClient.Builder builder = CatalystClient.builder();
```

The reasoning behind using a static factory method for builders is in order to transparently support recycling builders. In some cases, builders are used to configure short-lived objects such as [commands][Command] and [Queries][query]. In those cases, rather than constructing a new `Builder` for each instance (thus resulting in two objects being created for one), Catalyst recycles builders via the `builder()` factory method.

## Listeners

Catalyst largely provides its API for asynchronous callbacks via Java 8's [CompletableFuture][CompletableFuture]. But in some cases, users need to register to receive events that are invoked by Catalyst internally. For those cases, Catalyst provides a [Listener][Listener] to help manage event listeners.

Listeners work by first registering a `Consumer` for an event:

```java
DistributedTopic<String> topic = atomix.create("/topic", DistributedTopic.class).get();

Listener<String> listener = topic.onMessage(message -> System.out.println("Received " + message)).get();
```

The `Listener` acts as a registration for the user-provided `Consumer` and allows the user to unregister the listener simply by calling the `close()` method:

```java
// Stop listening for messages.
listener.close();
```

## Contexts

[Contexts][Context] are used by Catalyst internally to control thread scheduling and execution. At a low level, `Context` implementations wrap single-thread or thread-pool [Executors][Executor]. All threads within a running Catalyst cluster have an associated `Context`. The `Context` holds thread-unsafe objects such as a `Serializer` clone per thread.

{% include common-links.html %}