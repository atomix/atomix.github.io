---
layout: content
menu: user-manual
title: Copycat API
---

Copycat provides a high-level path-based API for creating and operating on custom replicated state machines. Additionally, Copycat provides a number of custom [resources](#resources) to aid in common distributed coordination tasks:

* [Distributed atomic variables](#distributed-atomic-variables)
* [Distributed collections](#distributed-collections)
* [Distributed coordination tools](#distributed-coordination)

Resources are managed via a [Copycat][Copycat] instance which is shared by both [clients](#copycatclient) and [replicas](#copycatreplica). This allows Copycat clients and servers to be embedded in applications that don't care about the context. Resources can be created and operated on regardless of whether the local `Copycat` instance is a [CopycatClient][CopycatClient] or [CopycatReplica][CopycatReplica].

## CopycatReplica

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

## CopycatClient

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