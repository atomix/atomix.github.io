---
layout: docs
project: atomix
menu: docs
title: Threading Model
---

{:.no-margin-top}
Atomix is designed to be used in an asynchronous manner that provides easily understood guarantees for users. All usage of asynchronous APIs such as [CompletableFuture] are carefully orchestrated to ensure that various callbacks are executed in a deterministic manner.

All Atomix APIs that interact with remote clusters will return a [`CompletableFuture`][CompletableFuture] object. Futures allow client code to operate either synchronously or asynchronously. When `get()` or `join()` is called on a [`CompletableFuture`][CompletableFuture], the calling thread will be blocked until the future is completed. When completion callbacks are used, Atomix guarantees that all operations will be completed in the client's event thread and that all clients will see operations occur in the same order on that thread.

Certain operations may result in events being published from the cluster to clients. For instance, when a member joins a [`DistributedGroup`][DistributedGroup], a join event is published to each open instance of the group on every client. As with operation responses, events will occur in the client's event thread. Events are guaranteed to be sequentially consistent and to occur at the same time as the command that triggers them. For example, if a client joins a [`DistributedGroup`][DistributedGroup], the [`CompletableFuture`][CompletableFuture] returned by the `join()` method call will be completed, followed by an `onJoin` event being received by the client. All other clients with an open instance of the same [`DistributedGroup`][DistributedGroup] will see the same join event at the same logical time.

In certain cases, client code may want to block in the event thread. Because all operations and events are completed in the same thread, blocking the event thread can result in a deadlock wherein the blocked future cannot be completed because it's blocking the event thread. In order to account for deadlocks, Atomix monitors response futures for blocking operations. If client code blocks a response future, Atomix will complete the blocked future in a separate thread. This allows clients to block inside operation or event callbacks.

Given Atomix threading model, the following sequence of operations is valid:

```java
map.put("foo", "Hello world!").thenRun(() -> {
  String value = map.get("foo").join();
});
```

{% include common-links.html %}