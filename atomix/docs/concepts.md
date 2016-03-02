---
layout: docs
project: atomix
menu: docs
title: Concepts
---

{:.no-margin-top}
Atomix is built around several fundamental concepts that are worth learning about in order to fully utilize its capabilities.

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

## Fault-tolerance

Because Atomix falls on the CP side of the CAP theorem, it favors consistency over availability, particularly under failure. In order to ensure consistency, Atomix's [consensus protocol][raft-framework] requires that a majority of the cluster be alive and operating normally to service reads and writes. This means:

* A cluster of `1` replica can tolerate `0` failures
* A cluster of `2` replicas can tolerate `0` failures
* A cluster of `3` replicas can tolerate `1` failure
* A cluster of `4` replicas can tolerate `1` failure
* A cluster of `5` replicas can tolerate `2` failures

Failures in Atomix are handled by Raft's [leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm. When the Atomix cluster starts, a leader is elected. Leaders are elected by a round of voting wherein servers vote for a candidate based on the [consistency of its log](#consistency-model).

In the event of a failure of the leader, the remaining servers in the cluster will begin a new election and a new leader will be elected. This means for a brief period (seconds) the cluster will be unavailable.

In the event of a partition, if the leader is on a quorum side of the partition, it will continue to operate normally. Alternatively, if the leader is on a non-quorum side of the partition, the leader will detect the partition (based on the fact that it can no longer contact a majority of the cluster) and step down, and the servers on the majority side of the partition will elect a new leader. Once the partition is resolved, nodes on the non-quorum side of the partition will join the quorum side and receive updates to their log from the remaining leader.

## Threading model

Atomix is designed to be used in an asynchronous manner that provides easily understood guarantees for users. All usage of asynchronous APIs such as [CompletableFuture] are carefully orchestrated to ensure that various callbacks are executed in a deterministic manner. To that end, Atomix provides the following guarantees:

* Callbacks for any given object are guaranteed to always be executed on the same thread
* `CompletableFuture`s are guaranteed to be completed in the same order in which they were created

### Asynchronous API usage

Atomix's API makes heavy use of Java 8's [CompletableFuture][CompletableFuture] for asynchronous completion of method calls. The asynchronous API allows users to execute multiple operations concurrently instead of blocking on each operation in sequence. For information on the usage of `CompletableFuture` see the [CompletableFuture documentation][CompletableFuture].

### Synchronous API usage

Atomix makes heavy use of Java 8's [CompletableFuture][CompletableFuture] in part because it allows users to easily block on asynchronous method calls. To block and wait for a `CompletableFuture` result instead of registering an asynchronous callback, simply use the `get()` or `join()` methods.

```java
// Get the "foo" key from a map
CompletableFuture<String> future = map.get("foo");

// Block to wait for the result
String result = future.get();
```

{% include common-links.html %}