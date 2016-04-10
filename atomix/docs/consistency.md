---
layout: docs
project: atomix
menu: docs
title: Consistency
---

{:.no-margin-top}
Consistency and how it is achieved is a fundamental concept in Atomix. This page describes Atomix's consistency model, how it compares to other systems, and how it is used.

## CAP Theorem

The [CAP theorem][CAP] is frequently cited in discussion of distributed systems as a way of classifying the behavior of a system according to how it deals with ***C**onsistency*, ***A**vailability*, and ***P**artition-tolerance*. Since the CAP theorem states that only 2 out of 3 can be achieved, and since partition tolerance is usually a necessity, systems are left to choose between consistency and availability, or some degree of each, in the event of a partition.

High-throughput, high-availability distributed databases like [Hazelcast], [Cassandra] and other [Dynamo] based systems fall under the *A* and *P* in the CAP theorem. That is, these systems generally sacrifice consistency in favor of availability during network partitions. In AP systems, a network partition can result in temporary or even permanent loss of writes. Additionally, AP systems may allow conflicting data values to be written. These systems are generally designed to store and query large amounts of data quickly.

Alternatively, systems like [ZooKeeper] and Atomix, which fall under the *C* and *P* in the CAP theorem, are generally designed to store small amounts of mission critical data. CP systems provide strong consistency guarantees like [linearizability][Linearizability] and [sequential consistency][SequentialConsistency] even in the face of failures. But that level of consistency comes at a cost: availability. CP systems like ZooKeeper and Atomix are consensus-based and require a quorum to operate, so they can only tolerate the loss of a minority of servers.

{:.callout .callout-info}
Fortunately, Atomix provides support for [passive and standby][node-types] replicas to minimize the risk  of losing availability in the case of a node loss.

## Consistency Model

In terms of the CAP theorem, Atomix falls squarely in the CP range. That means Atomix provides configurable strong consistency levels: [linearizability][Linearizability] for both reads and writes and optional weaker [sequential consistency][SequentialConsistency] for reads operations and events. Linearizability says an operation must take place some time between its invocation and completion. This means that once a write is committed to a Atomix cluster, all clients are guaranteed to see the resulting state.

Consistency is guaranteed by [Atomix's implementation of the Raft consensus algorithm][copycat-internals]. Raft uses a [distributed leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm to elect a leader. The leader election algorithm guarantees that the server that is elected leader will have all the writes to the cluster that have previously been successful. All writes go through the cluster leader and are *synchronously replicated to a majority of servers* before completion. Additionally, writes are sequenced in the order in which they're submitted by the client, ensuring sequential consistency.

Unlike [ZooKeeper], Atomix natively supports linearizable reads as well. Much like writes, linearizable reads must go through the cluster leader (which always has the most recent cluster state) and may require contact with a majority of the cluster. For higher throughput, Atomix also allows reads from followers. Reads from followers guarantee *sequential consistency* or *causal consistency*, depending on the configuration, meaning all clients will see state changes in the same order but different clients may see different views of the state at any given time. Notably, *a client's view of the cluster will never go back in time* even when switching between servers. Additionally, Atomix places a bound on followers servicing reads: in order to service a read, a follower's log must be less than a heartbeat behind the leader's log.

{:.callout .callout-info}
See the Copycat [Raft internals](/copycat/docs/internals/) documentation for an in depth look at consistency in Atomix.

## Consistency Levels

Atomix supports per-operation configurable read consistency levels. This allows clients to choose guarantees for read operations based on performances and consistency requirements.

* `ReadConsistency.ATOMIC` - Guarantees atomicity ([linearizability]) for read operations. The atomic consistency level guarantees linearizability by contacting a majority of the cluster on every read. When a Query is submitted to the cluster with linearizable consistency, it must be forwarded to the current cluster leader. Once received by the leader, the leader will contact a majority of the cluster before applying the query to its state machine and returning the result. Note that if the leader is already in the process of contacting a majority of the cluster, it will queue the Query to be processed on the next round trip. This allows the leader to batch expensive quorum based reads for efficiency.
* `ReadConsistency.ATOMIC_LEASE` - Guarantees atomicity ([linearizability]) for read operations. The atomic consistency level guarantees linearizablearizability by contacting a majority of the cluster on every read. When a Query is submitted to the cluster with linearizable consistency, it must be forwarded to the current cluster leader. Once received by the leader, the leader will contact a majority of the cluster before applying the query to its state machine and returning the result. Note that if the leader is already in the process of contacting a majority of the cluster, it will queue the Query to be processed on the next round trip. This allows the leader to batch expensive quorum based reads for efficiency.
* `ReadConsistency.SEQUENTIAL` - Guarantees sequential consistency for read operations. Sequential read consistency requires that clients always see state progress in monotonically increasing order. Note that this constraint allows reads from followers and passive replicas. When a sequential query is submitted to the cluster, the first server that receives the query will handle it. Atomix ensures that clients will never see state go back in time even when switching servers.

Overloaded methods with consistency parameters are provided throughout Atomix's resources wherever it makes sense. In many cases, resources dictate the strongest consistency levels - e.g. [concurrent][concurrency] - and so weaker consistency levels are not allowed.

```java
map.get("foo", ReadConsistency.SEQUENTIAL).get();
```

## Event Consistency

Certain resource operations may result in events being published by the cluster to resource instances. For instance, when a client `join`s a [`DistributedGroup`][DistributedGroup], the group publishes a join event to each open instance of the group. Events are published to clients by the server to which the client is connected. If a client is connected to a follower, the join event will be published once the follower receives the join commit. If a resource was created on a stateful replica, the events will be published as state changes are received by the replica. Atomix guarantees that all clients will see operations and events occur in the same order they occur in the replicated state machine. If a client performs a write operation that triggers an event to all sessions, all clients will first see the write operation complete and then receive the event. If a read operation occurs concurrently with a write and event, the read operation will always occur after a write operation and event at the same logical time.

## Cross-resource Consistency

All resources and their operations and events share a single Copycat session. Therefore, the consistency guarantees described above apply to multiple resource instances in use by a client. If a client creates two separate [`DistributedMap`][DistributedMap] objects and calls `put` on one map before calling `get` on the other, the `put` operation on the first map is guaranteed to occur before the `get` operation on the latter map.

{% include common-links.html %}