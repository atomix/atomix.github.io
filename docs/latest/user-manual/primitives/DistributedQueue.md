---
layout: user-manual
project: atomix
menu: user-manual
title: DistributedQueue
---

The [`DistributedQueue`][DistributedQueue] primitive is an implementation of Java's [`Queue`][Queue] collection.

[`DistributedQueue`][DistributedQueue] is an extension of [`DistributedCollection`][DistributedCollection] and supports event-based notifications of changes to the queue. Clients can listen for add/remove events by registering event listeners on a distributed queue.

Finally, [`DistributedQueue`][DistributedQueue] supports lazy iteration and Java 8's [`Stream`][Stream]s.

## Configuration

The [`DistributedQueue`][DistributedQueue] can be configured programmatically using the [`DistributedQueueBuilder`][DistributedQueueBuilder]. To create a new queue builder, use the `queueBuilder` method, passing the name of the queue to construct:

```java
DistributedQueueBuilder<String> queueBuilder = atomix.<String>queueBuilder("my-queue");
```

The queue can be configured with a [protocol][primitive-protocols] to use to replicate changes. Since `DistributedQueue` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Because distributed queues are ordered, when using partitioned protocols like the ones above, the queue will be mapped to a single partition in the configured [partition group][partition-groups].

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

Queue<String> queue = atomix.<String>queueBuilder("my-queue")
  .withProtocol(protocol)
  .build();
```

The generic parameter in the value configuration is the element type. By default, arbitrary element types may be used. However, when non-standard types are used, class names will be serialized with elements, and the thread context class loader will be used to load classes from names. To avoid serializing class names, register an element type via `withElementType`. Class-based serialization can also be disabled via `withRegistrationRequired()`.

```java
Queue<Foo> queue = atomix.<Foo>queueBuilder("my-queue")
  .withProtocol(protocol)
  .withElementType(Foo.class)
  .build();
```

Queues support caching. When caching is enabled, the queue will transparently listen for change events and update a local cache. To enable caching, use `withCacheEnabled()`:

```java
Queue<String> queue = atomix.<String>queueBuilder("my-queue")
  .withProtocol(protocol)
  .withCacheEnabled()
  .withCacheSize(1000)
  .build();
```

A queue can also be constructed in read-only mode using `withReadOnly()`:

```java
Queue<String> queue = atomix.<String>queueBuilder("my-queue")
  .withProtocol(protocol)
  .withReadOnly()
  .build();
```

Queues can be configured in configuration files. To configure an queue primitive, use the `queue` primitive type:

`atomix.conf`

```hocon
primitives.my-queue {
  type: queue
  cache.enabled: true
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured queue, use the `getQueue` method:

```java
Queue<String> queue = atomix.getQueue("my-queue");
```

The queue's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`DistributedQueue`][DistributedQueue] supports most of the same operations as Java's core `Queue`. All operations performed on the queue are guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
Queue<String> queue = atomix.<String>queueBuilder("my-queue")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

queue.offer("foo");
queue.offer("bar");

String next = queue.poll();
while (next != null) {
  ...
}
```

### Asynchronous Operations

As with all Atomix primitives, an asynchronous analogue of the queue API - [`AsyncDistributedQueue`][AsyncDistributedQueue] - can be retrieved by calling the `async()` method:

```java
// Get a synchronous DistributedQueue
DistributedQueue<String> queue = atomix.getQueue("my-queue");

// Get the underlying asynchronous DistributedQueue
AsyncDistributedQueue<String> asyncQueue = queue.async();

asyncQueue.add("foo").thenRun(() -> {
  asyncQueue.get(0).thenAccept(value -> {
    ...
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

### Event Notifications

[`DistributedQueue`][DistributedQueue] supports publishing event notifications to client listeners. This allows clients to react to insert, update, and remove operations on the queue. To add a listener to a queue, simply register the listener via `addListener`:

```java
queue.addListener(event -> {
  ...
});
```

Atomix guarantees that events will be received in the order in which they occurred inside replicated state machines, and event listeners will be called on an Atomix event thread. Users can optionally provide a custom executor on which to call the event listener:

```java
Executor executor = Executors.newSingleThreadExecutor();
queue.addListener(event -> {
  ...
}, executor);
```

{:.callout .callout-warning}
Custom executors can change the ordering of events. It's recommended that single thread executors be used to preserve order. Multi-threaded executors cannot provide the same guarantees as are provided by Atomix event threads or single thread executors.

The event listener will be called with an [`DistributedCollectionEvent`][DistributedCollectionEvent] instance. Each event in Atomix has an associated type which can be read via the `type()` method. To determine the type of modification that took place, use a switch statement:

```java
switch (event.type()) {
  case ADD:
    ...
    break;
  case REMOVE:
    ...
    break;
}
```

The [`DistributedCollectionEvent`][DistributedCollectionEvent] provides the added/removed element.

```java
String value = event.element();
```

The Atomix thread model allows for event listeners to make blocking calls on primitives within event threads. So, in response to an update event, an event listener can e.g. call `offer` on the same queue:

```java
// re-add entries that are removed from the queue
queue.addListener(event -> {
  if (event.type() == DistributedCollectionEvent.Type.REMOVE) {
    queue.offer(event.element());
  }
});
```

When performing blocking operations (any operation on a synchronous primitive) within an event threads, additional events and futures will be completed on a background thread pool. This means ordering guarantees are inherently relaxed when event threads are blocked.

### Iterators

[`DistributedQueue`][DistributedQueue] supports lazy iterators:

```java
for (String value : queue) {
  ...
}
```

Iterators are implemented by lazily fetching batches of queue elements from the partition as the elements are iterated. Once a primitive iterator has been created, it must either be exhausted or explicitly `close()`d to ensure the resources used to track the iterator state is cleaned up.

```java
Iterator<String> iterator = queue.iterator();

try {
  String value = iterator.next();
} finally {
  iterator.close();
}
```

{:.callout .callout-warning}
Failing to exhaust or explicitly close frequently created primitive iterators may cause a memory leak.

Just as with typical synchronous primitives, the iterators provided for Atomix primitives are backed by an asynchronous implementation called [`AsyncIterator`][AsyncIterator], and the asynchronous backing iterator can be retrieved via the `async()` method:

```java
AsyncIterator<String> asyncIterator = queue.async().iterator();
```

### Streams

The implementation of lazy iterators also allows the queue to support Java 8 [`Stream`][Stream]s:

```java
Set<String> fooValues = queue.stream()
  .filter(value -> value.contains("foo"))
  .collect(Collectors.toSet());
```

## Cleanup

While a queue is in use, Atomix may consume some network, memory, and disk resources to manage the queue. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
queue.close();
```

{% include common-links.html %}
