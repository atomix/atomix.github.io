---
layout: content
menu: user-manual
title: Introduction
---

# Introduction

Copycat is a framework for consistent distributed coordination. At the core of Copycat is a generic implementation of the [Raft consensus algorithm][Raft]. On top of Raft, Copycat provides a high level API for creating and managing arbitrary user-defined replicated state machines such as maps, sets, locks, or user-defined resources. Resources can be created and modified by any replica or client in the cluster.

Copycat clusters consist of at least one [replica](#copycatreplica) and any number of [clients](#copycatclient). *Replicas* are stateful nodes that actively participate in the Raft consensus protocol, and *clients* are stateless nodes that modify system state remotely.

When a cluster is started, the replicas in the cluster coordinate with one another to elect a leader. Once a leader has been elected, all state changes (i.e. writes) are proxied to the cluster leader. When the leader receives a write, it persists the write to [disk](#storage) and replicates it to the rest of the cluster. Once a write has been received and persisted on a majority of replicas, the write is committed and guaranteed not to be lost.

Because the Copycat cluster is dependent on a majority of the cluster being reachable to commit writes, the cluster can tolerate a minority of the nodes failing. For this reason, it is recommended that each Copycat cluster have at least 3 or 5 replicas, and the number of replicas should always be odd in order to achieve the greatest level of fault-tolerance. The number of replicas should be calculated as `2f + 1` where `f` is the number of failures to tolerate.

**So what's the difference between Copycat and those other projects?**

[ZooKeeper](https://zookeeper.apache.org/) - Copycat and ZooKeeper are both backed by a similar consensus-based persistence/replication layer. But Copycat is a framework that can be embedded instead of depending on an external cluster. Additionally, ZooKeeper's low-level primitives require complex recipes or other tools like [Apache Curator](http://curator.apache.org/), whereas Copycat provides [high-level interfaces](#resources) for common data structures and coordination tools like [locks](#distributedlock), [maps](#distributedmap), and [leader elections](#distributedleaderelection), or the option to create [custom replicated state machines](#custom-resources).

[Hazelcast](http://hazelcast.org/) - Hazelcast is a fast, in-memory data grid that, like Copycat, exposes rich APIs for operating on distributed object But whereas Hazelcast chooses [availability over consistency in the face of a partition](https://en.wikipedia.org/wiki/CAP_theorem), Copycat is designed to ensure that data is never lost in the event of a network partition or other failure. Like ZooKeeper, this requires that Copycat synchronously replicate all writes to a majority of the cluster and persist writes to disk, much like ZooKeeper.

## The CAP theorem

[The CAP theorem][CAP] is a frequently referenced theorem that states that it is impossible for a distributed system to simultaneously provide *Consistency*, *Availability*, and *Partition tolerance*. All distributed systems must necessarily sacrifice either consistency or availability, or some level of both, in the event of a partition.

By definition, high-throughput, high-availability distributed databases like [Hazelcast](http://hazelcast.org/) or [Cassandra](http://cassandra.apache.org/) and other Dynamo-based systems fall under the *A* and *P* in the CAP theorem. That is, these systems generally sacrifice consistency in favor of availability during network failures. In AP systems, a network partition can result in temporary or even permanent loss of writes. These systems are generally designed to store and query large amounts of data quickly.

Alternatively, systems like [ZooKeeper](https://zookeeper.apache.org/) which fall under the *C* and *P* in the CAP theorem are generally designed to store small amounts of mission critical state. CP systems provide strong consistency guarantees like [linearizability](https://en.wikipedia.org/wiki/Linearizability) and [sequential consistency](https://en.wikipedia.org/wiki/Sequential_consistency) even in the face of failures, but that level of consistency comes at a cost: availability. CP systems like ZooKeeper and Copycat are consensus-based and thus can only tolerate the loss of a minority of servers.

## Consistency model

In terms of the CAP theorem, Copycat falls squarely in the CP range. That means Copycat provides configurable strong consistency levels - [linearizability](https://en.wikipedia.org/wiki/Linearizability) for writes and reads, and optional weaker [serializability](https://en.wikipedia.org/wiki/Serializability) for reads - for all operations. Linearizability says that all operations must take place some time between their invocation and completion. This means that once a write is committed to the cluster, all clients are guaranteed to see the resulting state. 

Consistency is guaranteed by [Copycat's implementation of the Raft consensus algorithm](#raft-consensus-algorithm). Raft uses a [distributed leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm to elect a leader. The leader election algorithm guarantees that the server that is elected leader will have all the writes to the cluster that have previously been successful. All writes to the cluster go through the cluster leader and are *synchronously replicated to a majority of servers* before completion. Additionally, writes are sequenced in the order in which they're submitted by the client (sequential consistency).

Unlike [ZooKeeper](https://zookeeper.apache.org/), Copycat natively supports linearizable reads as well. Much like writes, linearizable reads must go through the cluster leader (which always has the most recent cluster state) and may require contact with a majority of the cluster. For higher throughput, Copycat also allows reads from followers. Reads from followers guarantee *serializable consistency*, meaning all clients will see state changes in the same order but different clients may see different views of the state at any given time. Notably, *a client's view of the cluster will never go back in time* even when switching between servers. Additionally, Copycat places a bound on followers servicing reads: in order to service a read, a follower's log must be less than a heartbeat behind the leader's log.

*See the [Raft implementation details](#raft-implementation-details) for more information on consistency in Copycat*

## Fault-tolerance

Because Copycat falls on the CP side of the CAP theorem, it favors consistency over availability, particularly under failure. In order to ensure consistency, Copycat's [consensus protocol](#raft-consensus-algorithm) requires that a majority of the cluster be alive and operating normally to service writes.

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

Copycat is designed to ensure that different components of the project ([resources](#resources), [Raft](#raft-consensus-algorithm), [I/O](#io--serialization), etc) can work independently of one another and with minimal dependencies. To that end, *the core library has zero dependencies*. The only components where dependencies are required is in custom `Transport` implementations, such as the [NettyTransport][NettyTransport].

Copycat provides an all-encompassing dependency - `copycat-all` - which provides all base modules, transport, and [resource](#resources) dependencies.

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

Additionally, in order to facilitate communication between [clients](#copycatclient) and [replicas](#copycatreplica) you must add a [Transport](#transport) dependency. Typically, the [NettyTransport][NettyTransport] will suffice for most use cases:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-netty</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

Finally, to add specific [resources](#resources) as dependencies, add one of the resource modules:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-collections</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

## The Copycat API

Copycat provides a high-level path-based API for creating and operating on custom replicated state machines. Additionally, Copycat provides a number of custom [resources](#resources) to aid in common distributed coordination tasks:

* [Distributed atomic variables](#distributed-atomic-variables)
* [Distributed collections](#distributed-collections)
* [Distributed coordination tools](#distributed-coordination)

Resources are managed via a [Copycat][Copycat] instance which is shared by both [clients](#copycatclient) and [replicas](#copycatreplica). This allows Copycat clients and servers to be embedded in applications that don't care about the context. Resources can be created and operated on regardless of whether the local `Copycat` instance is a [CopycatClient][CopycatClient] or [CopycatReplica][CopycatReplica].

### CopycatReplica

The [CopycatReplica][CopycatReplica] is a [Copycat][Copycat] implementation that is responsible for receiving creating and managing [resources](#resources) on behalf of other clients and replicas and receiving, persisting, and replicating state changes for existing resources.

Users should think of replicas as stateful nodes. Because replicas are responsible for persisting and replicating resource state changes, they require more configuration than [clients](#copycatclient).

To create a `CopycatReplica`, first you must create a [Transport](#transport) via which the replica will communicate with other clients and replicas:

```java
Transport transport = new NettyTransport();
```

The [Transport][Transport] provides the mechanism through which replicas communicate with one another and with clients. It is essential that all clients and replicas configure the same transport.

Once the transport is configured, the replica must be provided with a list of members to which to connect. Cluster membership information is provided by configuring a `Members` list.

```java
Members members = Members.builder()
  .addMember(new Member(1, "123.456.789.1", 5555))
  .addMember(new Member(2, "123.456.789.2", 5555))
  .addMember(new Member(3, "123.456.789.3", 5555))
  .build();
```

Each member in the `Members` list must be assigned a unique `id` that remains consistent across all clients and replicas in the cluster, and the local replica must be listed in the `Members` list. In other words, if host `123.456.789.1` is member `1` on one replica, it must be listed as member `1` on all replicas.

Finally, the `CopycatReplica` is responsible for persisting [resource](#resources) state changes. To do so, the underlying [Raft server](#raftserver) writes state changes to a persistent [Log][Log]. Users must provide a [Storage][Storage] object which specifies how the underlying `Log` should be created and managed.

To create a [Storage](#storage) object, use the storage [Builder](#builders) or for simpler configurations simply pass the log directory into the `Storage` constructor:

```java
Storage storage = new Storage("logs");
```

Finally, with the [Transport][Transport], [Storage][Storage], and `Members` configured, create the [CopycatReplica][CopycatReplica] with the replica [Builder](#builders) and `open()` the replica:

```java
Copycat copycat = CopycatReplica.builder()
  .withMemberId(1)
  .withMembers(members)
  .withTransport(transport)
  .withStorage(storage)
  .build();

copycat.open().thenRun(() -> {
  System.out.println("Copycat started!");
});
```

Once created, the replica can be used as any `Copycat` instance to create and operate on [resources](#resources).

Internally, the `CopycatReplica` wraps a [RaftClient][RaftClient] and [RaftServer][RaftServer] to communicate with other members of the cluster. For more information on the specific implementation of `CopycatReplica` see the [RaftClient](#raftclient) and [RaftServer](#raftserver) documentation.

### CopycatClient

The [CopycatClient][CopycatClient] is a [Copycat][Copycat] implementation that manages and operates on [resources](#resources) by communicating with a remote cluster of [replicas](#copycatreplica).

Users should think of clients as stateless members of the Copycat cluster.

To create a `CopycatClient`, use the client [Builder](#builders) and provide a [Transport][Transport] and a list of `Members` to which to connect:

```java
Copycat copycat = CopycatClient.builder()
  .withTransport(new NettyTransport())
  .withMembers(Members.builder()
    .addMember(new Member(1, "123.456.789.1", 5555))
    .addMember(new Member(2, "123.456.789.2", 5555))
    .addMember(new Member(3, "123.456.789.3", 5555))
    .build())
  .build();
```

The provided `Members` list does not have to be representative of the full list of active servers. Users must simply provide enough `Member`s to be able to successfully connect to at least one correct server.

Once the client has been created, open a new session to the Copycat cluster by calling the `open()` method:

```java
copycat.open().thenRun(() -> {
  System.out.println("Client connected!");
});
```

The `CopycatClient` wraps a [RaftClient][RaftClient] to communicate with servers internally. For more information on the client implementation see the [Raft client documentation](#raftclient).

## Thread model

Copycat is designed to be used in an asynchronous manner that provides easily understood guarantees for users. All usage of asynchronous APIs such as `CompletableFuture` are carefully orchestrated to ensure that various callbacks are executed in a deterministic manner. To that end, Copycat provides the following single guarantee:

* Callbacks for any given object are guaranteed to always be executed on the same thread

### Asynchronous API usage

Copycat's API makes heavy use of Java 8's [CompletableFuture][CompletableFuture] for asynchronous completion of method calls. The asynchronous API allows users to execute multiple operations concurrently instead of blocking on each operation in sequence. For information on the usage of `CompletableFuture` [see the CompletableFuture documentation][CompletableFuture].

Most examples in the following documentation will assume asynchronous usage of the `CompletableFuture` API. See [synchronous API usage](#synchronous-api-usage) for examples of how to use the API synchronously.

### Synchronous API usage

Copycat makes heavy use of Java 8's [CompletableFuture][CompletableFuture] in part because it allows users to easily block on asynchronous method calls. The following documentation largely portrays asynchronous usage. To block and wait for a `CompletableFuture` result instead of registering an asynchronous callback, simply use the `get()` or `join()` methods.

```java
// Get the "foo" key from a map
CompletableFuture<String> future = map.get("foo");

// Block to wait for the result
String result = future.get();
```

## Resources

The true power of Copycat comes through provided and custom [Resource][Resource] implementation. Resources are named distributed objects that are replicated and persisted in the Copycat cluster. Each name can be associated with a single resource, and each resource is backed by a replicated state machine managed by Copycat's underlying [implementation of the Raft consensus protocol](#raft-consensus-algorithm).

Resources are created by simply passing a `Resource` class to one of Copycat's `create` methods:

```java
DistributedMap<String, String> map = copycat.create("/test-map", DistributedMap.class);
```

Copycat uses the provided `Class` to create an associated [StateMachine](#state-machines) on each replica. This allows users to create and integrate [custom resources](#custom-resources).

### Persistence model

Copycat clients and replicas communicate with each other through [sessions](#sessions). Each session represents a persistent connection between a single client and a complete Copycat cluster. Sessions allow Copycat to associate resource state changes with clients, and this information can often be used to manage state changes in terms of sessions as well.

Some Copycat resources expose a configurable `PersistenceMode` for resource state change operations. The persistence mode specifies whether a state change is associated directly with the client's `Session`. Copycat exposes two persistence modes:

* `PersistenceMode.PERSISTENT` - State changes persist across session changes
* `PersistenceMode.EPHEMERAL` - State changes are associated directly with the session that created them

The `EPHEMERAL` persistence mode allows resource state changes to be reflected only as long as the session that created them remains alive. For instance, if a `DistributedMap` key is set with `PersistenceMode.EPHEMERAL`, the key will disappear from the map when the session that created it expires or is otherwise closed.

### Consistency levels

When performing operations on resources, Copycat separates the types of operations into two categories:

* *commands* - operations that alter the state of a resource
* *queries* - operations that query the state of a resource

The [Raft consensus algorithm](#raft-consensus-algorithm) on which Copycat is built guarantees linearizability for *commands* in all cases. When a command is submitted to the cluster, the command will always be forwarded to the cluster leader and replicated to a majority of servers before being applied to the resource's state machine and completed.

Alternatively, Copycat allows for optional trade-offs in the case of *queries*. These optimizations come at the expense of consistency. When a query is submitted to the cluster, users can often specify the minimum consistency level of the request by providing a `ConsistencyLevel` constant. The four minimum consistency levels available are:

* `ConsistencyLevel.LINEARIZABLE` - Provides guaranteed linearizability by forcing all reads to go through the leader and verifying leadership with a majority of the Raft cluster prior to the completion of all operations
* `ConsistencyLevel.LINEARIZABLE_LEASE` - Provides best-effort optimized linearizability by forcing all reads to go through the leader but allowing most queries to be executed without contacting a majority of the cluster so long as less than the election timeout has passed since the last time the leader communicated with a majority
* `ConsistencyLevel.SERIALIZABLE` - Provides serializable consistency by allowing clients to read from followers and ensuring that clients see state progress monotonically

Overloaded methods with `ConsistencyLevel` parameters are provided throughout Copycat's resources wherever it makes sense. In many cases, resources dictate the strongest consistency levels - e.g. [coordination](#distributed-coordination) - and so weaker consistency levels are not allowed.

[Javadoc]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/
[CAP]: https://en.wikipedia.org/wiki/CAP_theorem
[Raft]: https://raft.github.io/
[Executor]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/Executor.html
[CompletableFuture]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html
[collections]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections.html
[atomic]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/atomic.html
[coordination]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination.html
[copycat]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat.html
[protocol]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol.html
[io]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io.html
[serializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer.html
[transport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport.html
[storage]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage.html
[utilities]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util.html
[Copycat]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/Copycat.html
[CopycatReplica]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/CopycatReplica.html
[CopycatClient]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/CopycatClient.html
[Resource]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/Resource.html
[Transport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/Transport.html
[LocalTransport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/LocalTransport.html
[NettyTransport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/NettyTransport.html
[Storage]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage/Storage.html
[Log]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage/Log.html
[Buffer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/Buffer.html
[BufferReader]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/BufferReader.html
[BufferWriter]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/BufferWriter.html
[Serializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/Serializer.html
[CopycatSerializable]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/CopycatSerializable.html
[TypeSerializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/TypeSerializer.html
[SerializableTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[PrimitiveTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[JdkTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[ServiceLoaderTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/ServiceLoaderTypeResolver.html
[RaftServer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/RaftServer.html
[RaftClient]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/RaftClient.html
[Session]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/session/Session.html
[Operation]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Operation.html
[Command]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Command.html
[Query]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Query.html
[Commit]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Commit.html
[ConsistencyLevel]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/ConsistencyLevel.html
[DistributedAtomicValue]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/atomic/DistributedAtomicValue.html
[DistributedSet]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections/DistributedSet.html
[DistributedMap]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections/DistributedMap.html
[DistributedLock]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedLock.html
[DistributedLeaderElection]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedLeaderElection.html
[DistributedTopic]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedTopic.html
[Builder]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/Builder.html
[Listener]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/Listener.html
[Context]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/concurrent/Context.html