---
layout: docs
project: atomix
menu: docs
title: Distributed Resources
pitch: Common abstractions for distributed coordination
first-section: what-are-resources
---

The true power of Atomix comes from [Resource] implementations. Resources are named distributed objects that are replicated and persisted in the Atomix cluster. Each name can be associated with a single resource, and each resource is backed by a replicated state machine managed by Atomix's underlying [implementation of the Raft consensus protocol](/copycat/docs/internals).

Resources are created by simply using one of `Atomix`'s `get` methods or passing a custom `Resource` class to `get`:

```java
DistributedMap<String, String> map = atomix.getMap("my-map").get();
```

Atomix create a replicated [StateMachine][StateMachine] on each replica in the cluster. Operations performed on the resource are submitted as state changes to the cluster where they're replicated and persisted before being applied to the replicated state machine.

Atomix provides a number of resource implementations for common distributed systems problems. Currently, the provided resources are divided into three subsets that are represented as Maven submodules:

* [Distributed collections](#distributed-collections) - `DistributedSet`, `DistributedMap`, `DistributedMultiMap`, `DistributedQueue`
* [Distributed atomic variables](#distributed-variables) - `DistributedValue`, `DistributedLong`
* [Distributed coordination tools](#distributed-coordination) - `DistributedLock`, `DistributedGroup`
* [Distributed messaging](#distributed-messaging) - `DistributedTopic`, `DistributedMessageBus`

{% include common-links.html %}