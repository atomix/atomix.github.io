---
layout: content
project: copycat
menu: user-manual
title: Raft Consensus Algorithm
pitch: Sophisticated Raft Consensus implementation
first-section: server
---

## CopycatServer

The [CopycatServer][CopycatServer] class is a feature complete implementation of the [Raft consensus algorithm][Raft]. `CopycatServer` underlies all distributed resources supported by Copycat's high-level APIs.

Each `CopycatServer` consists of three essential components:

* [Transport][transport] - Used to communicate with clients and other Raft servers
* [Storage][storage-jd] - Used to persist [commands] to memory or disk
* [StateMachine][state-machines] - Represents state resulting from [commands] logged and replicated via Raft

To create a Raft server, use the server [Builder][builders]:

```java
CopycatServer server = CopycatServer.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage("logs"))
  .withStateMachine(new MyStateMachine())
  .build();
```

The only two required arguments are those required by the `CopycatServer.builder` static factory method. The `address` passed into the builder factory is the `Address` of the server within the provided list of `Address`es.

Users can optionally configure the [Catalyst][catalyst] transport to use and configure the Raft storage (log) module. To manage state in the Raft cluster, users must provide a `StateMachine` implementation to the server. The state machine should *always* be consistent and deterministic across all servers in the cluster.

Once the server has been created, call `open()` to start the server:

{% include sync-tabs.html target1="#async-server-open" desc1="Async" target2="#sync-server-open" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-server-open">
```java
server.open().thenRun(() -> System.out.println("Server started successfully!"));
```
</div>

<div class="tab-pane" id="sync-server-open">
```java
server.open().join();
```
</div>
</div>

The returned `CompletableFuture` will be completed once the server has connected to other members of the cluster and, critically, discovered the cluster leader. See the [server lifecycle](#server-lifecycle) for more information on how the server joins the cluster.

### Server lifecycle

Copycat's Raft implementation supports dynamic membership changes designed to allow servers to arbitrarily join and leave the cluster. When a `CopycatServer` is configured, the `Address` list provided in the server configuration specifies some number of servers to join to form a cluster. When the server is started, the server begins a series of steps to either join an existing Raft cluster or start a new cluster:

* When the server starts, transition to a *join* state and attempt to join the cluster by sending a *join* request to each known member of the cluster
* If, after an election timeout, the server has failed to receive a response to a *join* requests from any member of the cluster, assume that the cluster doesn't exist and transition into the *follower* state
* Once a leader has been elected or otherwise discovered, complete the startup

When a member *joins* the cluster, a *join* request will ultimately be received by the cluster's leader. The leader will log and replicate the joining member's configuration. Once the joined member's configuration has been persisted on a majority of the cluster, the joining member will be notified of the membership change and transition to the *passive* state. While in the *passive* state, the joining member cannot participate in votes but does receive *append* requests from the cluster leader. Once the leader has determined that the joining member's log has caught up to its own (the joining node's log has the last committed entry at any given point in time), the member is promoted to a full member via another replicated configuration change.

Once a node has fully joined the Raft cluster, in the event of a failure the quorum size will not change. To leave the cluster, the `close()` method must be called on a [CopycatServer] instance. When `close()` is called, the member will submit a *leave* request to the leader. Once the leaving member's configuration has been removed from the cluster and the new configuration replicated and committed, the server will complete the close.

{% include common-links.html %}