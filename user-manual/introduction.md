---
layout: content
menu: user-manual
title: Introduction
---

Copycat is a framework for consistent distributed coordination. At the core of Copycat is a generic implementation of the [Raft consensus algorithm][Raft]. On top of Raft, Copycat provides a high level API for creating and managing arbitrary user-defined replicated state machines such as maps, sets, locks, or user-defined resources. Resources can be created and modified by any replica or client in the cluster.

Copycat clusters consist of at least one (but usually 3 or 5) [replica] and any number of [clients][client]. *Replicas* are stateful nodes that actively participate in the Raft consensus protocol, and *clients* are stateless nodes that modify system state remotely. When a cluster is started, the replicas in the cluster coordinate with one another to elect a leader.

![Copycat cluster](http://s24.postimg.org/3jrc7yuad/IMG_0007.png)

Once a leader has been elected, clients connect to a random server in the cluster, create resources (e.g. maps, sets, locks, etc) and submit commands (writes) and queries (reads). All commands are proxied to the cluster leader. When the leader receives a command, it persists the write to [disk]({{ site.baseurl }}/user-manual/io-serialization#storage) and replicates it to the rest of the cluster. Once a command has been received and persisted on a majority of replicas, the state change is committed and guaranteed not to be lost.

Because the Copycat cluster is dependent on a majority of the cluster being reachable to commit writes, the cluster can tolerate a minority of the nodes failing. For this reason, it is recommended that each Copycat cluster have at least 3 or 5 replicas, and the number of replicas should always be odd in order to achieve the greatest level of fault-tolerance. The number of replicas should be calculated as `2f + 1` where `f` is the number of failures to tolerate.

**So what's the difference between Copycat and those other projects?**

[ZooKeeper](https://zookeeper.apache.org/) - Copycat and ZooKeeper are both backed by a similar consensus-based persistence/replication layer. But Copycat is a framework that can be embedded instead of depending on an external cluster. Additionally, ZooKeeper's low-level primitives require complex recipes or other tools like [Apache Curator](http://curator.apache.org/), whereas Copycat provides [high-level interfaces]({{ site.baseurl }}/user-manual/distributed-resources#resources) for common data structures and coordination tools like [locks]({{ site.baseurl }}/user-manual/distributed-resources#distributedlock), [maps]({{ site.baseurl }}/user-manual/distributed-resources#distributedmap), and [leader elections]({{ site.baseurl }}/user-manual/distributed-resources#distributedleaderelection), or the option to create [custom replicated state machines]({{ site.baseurl }}/user-manual/distributed-resources#custom-resources).

[Hazelcast] - Hazelcast is a fast, in-memory data grid that, like Copycat, exposes rich APIs for operating on distributed object But whereas Hazelcast chooses [availability over consistency in the face of a partition](https://en.wikipedia.org/wiki/CAP_theorem), Copycat is designed to ensure that data is never lost in the event of a network partition or other failure. Like ZooKeeper, this requires that Copycat synchronously replicate all writes to a majority of the cluster and persist writes to disk, much like ZooKeeper.

## The CAP theorem

[The CAP theorem][CAP] is a frequently referenced theorem that states that it is impossible for a distributed system to simultaneously provide **C**onsistency, **A**vailability, and **P**artition tolerance. All distributed systems must necessarily sacrifice either consistency or availability, or some degree of each, in the event of a partition.

High-throughput, high-availability distributed databases like [Hazelcast] or [Cassandra] and other Dynamo-based systems fall under the *A* and *P* in the CAP theorem. That is, these systems generally sacrifice consistency in favor of availability during network partitions. In AP systems, a network partition can result in temporary or even permanent loss of writes. These systems are generally designed to store and query large amounts of data quickly.

Alternatively, systems like [ZooKeeper] and Copycat, which fall under the *C* and *P* in the CAP theorem, are generally designed to store small amounts of mission critical state. CP systems provide strong consistency guarantees like [linearizability](https://en.wikipedia.org/wiki/Linearizability) and [sequential consistency](https://en.wikipedia.org/wiki/Sequential_consistency) even in the face of failures, but that level of consistency comes at a cost: availability. CP systems like ZooKeeper and Copycat are consensus-based and require a quorum to operate, so they can only tolerate the loss of a minority of servers.

## Consistency model

In terms of the CAP theorem, Copycat falls squarely in the CP range. That means Copycat provides configurable strong consistency levels - [linearizability](https://en.wikipedia.org/wiki/Linearizability) for writes and reads, and optional weaker [serializability](https://en.wikipedia.org/wiki/Serializability) for reads - for all operations. Linearizability says that all operations must take place some time between their invocation and completion. This means that once a write is committed to a Copycat cluster, all clients are guaranteed to see the resulting state.

Consistency is guaranteed by [Copycat's implementation of the Raft consensus algorithm][raft-framework]. Raft uses a [distributed leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm to elect a leader. The leader election algorithm guarantees that the server that is elected leader will have all the writes to the cluster that have previously been successful. All writes go through the cluster leader and are *synchronously replicated to a majority of servers* before completion. Additionally, writes are sequenced in the order in which they're submitted by the client (sequential consistency).

Unlike [ZooKeeper], Copycat natively supports linearizable reads as well. Much like writes, linearizable reads must go through the cluster leader (which always has the most recent cluster state) and may require contact with a majority of the cluster. For higher throughput, Copycat also allows reads from followers. Reads from followers guarantee *serializable consistency*, meaning all clients will see state changes in the same order but different clients may see different views of the state at any given time. Notably, *a client's view of the cluster will never go back in time* even when switching between servers. Additionally, Copycat places a bound on followers servicing reads: in order to service a read, a follower's log must be less than a heartbeat behind the leader's log.

*See the [Raft implementation details]({{ site.baseurl }}/user-manual/raft-internals/) for more information on consistency in Copycat*

## Fault-tolerance

Because Copycat falls on the CP side of the CAP theorem, it favors consistency over availability, particularly under failure. In order to ensure consistency, Copycat's [consensus protocol][raft-framework] requires that a majority of the cluster be alive and operating normally to service reads and writes.

* A cluster of `1` replica can tolerate `0` failures
* A cluster of `2` replicas can tolerate `0` failures
* A cluster of `3` replicas can tolerate `1` failure
* A cluster of `4` replicas can tolerate `1` failure
* A cluster of `5` replicas can tolerate `2` failures

Failures in Copycat are handled by Raft's [leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm. When the Copycat cluster starts, a leader is elected. Leaders are elected by a round of voting wherein servers vote for a candidate based on the [consistency of its log](#consistency-model).

In the event of a failure of the leader, the remaining servers in the cluster will begin a new election and a new leader will be elected. This means for a brief period (seconds) the cluster will be unavailable.

In the event of a partition, if the leader is on the quorum side of the partition, it will continue to operate normally. Alternatively, if the leader is on the non-quorum side of the partition, the leader will detect the partition (based on the fact that it can no longer contact a majority of the cluster) and step down, and the servers on the majority side of the partition will elect a new leader. Once the partition is resolved, nodes on the non-quorum side of the partition will join the quorum side and receive updates to their log from the remaining leader.

## Project structure

Copycat is designed as a series of libraries that combine to form a framework for managing fault-tolerant state in a distributed system. The project currently consists of 14 modules, each of which implements a portion of the framework's functionality. The components of the project are composed hierarchically, so lower level components can be used independently of most other modules.

A rough outline of Copycat's project hierarchy is as follows (from high-level to low-level):

{:.well}
* [Resources][Resource]
   * [Distributed collections][collections] (artifact ID: `copycat-collections`)
   * [Distributed atomic variables][atomic] (artifact ID: `copycat-atomic`)
   * [Distributed coordination tools][coordination] (artifact ID: `copycat-coordination`)
* [Copycat API][copycat] (artifact ID: `copycat`)
   * [Copycat Client][CopycatClient]
   * [Copycat Replica][CopycatReplica]
   * [Resource API][Resource]
* [Raft Consensus Algorithm][raft]
   * [Raft Protocol][protocol] (artifact ID: `copycat-protocol`)
   * [Raft Client][RaftClient] (artifact ID: `copycat-client`)
   * [Raft Server][RaftServer] (artifact ID: `copycat-server`)
* [I/O & Serialization][io]
   * [Buffer][io] (artifact ID: `copycat-io`)
   * [Serializer][serializer] (artifact ID: `copycat-io`)
   * [Transport][transport] (artifact ID: `copycat-transport`)
      * [Local transport][LocalTransport] (artifact ID: `copycat-local`)
      * [Netty transport][NettyTransport] (artifact ID: `copycat-netty`)
   * [Storage][storage] (artifact ID: `copycat-storage`)
* [Utilities][utilities] (artifact ID: `copycat-common`)
   * [Builder][Builder]
   * [Listener][Listener]
   * [Context][Context]

## Dependencies

Copycat is designed to ensure that different components of the project ([resources], [Raft][raft-framework], [I/O][io-serialization], etc) can work independently of one another and with minimal dependencies. To that end, *the core library has zero dependencies*. The only components where dependencies are required is in custom `Transport` implementations, such as the [NettyTransport][NettyTransport].

Copycat provides an all-encompassing dependency - `copycat-all` - which provides all base modules, transport, and [resource][resources] dependencies.

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-all</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

If `copycat-all` is just not your style, to add Copycat's high-level API as a dependency to your Maven project add the `copycat` dependency:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

Additionally, in order to facilitate communication between [clients][client] and [replicas][replica] you must add a [Transport][transports] dependency. Typically, the [NettyTransport][NettyTransport] will suffice for most use cases:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-netty</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

Finally, to add specific [resources][resources] as dependencies, add one of the resource modules:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-collections</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

## Thread model

Copycat is designed to be used in an asynchronous manner that provides easily understood guarantees for users. All usage of asynchronous APIs such as `CompletableFuture` are carefully orchestrated to ensure that various callbacks are executed in a deterministic manner. To that end, Copycat provides the following single guarantee:

* Callbacks for any given object are guaranteed to always be executed on the same thread

### Asynchronous API usage

Copycat's API makes heavy use of Java 8's [CompletableFuture][CompletableFuture] for asynchronous completion of method calls. The asynchronous API allows users to execute multiple operations concurrently instead of blocking on each operation in sequence. For information on the usage of `CompletableFuture` [see the CompletableFuture documentation][CompletableFuture].

Most examples in the following documentation will assume asynchronous usage of the `CompletableFuture` API. See [synchronous API usage]({{ site.baseurl}}/user-manual/introduction#synchronous-api-usage) for examples of how to use the API synchronously.

### Synchronous API usage

Copycat makes heavy use of Java 8's [CompletableFuture][CompletableFuture] in part because it allows users to easily block on asynchronous method calls. The following documentation largely portrays asynchronous usage. To block and wait for a `CompletableFuture` result instead of registering an asynchronous callback, simply use the `get()` or `join()` methods.

```java
// Get the "foo" key from a map
CompletableFuture<String> future = map.get("foo");

// Block to wait for the result
String result = future.get();
```

{% include common-links.html %}