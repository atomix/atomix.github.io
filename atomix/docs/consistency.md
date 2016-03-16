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

In terms of the CAP theorem, Atomix falls squarely in the CP range. That means Atomix provides configurable strong consistency levels: [linearizability][Linearizability] for both reads, writes, and other events, and optional weaker [sequential consistency][SequentialConsistency] or [causal consistency][CausalConsistency] for certain operations. Linearizability says that all operations must take place some time between their invocation and completion. This means that once a write is committed to a Atomix cluster, all clients are guaranteed to see the resulting state.

Consistency is guaranteed by [Atomix's implementation of the Raft consensus algorithm][copycat-internals]. Raft uses a [distributed leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm to elect a leader. The leader election algorithm guarantees that the server that is elected leader will have all the writes to the cluster that have previously been successful. All writes go through the cluster leader and are *synchronously replicated to a majority of servers* before completion. Additionally, writes are sequenced in the order in which they're submitted by the client, ensuring sequential consistency.

Unlike [ZooKeeper], Atomix natively supports linearizable reads as well. Much like writes, linearizable reads must go through the cluster leader (which always has the most recent cluster state) and may require contact with a majority of the cluster. For higher throughput, Atomix also allows reads from followers. Reads from followers guarantee *sequential consistency* or *causal consistency*, depending on the configuration, meaning all clients will see state changes in the same order but different clients may see different views of the state at any given time. Notably, *a client's view of the cluster will never go back in time* even when switching between servers. Additionally, Atomix places a bound on followers servicing reads: in order to service a read, a follower's log must be less than a heartbeat behind the leader's log.

{:.callout .callout-info}
See the Copycat [Raft internals](/copycat/docs/internals/) documentation for an in depth look at consistency in Atomix.

## Consistency Levels

Atomix provides different consistency levels for controlling the behavior of read and write operations:

#### Write Consistency Levels

* `WriteConsistency.ATOMIC` - Guarantees atomicity ([linearizability]) for write operations and events. Atomic write consistency enforces sequential consistency for concurrent commands from a single client by sequencing commands as they're applied to the Raft state machine. If a client submits writes a, b, and c in that order, they're guaranteed to be applied to the Raft state machine and client futures are guaranteed to be completed in that order. Additionally, linearizable commands are guaranteed to be applied to the server state machine some time between invocation and response, and command-related session events are guaranteed to be received by clients prior to completion of the command.
* `WriteConsistency.SEQUENTIAL_EVENT` - Guarantees atomicity ([linearizability]) for write operations and sequential consistency for events triggered by a command. All commands are applied to the server state machine in program order and at some point between their invocation and response (linearization point). But session events related to commands can be controlled by this consistency level. The sequential consistency level guarantees that all session events related to a command will be received by the client in sequential order. However, it does not guarantee that the events will be received during the invocation of the command.

#### Read Consistency Levels

* `ReadConsistency.ATOMIC` - Guarantees atomicity ([linearizability]) for read operations. The atomic consistency level guarantees linearizability by contacting a majority of the cluster on every read. When a Query is submitted to the cluster with linearizable consistency, it must be forwarded to the current cluster leader. Once received by the leader, the leader will contact a majority of the cluster before applying the query to its state machine and returning the result. Note that if the leader is already in the process of contacting a majority of the cluster, it will queue the Query to be processed on the next round trip. This allows the leader to batch expensive quorum based reads for efficiency.
* `ReadConsistency.ATOMIC_LEASE` - Guarantees atomicity ([linearizability]) for read operations. The atomic consistency level guarantees linearizablearizability by contacting a majority of the cluster on every read. When a Query is submitted to the cluster with linearizable consistency, it must be forwarded to the current cluster leader. Once received by the leader, the leader will contact a majority of the cluster before applying the query to its state machine and returning the result. Note that if the leader is already in the process of contacting a majority of the cluster, it will queue the Query to be processed on the next round trip. This allows the leader to batch expensive quorum based reads for efficiency.
* `ReadConsistency.SEQUENTIAL` - Guarantees sequential consistency for read operations. Sequential read consistency requires that clients always see state progress in monotonically increasing order. Note that this constraint allows reads from followers. When a sequential Query is submitted to the cluster, the first server that receives the query will handle it. However, in order to ensure that state does not go back in time, the client must submit its last known index with the query as well. If the server that receives the query has not advanced past the provided client index, it will queue the query and await more entries from the leader.
* `ReadConsistency.CAUSAL` - Guarantees causal consistency for read operations. Causal consistency requires that clients always see non-overlapping state progress monotonically. This constraint allows reads from followers. When a causally consistent Query is submitted to the cluster, the first server that receives the query will attempt to handle it. If the server that receives the query is more than a heartbeat behind the leader, the query will be forwarded to the leader. If the server that receives the query has not advanced past the client's last write, the read will be queued until it can be satisfied.

Overloaded methods with consistency parameters are provided throughout Atomix's resources wherever it makes sense. In many cases, resources dictate the strongest consistency levels - e.g. [concurrent][concurrency] - and so weaker consistency levels are not allowed.

### Configuring Consistency

To configure the [ReadConsistency] or [WriteConsistency] for a resource, use the `with` method:

```java
DistributedLock lock = atomix.getLock("my-lock").get();

lock.with(WriteConsistency.ATOMIC).lock().thenRun(() -> System.out.println("Lock acquired!"));
```

{% include common-links.html %}