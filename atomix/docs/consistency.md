---
layout: docs
project: atomix
menu: docs
title: Consistency
---

{:.no-margin-top}
Consistency and how it is achieved is a fundamental concept in Atomix. This page describe's Atomix's consistency model and where it fits among other systems.

## CAP theorem

The [CAP theorem][CAP] is frequently cited in discussion of distributed systems as a way of classifying the behavior of a system according to how it deals with **C**onsistency, **A**vailability, and **P**artition tolerance. Since the CAP theorem states that only 2 out of 3 can be achieved, and since partition tolerance is usually a necessity, systems are left to choose between consistency and availability, or some degree of each, in the event of a partition.

High-throughput, high-availability distributed databases like [Hazelcast], [Cassandra] and other Dynamo-based systems fall under the *A* and *P* in the CAP theorem. That is, these systems generally sacrifice consistency in favor of availability during network partitions. In AP systems, a network partition can result in temporary or even permanent loss of writes. Additionally, AP systems may allow conflicting data values which must be resolved. These systems are generally designed to store and query large amounts of data quickly.

Alternatively, systems like [ZooKeeper] and Atomix, which fall under the *C* and *P* in the CAP theorem, are generally designed to store small amounts of mission critical data. CP systems provide strong consistency guarantees like [linearizability][Linearizability] and [sequential consistency][SequentialConsistency] even in the face of failures. But that level of consistency comes at a cost: availability. CP systems like ZooKeeper and Atomix are consensus-based and require a quorum to operate, so they can only tolerate the loss of a minority of servers. 

{:.callout .callout-info}
Fortunately, Atomix provides support for passive and standby replicas to minimize the risk  of losing availability in the case of a node loss.

## Consistency model

In terms of the CAP theorem, Atomix falls squarely in the CP range. That means Atomix provides configurable strong consistency levels: [linearizability][Linearizability] for both reads, writes, and other events, and optional weaker [sequential consistency][SequentialConsistency] or [causal consistency][CausalConsistency] for certain operations. Linearizability says that all operations must take place some time between their invocation and completion. This means that once a write is committed to a Atomix cluster, all clients are guaranteed to see the resulting state.

Consistency is guaranteed by [Atomix's implementation of the Raft consensus algorithm][raft-framework]. Raft uses a [distributed leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm to elect a leader. The leader election algorithm guarantees that the server that is elected leader will have all the writes to the cluster that have previously been successful. All writes go through the cluster leader and are *synchronously replicated to a majority of servers* before completion. Additionally, writes are sequenced in the order in which they're submitted by the client (sequential consistency).

Unlike [ZooKeeper], Atomix natively supports linearizable reads as well. Much like writes, linearizable reads must go through the cluster leader (which always has the most recent cluster state) and may require contact with a majority of the cluster. For higher throughput, Atomix also allows reads from followers. Reads from followers guarantee *sequential consistency* or *causal consistency*, depending on the configuration, meaning all clients will see state changes in the same order but different clients may see different views of the state at any given time. Notably, *a client's view of the cluster will never go back in time* even when switching between servers. Additionally, Atomix places a bound on followers servicing reads: in order to service a read, a follower's log must be less than a heartbeat behind the leader's log.

{:.callout .callout-info}
See the [Raft implementation details](/copycat/docs/internals/) for more information on consistency in Atomix.

{% include common-links.html %}