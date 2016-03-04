---
layout: docs
project: atomix
menu: docs
title: Distributed Messaging
pitch: Reliable and unreliable distributed messaging
first-section: distributed-messaging
---

{:.no-margin-top}
The `atomix-messaging` module provides a set of distributed messaging tools. These tools are designed tofacilitate communication in a distributed system.

### DistributedMessageBus

The [DistributedMessageBus] resource provides a simple asynchronous framework for unreliable synchronous messaging between instances of the resource in a cluster. Message bus resource instances communicate with one another by each starting a [Server] and connecting to each other instance via a [Client]. Users can register message bus handlers which are identified by an *address*, and handler address registrations are shared across the cluster via an internal replicated state machine.

To use the message bus, create a `DistributedMessageBus` resource:

```java
DistributedMessageBus bus = atomix.getMessageBus("bus").get();
```

Each instance of the message bus must be `open`ed by providing the bus with a local [Address] to which to bind the server:

```java
Address address = new Address("123.456.789.0", 5000);

bus.open(address).join();
```

When the message bus is opened, all other instances of the message bus resource will be notified before the `open` operation completes.

#### Message Producers

To send a message to a registered message bus address, create a `MessageProducer` and `send` the message:

```java
MessageProducer<String> producer = bus.producer("foo").get();

producer.send("hello");
```

The `send` method returns a `CompletableFuture` which will be completed with the response value of the receiver once received.

#### Message Consumers

To register a message consumer, create a `MessageConsumer` for a message bus *address*:

```java
bus.consumer("foo", message -> {
  return CompletableFuture.completedFuture("world!");
});
```

The `consumer` method will return a `CompletableFuture` which will be completed once all instances of the message bus have been notified of the new consumer registration.

### DistributedTopic

The [DistributedTopic] resource provides persistent, publish subscribe messaging between instances of the resource. Topic resource instances can subscribe to receive messages for a topic, and when a message is `publish`ed to a topic, the message will be committed to the underlying [Raft] commit log and then asynchronously sent to all available subscribers.

To use the topic resource, create a `DistributedTopic` resource:

```java
DistributedTopic<String> topic = atomix.getTopic("topic").get();
```

To register a topic message listener, use the `onMessage` method:

```java
topic.onMessage(message -> System.out.println("Got message: " + message));
```

To publish a message to the topic, use the `publish` method:

```java
topic.publish("Hello world!").thenRun(() -> System.out.println("Published message!"));
```

The returned [CompletableFuture] will be completed once the message has been replicated and stored in the Atomix cluster. By default, messages will be sent to subscribers asynchronously. To configure the resource to synchronously send messages to all subscribers before completing the `publish` operation, configure the resource's `Consistency` to `ATOMIC`:

```java
topic.with(Consistency.ATOMIC).publish("Hello world!").join();
```

{% include common-links.html %}