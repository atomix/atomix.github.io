---
layout: docs
project: copycat
menu: docs
title: Working with Servers
first-section: server
---

{:.no-margin-top}
The [`CopycatServer`][CopycatServer] class is a feature complete implementation of the [Raft consensus algorithm][Raft]. Multiple servers communicate with each other to form a cluster and manage a replicated [state machine][StateMachine]. Server state machines are user-defined.

## Server Lifecycle

Copycat's Raft implementation supports dynamic membership changes designed to allow servers to arbitrarily join and leave the cluster. The first time a cluster is started, the cluster must be [`bootstrap`][CopycatServer.bootstrap]ped with a single initial member or a cluster of initial members. The bootstrap servers make up the initial Raft cluster. Once the cluster is initialized, additional servers can be [`join`][CopycatServer.join]ed to the cluster.

When a member *joins* the cluster, a *join* request will ultimately be received by the cluster's leader. The leader will log and replicate the joining member's configuration. Once the joined member's configuration has been persisted on a majority of the cluster, the joining member will be notified of the membership change and transition to the *passive* state. While in the *passive* state, the joining member cannot participate in votes but does receive *append* requests from the cluster leader. Once the leader has determined that the joining member's log has caught up to its own (the joining node's log has the last committed entry at any given point in time), the member is promoted to a full member via another replicated configuration change.

Once a node has fully joined the Raft cluster, in the event of a failure the quorum size will not change. To leave the cluster, the [`leave`][CopycatServer.leave] method must be called on a [`CopycatServer`][CopycatServer] instance. When [`leave`][CopycatServer.leave] is called, the member will submit a *leave* request to the leader. Once the leaving member's configuration has been removed from the cluster and the new configuration replicated and committed, the server will complete the close.

## Configuring the Server

Each [`CopycatServer`][CopycatServer] consists of three essential components:

* [`Transport`][Transport] - Used to communicate with clients and other servers
* [`Storage`][Storage] - Used to persist [`Command`][Command]s to memory or disk
* [`StateMachine`][StateMachine] - Represents state resulting from [`Command`][Command]s logged and replicated via Raft

To create a new server, use the server [`Builder`][CopycatServer.Builder]. Servers require cluster membership information in order to perform communication. Each server must be provided a local [`Address`][Address] to which to bind the internal [`Server`][Server].

```java
CopycatServer.Builder builder = CopycatServer.builder(new Address("123.456.789.0", 8700));

// Configure the server

CopycatServer server = builder.build();
```

The [`Address`][Address] provided to the server builder factory method is the address that will be used by the server to communicate both with servers and with clients. Alternatively, separate addresses for client and server communication can be provided to allow for more concurrently when communicating with clients and servers.

```java
Address serverAddress = new Address("123.456.789.0", 8700);
Address clientAddress = new Address("123.456.789.0", 8701);
CopycatServer server = CopycatServer.builder(clientAddress, serverAddress).build();
```

When providing both a client and server [`Address`][Address], the client address must be passed as the first argument to the `builder(Address, Address)` factory and the server address as the second.

## Configuring the State Machine

Underlying each server is a [`StateMachine`][StateMachine]. The state machine is responsible for maintaining the state with relation to [`Command`][Command] and [`Query`][Query] operations submitted to the server by a client. State machines are provided in a factory to allow servers to transition between stateful and stateless states.

```java
Address address = new Address("123.456.789.0", 5000);
Collection<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000),
);

CopycatServer server = CopycatServer.builder(address)
  .withStateMachine(MyStateMachine::new)
  .build();
```

Server state machines are responsible for registering [`Command`][Command]s which can be submitted to the cluster. Raft relies upon determinism to ensure consistency throughout the cluster, so *it is imperative that each server in a cluster have the same state machine with the same commands.* State machines are provided to the server as a factory to allow servers to transition between stateful and stateless states.

## Configuring the Transport

By default, the server will use the [`NettyTransport`][NettyTransport] for communication. You can configure the transport via `withTransport`. To use the Netty transport, ensure you have the `io.atomix.catalyst:catalyst-netty` jar on your classpath.

```java
CopycatServer server = CopycatServer.builder(address)
  .withStateMachine(MyStateMachine::new)
  .withTransport(NettyTransport.builder()
    .withThreads(4)
    .build())
  .build();
```

## Configuring the Storage

As commands are received by the server, they're written to the Raft [`Log`][Log] and replicated to other members of the cluster. By default, the log is stored on disk, but users can override the default [`Storage`][Storage] configuration via `withStorage`. Most notably, to configure the storage module to store entries in memory instead of disk, configure the [`StorageLevel`][StorageLevel].

```java
CopycatServer server = CopycatServer.builder(address)
  .withStateMachine(MyStateMachine::new)
  .withStorage(Storage.builder()
    .withDirectory(new File("logs"))
    .withStorageLevel(StorageLevel.DISK)
    .build())
  .build();
```

Servers use the [`Storage`][Storage] object to manage the storage of cluster configurations, voting information, and state machine snapshots in addition to logs. See the [`Storage`][Storage] documentation for more information.

## Serialization

All serialization is performed with a Catalyst [`Serializer`][Serializer]. The serializer is shared across all components of the server. Users are responsible for ensuring that [`Command`][Command] and [`Query`][Query] operations submitted to the cluster can be serialized by the server serializer by registering serializable types as necessary.

For the most efficient serialization, users should explicitly register serializable classes and binary serializers. Explicit registration of serializable typs allows types to be serialized using more compact 8- 16- 24- and 32-bit serialization IDs rather than serializing complete class names. Thus, serializable type registration is strongly recommended for production systems.

```java
server.serializer().register(MySerializable.class, 123, MySerializableSerializer.class);
```

## Bootstrapping a Server

Once the server has been built, we can bootstrap a new cluster by calling the [`bootstrap()`][CopycatServer.bootstrap] method:

```java
CompletableFuture<CopycatServer> future = server.bootstrap();
future.join();
```

When a server is bootstrapped, it forms a *new* cluster single node cluster to which additional servers can be joined.

## Bootstrapping a Cluster

Multiple servers can be bootstrapped to form a cluster by passing a list of server addresses to the [`bootstrap(Address...)`][CopycatServer.bootstrap] method:

```java
Collection<Addres> cluster = Arrays.asList(
  new Address("123.456.789.0", 8700),
  new Address("123.456.789.1", 8700),
  new Address("123.456.789.2", 8700)
);

CompletableFuture<CopycatServer> future = server.bootstrap(cluster);
future.join();
```

<h2 id="joining-a-cluster">Joining an Existing Cluster</h2>

Once an initial cluster has been bootstrapped, additional servers can be added to the cluster via the [`join(Address...)`][CopycatServer.join] method. When joining an existing cluster, the existing cluster configuration must be provided to the join method:

```java
Collection<Addres> cluster = Arrays.asList(
  new Address("123.456.789.0", 8700),
  new Address("123.456.789.1", 8700),
  new Address("123.456.789.2", 8700)
);

server.join(cluster).join();
```

{% include common-links.html %}
