---
layout: content
menu: user-manual
title: Utilities
---

The following documentation explains the usage of various utility APIs provided by the `copycat-common` module.

## Builders

Throughout the project, Copycat often uses the [builder pattern](https://en.wikipedia.org/wiki/Builder_pattern) in lieu of constructors to provide users with a fluent interface for configuring complex objects. Builders are implementations of the [Builder][Builder] interface and in most cases are nested within the type they build. For instance, the `CopycatClient.Builder` builds a [CopycatClient][CopycatClient] instance. Additionally, builders usually have an associated static `builder()` method that can be used to retrieve a builder:

```java
CopycatClient.Builder builder = CopycatClient.builder();
```

The reasoning behind using a static factory method for builders is in order to transparently support recycling builders. In some cases, builders are used to configure short-lived objects such as [commands][Command] and [Queries][query]. In those cases, rather than constructing a new `Builder` for each instance (thus resulting in two objects being created for one), Copycat recycles builders via the `builder()` factory method.

## Listeners

Copycat largely provides its API for asynchronous callbacks via Java 8's [CompletableFuture][CompletableFuture]. But in some cases, users need to register to receive events that are invoked by Copycat internally. For those cases, Copycat provides a [Listener][Listener] to help manage event listeners.

Listeners work by first registering a `Consumer` for an event:

```java
DistributedTopic<String> topic = copycat.create("/topic", DistributedTopic.class).get();

Listener<String> listener = topic.onMessage(message -> System.out.println("Received " + message)).get();
```

The `Listener` acts as a registration for the user-provided `Consumer` and allows the user to unregister the listener simply by calling the `close()` method:

```java
// Stop listening for messages.
listener.close();
```

## Contexts

[Contexts][Context] are used by Copycat internally to control thread scheduling and execution. At a low level, `Context` implementations wrap single-thread or thread-pool [Executors][Executor]. All threads within a running Copycat cluster have an associated `Context`. The `Context` holds thread-unsafe objects such as a `Serializer` clone per thread.

{% include common-links.html %}