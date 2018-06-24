---
layout: user-manual
project: atomix
menu: user-manual
title: Comparisons
---

While Atomix was influenced by various open source projects that came before it, is also aims to solve some of the limitations of those projects. This section discusses some of the comparisons of Atomix to similar open source projects and points out how Atomix differs from them.

## Hazelcast

Hazelcast was one of the most influential projects in shaping the direction of Atomix. Like Atomix, Hazelcast provides a set of primitives for replicating state and coordinating state changes in a distributed system. But unlike Atomix, Hazelcast's replication algorithms are not suitable for building partition tolerant systems. Atomix has always been built on the notion of strong consistency and correctness first and foremost. While Atomix does provide options for Hazelcast-style in-memory data grid replication (through primary-backup partition groups), it will never sacrifice the ability to provide strong consistency guarantees as an option. Indeed, Atomix will not even recommend that locks, leader elections, and other safety critical primitives be used without consensus.

## ZooKeeper

ZooKeeper is perhaps the most stable open source distributed system in existence and has been an extremely influential project for that reason. ZooKeeper is used in mission critical systems all over the world, and that's a testament to its reliability. What Atomix aims to provide above and beyond ZooKeeper is usability and customizability. ZooKeeper provides an API for managing a limited set of low-level primitives. Atomix, instead, provides much higher level primitives that are suited to specific use cases. For example, ZooKeeper provides watches which can be used to create a lock. Atomix instead provides a lock primitive specifically designed to suit distributed locking use cases. This allows for more complex atomic state changes in Atomix clusters without the need to use expensive coordination like optimistic and pessimistic locking.

Like Raft, ZooKeeper is also a leader-based system that's limited in terms of scalability. And while Atomix does use Raft for replication, it is able to scale writes using a so called Multi-Raft protocol in Raft partition groups, allowing Raft-based primitives to scale to multiple Raft leaders for better parallelism.

{% include common-links.html %}
