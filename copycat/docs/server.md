---
layout: docs
project: copycat
menu: docs
title: Raft Servers
first-section: server
---

{:.no-margin-top}
The [CopycatServer] class is a feature complete implementation of the [Raft consensus algorithm][Raft]. Multiple servers communicate with each other to form a cluster and manage a replicated [state machine][StateMachine]. Server state machines are user-defined.

Each `CopycatServer` consists of three essential components:

* [Transport] - Used to communicate with clients and other servers
* [Storage] - Used to persist [commands] to memory or disk
* [StateMachine][state-machines] - Represents state resulting from [commands] logged and replicated via Raft

To create a new server, use the server `Builder`. Servers require cluster membership information in order to perform communication. Each server must be provided a local `Address` to which to bind the internal `Server` and a set of addresses for other members in the cluster.

### State machines
Underlying each server is a [StateMachine][StateMachine]. The state machine is responsible for maintaining the state with relation to [commands][Command] and [queries][Query] submitted to the server by a client. State machines are provided in a factory to allow servers to transition between stateful and stateless states.

```java
Address address = new Address("123.456.789.0", 5000);
Collection<Address> members = Arrays.asList(
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000),
  new Address("123.456.789.3", 5000),
);

CopycatServer server = CopycatServer.builder(address, members)
  .withStateMachine(MyStateMachine::new)
  .build();
```

Server state machines are responsible for registering [commands][Command] which can be submitted to the cluster. Raft relies upon determinism to ensure consistency throughout the cluster, so *it is imperative that each server in a cluster have the same state machine with the same commands.* State machines are provided to the server as a factory to allow servers to transition between stateful and stateless states.

### Transports
By default, the server will use the [NettyTransport][NettyTransport] for communication. You can configure the transport via `withTransport`. To use the Netty transport, ensure you have the `io.atomix.catalyst:catalyst-netty` jar on your classpath.

```java
CopycatServer server = CopycatServer.builder(address, members)
  .withStateMachine(MyStateMachine::new)
  .withTransport(NettyTransport.builder()
    .withThreads(4)
    .build())
  .build();
```

### Storage

As commands are received by the server, they're written to the Raft [Log][Log] and replicated to other members of the cluster. By default, the log is stored on disk, but users can override the default [Storage][Storage] configuration via `withStorage`. Most notably, to configure the storage module to store entries in memory instead of disk, configure the [StorageLevel][StorageLevel].

```java
CopycatServer server = CopycatServer.builder(address, members)
  .withStateMachine(MyStateMachine::new)
  .withStorage(Storage.builder()
    .withDirectory(new File("logs"))
    .withStorageLevel(StorageLevel.DISK)
    .build())
  .build();
```

Servers use the `Storage` object to manage the storage of cluster configurations, voting information, and state machine snapshots in addition to logs. See the [Storage][Storage] documentation for more information.

### Serialization

All serialization is performed with a Catalyst [Serializer][Serializer]. The serializer is shared across all components of the server. Users are responsible for ensuring that {@link Command commands} and {@link Query queries} submitted to the cluster can be serialized by the server serializer by registering serializable types as necessary.

By default, the server serializer does not allow arbitrary classes to be serialized due to security concerns. However, users can enable arbitrary class serialization by disabling the whitelisting feature on the Catalyst `Serializer`:

```java
server.serializer().disableWhitelist();
```

However, for more efficient serialization, users should explicitly register serializable classes and binary [serializers][serialization]. Explicit registration of serializable typs allows types to be serialized using more compact 8- 16- 24- and 32-bit serialization IDs rather than serializing complete class names. Thus, serializable type registration is strongly recommended for production systems.

```java
server.serializer().register(MySerializable.class, 123, MySerializableSerializer.class);
```

### Running the server

Once the server has been created, to connect to a cluster simply `start` the server. The server API is
fully asynchronous and relies on `CompletableFuture` to provide promises:

```java
server.open().thenRun(() -> {
  System.out.println("Server started successfully!");
});
```

When the server is started, it will attempt to connect to an existing cluster. If the server cannot find any
existing members, it will attempt to form its own cluster.

Once the server is started, it will communicate with the rest of the nodes in the cluster, periodically
transitioning between states. Users can listen for state transitions via `onStateChange`:

```java
server.onStateChange(state -> {
  if (state == CopycatServer.State.LEADER) {
    System.out.println("Server elected leader!");
  }
});
```

### Server Lifecycle

Copycat's Raft implementation supports dynamic membership changes designed to allow servers to arbitrarily join and leave the cluster. When a `CopycatServer` is configured, the `Address` list provided in the server configuration specifies some number of servers to join to form a cluster. When the server is started, the server begins a series of steps to either join an existing Raft cluster or start a new cluster:

* When the server starts, transition to a *join* state and attempt to join the cluster by sending a *join* request to each known member of the cluster
* If, after an election timeout, the server has failed to receive a response to a *join* requests from any member of the cluster, assume that the cluster doesn't exist and transition into the *follower* state
* Once a leader has been elected or otherwise discovered, complete the startup

When a member *joins* the cluster, a *join* request will ultimately be received by the cluster's leader. The leader will log and replicate the joining member's configuration. Once the joined member's configuration has been persisted on a majority of the cluster, the joining member will be notified of the membership change and transition to the *passive* state. While in the *passive* state, the joining member cannot participate in votes but does receive *append* requests from the cluster leader. Once the leader has determined that the joining member's log has caught up to its own (the joining node's log has the last committed entry at any given point in time), the member is promoted to a full member via another replicated configuration change.

Once a node has fully joined the Raft cluster, in the event of a failure the quorum size will not change. To leave the cluster, the `close()` method must be called on a [CopycatServer] instance. When `close()` is called, the member will submit a *leave* request to the leader. Once the leaving member's configuration has been removed from the cluster and the new configuration replicated and committed, the server will complete the close.

{% include common-links.html %}