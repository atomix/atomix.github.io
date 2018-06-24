---
layout: user-manual
project: atomix
menu: user-manual
title: Distributed Primitives
---

Distributed primitives are at the core of how Atomix replicates state and coordinates state changes in distributed systems. Distributed primitives are high-level abstractions for solving common distributed systems problems. The primitive interfaces are designed to mimic core Java collections and `java.util.concurrent` APIs wherever possible.

Each Atomix primitive is identified by a `String` name. The name can be used to reference the same state on multiple nodes within an Atomix cluster:

```java
DistributedSet<String> set = atomix.getSet("my-set");
set.add("foo");
```

Additionally, both synchronous and asynchronous (non-blocking) interfaces are provided for every primitive.

```java
AsyncDistributedSet<String> asyncSet = atomix.getSet("my-set").async();
asyncSet.add("foo").thenRun(() -> {
  ...
});
```

When operations are performed on the set, Atomix transparently replicates changes using the configured replication protocol such that the failure of a node will not result in the loss of state. One instance can see changes from another instance just by creating an instance of the same primitive with the same name:

```java
DistributedSet<String> set = atomix.getSet("my-set");
if (set.contains("foo")) {
  ...
}
```

{% include common-links.html %}
