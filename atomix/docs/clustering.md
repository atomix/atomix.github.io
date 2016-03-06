---
layout: docs
project: atomix
menu: docs
title: Clustering
---

{:.no-margin-top}
Atomix clusters consist of at least one (but usually 3 or 5) [replica][replicas] and any number of [clients]. *Replicas* are stateful nodes that actively participate in the Raft consensus protocol, and *clients* are stateless nodes that modify system state remotely. When a cluster is started, the replicas in the cluster coordinate with one another to elect a leader.

![Atomix cluster](/assets/img/docs/cluster.png)

Once a leader has been elected, clients can connect to a random server in the cluster, create resources (e.g. maps, sets, locks, etc) and submit commands (writes) and queries (reads). All commands are proxied to the cluster leader. When the leader receives a command, it persists the write to disk and replicates it to the rest of the cluster. Once a command has been received and persisted on a majority of replicas, the state change is committed and guaranteed not to be lost.

Because the Atomix cluster is dependent on a majority of the cluster being reachable to commit writes, the cluster can tolerate a minority of the nodes failing. For this reason, it is recommended that each Atomix cluster have at least 3 or 5 replicas, and the number of replicas should always be odd in order to achieve the greatest level of fault-tolerance. The number of replicas should be calculated as `2f + 1` where `f` is the number of failures to tolerate.

Distributed resources are managed by a cluster of [replicas] and can be created and operated via an [Atomix] instance which is shared by both [clients] and [replicas]. This allows Atomix clients and servers to be embedded in applications that don't care about the context. Resources can be created and operated on by any `Atomix` instance.

## Forming a Cluster


## Joining an Existing Cluster



## Replicas

The [AtomixReplica] is an [Atomix] implementation that is responsible for receiving creating and managing resources on behalf of other clients and replicas and receiving, persisting, and replicating state changes for existing resources. Users should think of replicas as stateful nodes. Since replicas are responsible for persisting and replicating resource state changes, they require more configuration than [clients].

To create an `AtomixReplica`, first you must create a [Transport] via which the replica will communicate with other clients and replicas:

```java
Transport transport = new NettyTransport();
```

The [Transport] provides the mechanism through which replicas communicate with one another and with clients. It is essential that all clients and replicas configure the same transport.

Once the transport is configured, the replica must be provided with a list of members to which to connect. Cluster membership information is provided by configuring a collection of addresses.

```java
List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);
```

The members in the `Address` list must be representative of at least one reachable member of the cluster. If the replica can reach a member that can communicate with the leader, it can join the cluster.

Finally, the `AtomixReplica` is responsible for persisting resource state changes. To do so, the underlying Raft server writes state changes to a consistent replicated commit log. Users must provide a [Storage] object which specifies how the underlying `Log` should be created and managed.

To create a `Storage` object, use the storage [Builder][builders] or for simpler configurations simply pass the log directory into the `Storage` constructor:

```java
Storage storage = new Storage("logs");
```

The [Storage] object can optionally be configured with a custom `StorageLevel` which dictates how logs should be stored. The storage module supports the following storage levels:

* `StorageLevel.MEMORY` - Stores log entries in an off-heap memory buffer
* `StorageLevel.MAPPED` - Stores log entries in a memory mapped file buffer
* `StorageLevel.DISK` - Stores log entries in a `RandomAccessFile` backed buffer

Finally, with the `Transport`, `Storage`, and an `Address` list configured, create the [AtomixReplica][AtomixReplica] with the replica [Builder][builders] and `open()` the replica:

```java
Address address = new Address("123.456.789.0", 5000);

List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);

Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(transport)
  .withStorage(storage)
  .build();

atomix.open().thenRun(() -> {
  System.out.println("Replica started!");
});
```

Once created, the replica can be used as any `Atomix` instance to create and operate on [resources].

## Clients

The [AtomixClient][AtomixClient] is an [Atomix][Atomix] implementation that manages and operates on resources by communicating with a remote cluster of *servers* or *replicas*. Users should think of clients as stateless members of the Atomix cluster.

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

{% include common-links.html %}