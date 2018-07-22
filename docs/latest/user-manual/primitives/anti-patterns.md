---
layout: user-manual
project: atomix
menu: user-manual
title: Anti-patterns
---

Atomix distributed primitives have been in use in the [ONOS](http://onosproject.org) project for years. During that time, Atomix engineers have learned some anti-patterns to help ensure systems built on Atomix remain scalable and performant.

## Use partitioned primitives

Some distributed primitives can be partitioned while others can't. Partitions are the primary mechanism by which Atomix primitives can scale both capacity and throughput. If data cannot be partitioned then it inevitably cannot scale well. Consider relying only on partitioned primitives or create multiple distinctly named primitives to scale across all partitions. If a primitive cannot be partitioned, consider whether writing a custom primitive would help.

## Avoid locking

Many distributed applications rely on distributed locking for controlling concurrent access to a shared resource. But locks are extremely costly. They require significant amounts of coordination. Instead, consider whether the same level of access control can be used to elect a longer running leader through which changes can be proxied via the `ClusterCommunicationService`.

The `DistributedLock` primitive provides a pessimistic lock, but optimistic locking - e.g. in a `AtomicMap#replace` call - can be just as problematic for scalability. Optimistic locking can result in a significant increase in network traffic at times of high contention. Consider falling back to a pessimistic lock when an optimistic lock fails, or better yet build a primitive that avoids distributed locks altogether.

It's also important to note that the optimistic locking rule applies also to `AtomicMap#compute` and similar methods. These methods use optimistic locking internally to ensure a map is updated atomically after applying the compute function locally. Sometimes compute methods can be avoided with more complex data structures like a `AtomicMultimap`.

## Never poll primitives

Atomix goes to great lengths to avoid unnecessary network traffic, and one of the ways it does so is by providing event-based notifications of changes to primitives. Always use event listeners to receive notifications of changes to primitives, and consider using the `ClusterEventService` for notifications of events outside of primitives.

{% include common-links.html %}
