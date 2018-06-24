---
layout: user-manual
project: atomix
menu: user-manual
title: Publish-Subscribe Messaging
---

Publish-subscribe messaging is done using the [`ClusterEventService`][ClusterEventService] API, which is closely modelled on the [`ClusterCommunicationService`][ClusterCommunicationService] API. Indeed, while the two appear to be almost the exact same, their semantics differ significantly. Rather than sending messages to specific nodes using [`MemberId`][MemberId]s, the `ClusterEventService` actually replicates subscriber information and routes messages internally. Point-to-point messages sent via the `ClusterEventService` are delivered in a round-robin fashion, and multicast messages do not require any specific node information. This decouples receivers from senders.

```java
// Add an event service subscriber
atomix.getEventService().subscribe("test", message -> {
  return CompletableFuture.completedFuture(message);
});

// Send a request-reply message via the event service
atomix.getEventService().send("test", "Hello world!").thenAccept(response -> {
  System.out.println("Received " + response);
});

// Broadcast a message to all event subscribers
atomix.getEventService().broadcast("test", "Hello world!");
```

{% include common-links.html %}
