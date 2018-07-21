---
layout: user-manual
project: atomix
menu: user-manual
title: AtomicDocumentTree
---

The [`AtomicDocumentTree`][AtomicDocumentTree] primitive is a tree-like data structure with methods for performing atomic updates via optimistic locks. All operations on the `AtomicDocumentTree` are guaranteed to be atomic, and values in the tree are represented as [`Versioned`][Versioned] objects which associate a monotonically increasing `long` version number with each value. The version number can be used to perform atomic check-and-set operations using optimistic locking.

[`AtomicDocumentTree`][AtomicDocumentTree] supports event-based notifications of changes to the tree. Clients can listen for inserted/updated/removed entries by registering event listeners on an atomic tree.

Finally, [`AtomicDocumentTree`][AtomicDocumentTree] supports key set, values, and entry set views that are iterable and support Java 8 streams.

## Configuration

The [`AtomicDocumentTree`][AtomicDocumentTree] can be configured programmatically using the [`AtomicDocumentTreeBuilder`][AtomicDocumentTreeBuilder]. To create a new document tree builder, use the `atomicDocumentTreeBuilder` method, passing the name of the tree to construct:

```java
AtomicDocumentTreeBuilder<String> treeBuilder = atomix.<String>atomicDocumentTreeBuilder("my-tree");
```

The tree can be configured with a [protocol][primitive-protocols] to use to replicate changes. Since `AtomicDocumentTree` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

When using partitioned protocols like the ones above, the tree will be partitioned and replicated among all partitions in the configured [partition group][partition-groups].

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

AtomicDocumentTree<String> tree = atomix.<String>atomicDocumentTreeBuilder("my-tree")
  .withProtocol(protocol)
  .build();
```

The generic parameter in the tree configuration is the node value type. By default, arbitrary value types may be used. However, when non-standard types are used, class names will be serialized with tree entries, and the thread context class loader will be used to load classes from names. To avoid serializing class names, register a key and value type via `withValueType`. Class-based serialization can also be disabled via `withRegistrationRequired()`.

```java
AtomicDocumentTree<MemberId> tree = atomix.<MemberId>atomicDocumentTreeBuilder("my-tree")
  .withProtocol(protocol)
  .withValueType(MemberId.class)
  .build();
```

Atomic trees support caching. When caching is enabled, the tree will transparently listen for change events and update a local cache. To enable caching, use `withCacheEnabled()`:

```java
AtomicDocumentTree<String> tree = atomix.<String>atomicDocumentTreeBuilder("my-tree")
  .withProtocol(protocol)
  .withCacheEnabled()
  .withCacheSize(1000)
  .build();
```

A tree can also be constructed in read-only mode using `withReadOnly()`:

```java
AtomicDocumentTree<String> tree = atomix.<String>atomicDocumentTreeBuilder("my-tree")
  .withProtocol(protocol)
  .withReadOnly()
  .build();
```

Atomic trees can also be configured in configuration files. To configure an atomic tree primitive, use the `atomic-document-tree` primitive type:

`atomix.conf`

```hocon
primitives.my-tree {
  type: atomic-document-tree
  cache.enabled: true
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured tree, use the `getAtomicDocumentTree` method:

```java
AtomicDocumentTree<String> tree = atomix.getAtomicDocumentTree("my-tree");
```

The tree's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`AtomicDocumentTree`][AtomicDocumentTree] API is a tree-like structure which uses `DocumentPath`s to reference specific nodes in the tree. All operations performed on the tree are, as suggested by the name, guaranteed to be atomic. Beyond that atomicity guarantee, the consistency guarantees of read and write operations are specified by the configured protocol.

```java
AtomicDocumentTree<String> tree = atomix.<String>atomicDocumentTreeBuilder("my-tree")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();

tree.set(DocumentPath.from("foo|bar"), "baz");

Map<String, Versioned<V>> children = tree.getChildren(DocumentPath.from("foo"));
```

### Optimistic Locking

The tree values are represented as `Versioned` objects. The `Versioned` wrapper contains the entry `value()` and a unique, monotonically increasing, totally ordered `version()` number with each node which can be used to determine order among concurrent updates.

```java
// Get the current entry version
Versioned<String> value = tree.get(DocumentPath.from("foo|bar"));

// Update the node, using the version to acquire an optimistic lock
if (!tree.replace(DocumentPath.from("foo|bar"), "baz", value.version())) {
  System.out.println("Lock failed!");
}
```

When performing atomic operations using optimistic locking a `boolean` value will be returned. This boolean indicates whether the update was successful. If the node's version has changed since the read which produced the version number, an update will return `false`. Otherwise, if the node's version has not changed, the update will be successful and the tree will return `true`.

{:.callout .callout-warning}
Optimistic locking should be used conservatively. Trees that experience high lock contention can quickly overload a partition from optimistic lock retries.

### Asynchronous Operations

As with all Atomix primitives, an asynchronous analogue of the document tree API - [`AsyncAtomicDocumentTree`][AsyncAtomicDocumentTree] - can be retrieved by calling the `async()` method:

```java
AsyncAtomicDocumentTree<String> asyncTree = tree.async();

asyncTree.get(DocumentPath.from("foo|bar")).thenAccept(value -> {
  asyncTree.replace(DocumentPath.from("foo|bar"), "baz", value.version()).thenAccept(succeeded -> {
    System.out.println("Optimistic lock successful!");
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`.

### Event Notifications

[`AtomicDocumentTree`][AtomicDocumentTree] supports publishing event notifications to client listeners. This allows clients to react to insert, update, and remove operations on the tree. To add a listener to a tree, simply register the listener via `addListener`:

```java
tree.addListener(event -> {
  ...
});
```

Atomix guarantees that events will be received in the order in which they occurred inside replicated state machines, and event listeners will be called on an Atomix event thread. Users can optionally provide a custom executor on which to call the event listener:

```java
Executor executor = Executors.newSingleThreadExecutor();
tree.addListener(event -> {
  ...
}, executor);
```

{:.callout .callout-warning}
Custom executors can change the ordering of events. It's recommended that single thread executors be used to preserve order. Multi-threaded executors cannot provide the same guarantees as are provided by Atomix event threads or single thread executors.

The event listener will be called with an [`DocumentTreeEvent`][DocumentTreeEvent] instance. Each event in Atomix has an associated type which can be read via the `type()` method. To determine the type of modification that took place, use a switch statement:

```java
switch (event.type()) {
  case CREATED:
    ...
    break;
  case UPDATED:
    ...
    break;
  case DELETED:
    ...
    break;
}
```

The [`DocumentTreeEvent`][DocumentTreeEvent] provides both the previous value and the updated value for all updates. The previous value can be read via `oldValue()` and the updated value via `newValue()`. Additionally, values are contained in `Versioned` wrappers to facilitate further updates to the tree.

```java
Versioned<String> value;
if (event.type() == DocumentTreeEvent.Type.DELETED) {
  value = event.oldValue().get();
} else {
  value = event.newValue().get();
}
```

The Atomix thread model allows for event listeners to make blocking calls on primitives within event threads. So, in response to an update event, an event listener can e.g. call `put` on the same tree:

```java
// Recreate nodes that are removed from the tree
tree.addListener(event -> {
  if (event.type() == DocumentTreeEvent.Type.DELETED) {
    tree.put(event.key(), event.newValue().get().value());
  }
});
```

When performing blocking operations (any operation on a synchronous primitive) within an event threads, additional events and futures will be completed on a background thread pool. This means ordering guarantees are inherently relaxed when event threads are blocked.

## Cleanup

While a tree is in use, Atomix may consume some network, memory, and disk resources to manage the tree. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
tree.close();
```

{% include common-links.html %}
