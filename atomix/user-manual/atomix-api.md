---
layout: content
project: atomix
menu: user-manual
title: Atomix API
pitch: Simple API for building powerful distributed systems
first-section: atomix-api
---

Atomix provides a high-level path-based API for creating and operating on custom replicated state machines. Additionally, Atomix provides a number of custom [resources] to aid in common distributed coordination tasks:

* [Distributed atomic variables](/user-manual/distributed-resources#distributed-atomic-variables)
* [Distributed collections](/user-manual/distributed-resources#distributed-collections)
* [Distributed coordination tools](/user-manual/distributed-resources#distributed-coordination)

Resources are managed via an [Atomix] instance which is shared by both [clients](#atomixclient) and [replicas](#atomixreplica). This allows Atomix clients and servers to be embedded in applications that don't care about the context. Resources can be created and operated on regardless of whether the local `Atomix` instance is a [AtomixClient] or [AtomixReplica].

## AtomixReplica

The [AtomixReplica] is an [Atomix] implementation that is responsible for receiving creating and managing [resources] on behalf of other clients and replicas and receiving, persisting, and replicating state changes for existing resources. Users should think of replicas as stateful nodes. Since replicas are responsible for persisting and replicating resource state changes, they require more configuration than [clients](#atomixclient).

To create a `AtomixReplica`, first you must create a [Transport][io-transports] via which the replica will communicate with other clients and replicas:

```java
Transport transport = new NettyTransport();
```

The [Transport] provides the mechanism through which replicas communicate with one another and with clients. It is essential that all clients and replicas configure the same transport.

Once the transport is configured, the replica must be provided with a list of members to which to connect. Cluster membership information is provided by configuring a `Members` list.

```java
Members members = Members.builder()
  .addMember(new Member(1, "123.456.789.1", 5555))
  .addMember(new Member(2, "123.456.789.2", 5555))
  .addMember(new Member(3, "123.456.789.3", 5555))
  .build();
```

Each member in the `Members` list must be assigned a unique `id` that remains consistent across all clients and replicas in the cluster, and the local replica must be listed in the `Members` list. In other words, if host `123.456.789.1` is member `1` on one replica, it must be listed as member `1` on all replicas.

Finally, the `AtomixReplica` is responsible for persisting [resource][resources] state changes. To do so, the underlying [Raft server][raft-server] writes state changes to a persistent [Log][Log]. Users must provide a [Storage][Storage] object which specifies how the underlying `Log` should be created and managed.

To create a [Storage](#storage) object, use the storage [Builder][builders] or for simpler configurations simply pass the log directory into the `Storage` constructor:

```java
Storage storage = new Storage("logs");
```

Finally, with the [Transport][Transport], [Storage][Storage], and `Members` configured, create the [AtomixReplica][AtomixReplica] with the replica [Builder][builders] and `open()` the replica:

```java
Atomix atomix = AtomixReplica.builder()
  .withMemberId(1)
  .withMembers(members)
  .withTransport(transport)
  .withStorage(storage)
  .build();

atomix.open().thenRun(() -> {
  System.out.println("Atomix started!");
});
```

Once created, the replica can be used as any `Atomix` instance to create and operate on [resources].

Internally, the `AtomixReplica` wraps a [RaftClient][RaftClient] and [RaftServer][RaftServer] to communicate with other members of the cluster. For more information on the specific implementation of `AtomixReplica` see the [RaftClient][raft-client] and [RaftServer][raft-server] documentation.

## AtomixClient

The [AtomixClient][AtomixClient] is a [Atomix][Atomix] implementation that manages and operates on [resources] by communicating with a remote cluster of [replicas](#atomixreplica). Users should think of clients as stateless members of the Atomix cluster.

To create a `AtomixClient`, use the client [Builder][builders] and provide a [Transport][Transport] and a list of `Members` to which to connect:

```java
Atomix atomix = AtomixClient.builder()
  .withTransport(new NettyTransport())
  .withMembers(Members.builder()
    .addMember(new Member(1, "123.456.789.1", 5555))
    .addMember(new Member(2, "123.456.789.2", 5555))
    .addMember(new Member(3, "123.456.789.3", 5555))
    .build())
  .build();
```

The provided `Members` list does not have to be representative of the full list of active servers. Users must simply provide enough `Member`s to be able to successfully connect to at least one correct server.

Once the client has been created, open a new session to the Atomix cluster by calling the `open()` method:

```java
atomix.open().thenRun(() -> {
  System.out.println("Client connected!");
});
```

The `AtomixClient` wraps a [RaftClient][RaftClient] to communicate with servers internally. For more information on the client implementation see the [Raft client documentation][raft-client].

{% include common-links.html %}