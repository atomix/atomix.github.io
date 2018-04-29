---
layout: user-manual
project: atomix
menu: user-manual
title: Direct Messaging
---

Atomix provides a variety of services that can be used for direct and publish-subscribe style communication. Underlying each of the communication abstractions is [Netty](https://netty.io/), which is used for all inter-cluster communication. Direct messaging is performed through the [`ClusterMessagingService`][ClusterMessagingService] interface. The `ClusterMessagingService` supports unicast, multicast, broadcast, and request-reply messaging patterns.

An important concept for inter-cluster communication is the message subject. Subjects are arbitrary strings that indicate the type of message being sent. Every message that's sent by one node and received by another must be identified by a subject. This allows senders and receivers to filter relevant messages.

#### Registering message subscribers

Messages are received on subscribers registered with the `subscribe` message:

```java
atomix.messagingService().subscribe("test", message -> {
  return CompletableFuture.completedFuture(message);
});
```

Three types of subscribers can be registered:
* A synchronous subscriber that returns a result and must provide an `Executor` on which to consume messages
* An asynchronous subscriber that must return `CompletableFuture`
* A consumer that must provide an `Executor` on which to consume messages

Additionally, [serializers](#message-serialization) can be provided for custom object types.

#### Sending messages

As noted above, messages can be sent using a variety of different communication patterns:
* `unicast` sends a message to a single peer without awaiting a response
* `multicast` sends a message to a set of members without awaiting any responses
* `broadcast` sends a message to all members known to the local [`ClusterMembershipService`][ClusterMembershipService] without awaiting any responses
* `send` sends a direct message to a peer and awaits a response via [`CompletableFuture`][CompletableFuture]

```java
// Send a request-reply message to node "foo"
atomix.messagingService().send("test", "Hello world!", MemberId.from("foo")).thenAccept(response -> {
  System.out.println("Received " + response);
});
```

#### Message serialization

The [`ClusterMessagingService`][ClusterMessagingService] uses a default serializer to serialize a variety of core data structures, but often custom objects need to be communicated across the wire. The messaging service provides overloaded methods for providing arbitrary message encoders/decoders for requests/replies:

```java
Serializer serializer = Serializer.using(KryoNamespace.builder()
  .register(KryoNamespaces.BASIC)
  .register(MemberId.class)
  .register(ClusterHeartbeat.class)
  .build());

ClusterHeartbeat heartbeat = new ClusterHeartbeat(atomix.membershipService().getLocalMember().id());
atomix.messagingService().broadcast("test", heartbeat, serializer::encode);
```

{% include common-links.html %}
