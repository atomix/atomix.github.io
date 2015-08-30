---
layout: content
menu: user-manual
title: Raft consensus algorithm
---

## Raft consensus algorithm

Copycat is built on a standalone, feature-complete implementation of the [Raft consensus algorithm][Raft].
The Raft implementation consists of three Maven submodules:

#### copycat-protocol

The `copycat-protocol` submodule provides base interfaces and classes that are shared between both
the [client](#copycat-client) and [server](#copycat-server) modules. The most notable components of
the protocol submodule are [commands][Command] and [queries][Query] with which the client
communicates state machine operations, and [sessions][Session] through which clients and servers
communicate.

#### copycat-server

The `copycat-server` submodule is a standalone [Raft][Raft] server implementation. The server provides
a feature-complete implementation of the [Raft consensus algorithm][Raft], including dynamic cluster
membership changes and log compaction.

The primary interface to the `copycat-server` module is [RaftServer][RaftServer].

#### copycat-client

The `copycat-client` submodule provides a [RaftClient][RaftClient] interface for submitting [commands][Command]
and [queries][Query] to a cluster of [RaftServer][RaftServer]s. The client implementation includes full support
for linearizable commands via [sessions][Session].

### RaftClient

The [RaftClient][RaftClient] provides an interface for submitting [commands](#commands) and [queries](#queries) to a cluster
of [Raft servers](#raftserver).

To create a client, you must supply the client [Builder](#builders) with a set of `Members` to which to connect.

```java
Members members = Members.builder()
  .addMember(new Member(1, "123.456.789.1" 5555))
  .addMember(new Member(2, "123.456.789.2" 5555))
  .addMember(new Member(3, "123.456.789.3" 5555))
  .build();
```

The provided `Members` do not have to be representative of the full Copycat cluster, but they do have to provide at
least one correct server to which the client can connect. In other words, the client must be able to communicate with
at least one `RaftServer` that is the leader or can communicate with the leader, and a majority of the cluster
must be able to communicate with one another in order for the client to register a new [Session](#session).

```java
RaftClient client = RaftClient.builder()
  .withTransport(new NettyTransport())
  .withMembers(members)
  .build();
```

Once a `RaftClient` has been created, connect to the cluster by calling `open()` on the client:

```java
client.open().thenRun(() -> System.out.println("Successfully connected to the cluster!"));
```

#### Client lifecycle

When the client is opened, it will connect to a random server and attempt to register its session. If session registration fails,
the client will continue to attempt registration via random servers until all servers have been tried. If the session cannot be
registered, the `CompletableFuture` returned by `open()` will fail.

#### Client sessions

Once the client's session has been registered, the `Session` object can be accessed via `RaftClient.session()`.

The client will remain connected to the server through which the session was registered for as long as possible. If the server
fails, the client can reconnect to another random server and maintain its open session.

The `Session` object can be used to receive events `publish`ed by the server's `StateMachine`. To register a session event listener,
use the `onReceive` method:

```java
client.session().onReceive(message -> System.out.println("Received " + message));
```

When events are sent from a server state machine to a client via the `Session` object, only the server to which the client is
connected will send the event. Copycat servers guarantee that state machine events will be received by the client session in the
order in which they're sent even if the client switches servers.

### RaftServer

The [RaftServer][RaftServer] class is a feature complete implementation of the [Raft consensus algorithm][Raft].
`RaftServer` underlies all distributed resources supports by Copycat's high-level APIs.

The `RaftServer` class is provided in the `copycat-server` module:

```
<dependency>
  <groupId>net.kuujo.copycat</groupId>
  <artifactId>copycat-server</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

Each `RaftServer` consists of three essential components:
* [Transport](#transports) - Used to communicate with clients and other Raft servers
* [Storage](#storage) - Used to persist [commands](#commands) to memory or disk
* [StateMachine](#state-machines) - Represents state resulting from [commands](#commands) logged and replicated via Raft

To create a Raft server, use the server [Builder](#builders):

```java
RaftServer server = RaftServer.builder()
  .withMemberId(1)
  .withMembers(members)
  .withTransport(new NettyTransport())
  .withStorage(Storage.builder()
    .withStorageLevel(StorageLevel.MEMORY)
    .build())
  .withStateMachine(new MyStateMachine())
  .build();
```

Once the server has been created, call `open()` to start the server:

```java
server.open().thenRun(() -> System.out.println("Server started successfully!"));
```

The returned `CompletableFuture` will be completed once the server has connected to other members of
the cluster and, critically, discovered the cluster leader. See the [server lifecycle](#server-lifecycle)
for more information on how the server joins the cluster.

#### Server lifecycle

Copycat's Raft implementation supports dynamic membership changes designed to allow servers to arbitrarily join and leave the
cluster. When a `RaftServer` is configured, the `Members` list provided in the server configuration specifies some number of
servers to join to form a cluster. When the server is started, the server begins a series of steps to either join an existing
Raft cluster or start a new cluster:

* When the server starts, transition to a *join* state and attempt to join the cluster by sending a *join* request to each known
  `Member` of the cluster
* If, after an election timeout, the server has failed to receive a response to a *join* requests from any `Member` of the cluster,
  assume that the cluster doesn't exist and transition into the *follower* state
* Once a leader has been elected or otherwise discovered, complete the startup

When a member *joins* the cluster, a *join* request will ultimately be received by the cluster's leader. The leader will log and
replicate the joining member's configuration. Once the joined member's configuration has been persisted on a majority of the cluster,
the joining member will be notified of the membership change and transition to the *passive* state. While in the *passive* state,
the joining member cannot participate in votes but does receive *append* requests from the cluster leader. Once the leader has
determined that the joining member's log has caught up to its own (the joining node's log has the last committed entry at any given
point in time), the member is promoted to a full member via another replicated configuration change.

Once a node has fully joined the Raft cluster, in the event of a failure the quorum size will not change. To leave the cluster,
the `close()` method must be called on a `RaftServer` instance. When `close()` is called, the member will submit a *leave* request
to the leader. Once the leaving member's configuration has been removed from the cluster and the new configuration replicated and
committed, the server will complete the close.

### Commands

Commands are operations that modify the state machine state. When a command operation is submitted to the Copycat cluster,
the command is logged to disk or memory (depending on the [Storage](#storage) configuration) and replicated via the Raft consensus
protocol. Once the command has been stored on a majority cluster members, it will be applied to the server-side
[StateMachine](#state-machines) and the output will be returned to the client.

Commands are defined by implementing the `Command` interface:

```java
public class Set<T> implements Command<T> {
  private final String value;

  public Set(String value) {
    this.value = value;
  }

  /**
   * The value to set.
   */
  public String value() {
    return value;
  }
}
```

The [Command][Command] interface extends [Operation][Operation] which is `Serializable` and can be sent over the wire with no
additional configuration. However, for the best performance users should implement [CopycatSerializable][CopycatSerializable]
or register a [TypeSerializer][TypeSerializer] for the type. This will reduce the size of the serialized object and allow
Copycat's [Serializer](#serializer) to optimize class loading internally during deserialization.

### Queries

In contrast to commands which perform state change operations, queries are read-only operations which do not modify the
server-side state machine's state. Because read operations do not modify the state machine state, Copycat can optimize
queries according to read from certain nodes according to the configuration and [may not require contacting a majority
of the cluster in order to maintain consistency](#query-consistency). This means queries can significantly reduce disk and
network I/O depending on the query configuration, so it is strongly recommended that all read-only operations be implemented as queries.

To create a query, simply implement the [Query][Query] interface:

```java
public class Get<T> implements Query {
}
```

As with [Command][Command], [Query][Query] extends the base [Operation][Operation] interface which is `Serializable`. However,
for the best performance users should implement [CopycatSerializable][CopycatSerializable] or register a
[TypeSerializer][TypeSerializer] for the type.

#### Query consistency

By default, [queries](#queries) submitted to the Copycat cluster are guaranteed to be linearizable. Linearizable queries are
forwarded to the leader where the leader verifies its leadership with a majority of the cluster before responding to the request.
However, this pattern can be inefficient for applications with less strict read consistency requirements. In those cases, Copycat
allows [Query][Query] implementations to specify a `ConsistencyLevel` to control how queries are handled by the cluster.

To configure the consistency level for a `Query`, simply override the default `consistency()` getter:

```java
public class Get<T> implements Query {

  @Override
  public ConsistencyLevel consistency() {
    return Consistency.SERIALIZABLE;
  }

}
```

The consistency level returned by the overridden `consistency()` method amounts to a *minimum consistency requirement*.
In many cases, a `SERIALIZABLE` query can actually result in `LINEARIZABLE` read depending the server to which a client submits
queries, but clients can only rely on the configured consistency level.

Copycat provides four consistency levels:
* `ConsistencyLevel.LINEARIZABLE` - Provides guaranteed linearizability by forcing all reads to go through the leader and
  verifying leadership with a majority of the Raft cluster prior to the completion of all operations
* `ConsistencyLevel.LINEARIZABLE_LEASE` - Provides best-effort optimized linearizability by forcing all reads to go through the
  leader but allowing most queries to be executed without contacting a majority of the cluster so long as less than the
  election timeout has passed since the last time the leader communicated with a majority
* `ConsistencyLevel.SERIALIZABLE` - Provides serializable consistency by allowing clients to read from followers and ensuring
  that clients see state progress monotonically

### State machines

State machines are the server-side representation of state based on a series of [commands](#commands) and [queries](#queries)
submitted to the Raft cluster.

**All state machines must be deterministic**

Given the same commands in the same order, state machines must always arrive at the same state with the same output.

Non-deterministic state machines will break the guarantees of the Raft consensus algorithm. Each [server](#raftserver) in the
cluster must have *the same state machine*. When a command is submitted to the cluster, the command will be forwarded to the leader,
logged to disk or memory, and replicated to a majority of the cluster before being applied to the state machine, and the return
value for a given command or query is returned to the requesting client.

State machines are created by extending the base `StateMachine` class and overriding the `configure(StateMachineExecutor)` method:

```java
public class MyStateMachine extends StateMachine {

  @Override
  protected void configure(StateMachineExecutor executor) {
  
  }

}
```

Internally, state machines are backed by a series of entries in an underlying [log](#log). In the event of a crash and
recovery, state machine commands in the log will be replayed to the state machine. This is why it's so critical that state
machines be deterministic.

#### Registering operations

The `StateMachineExecutor` is a special [Context](#contexts) implemntation that is responsible for applying [commands](#commands)
and [queries](#queries) to the state machine. Operations are handled by registering callbacks on the provided `StateMachineExecutor`
in the `configure` method:

```java
@Override
protected void configure(StateMachineExecutor executor) {
  executor.register(SetCommand.class, this::set);
  executor.register(GetQuery.class, this::get);
}
```

#### Commits

As [commands](#commands) and [queries](#queries) are logged and replicated through the Raft cluster, they gain some metadata
that is not present in the original operation. By the time operations are applied to the state machine, they've gained valuable
information that is exposed in the [Commit][Commit] wrapper class:

* `Commit.index()` - The sequential index of the commit in the underlying `Log`. The index is guaranteed to increase monotonically
  as commands are applied to the state machine. However, because [queries](#queries) are not logged, they may duplicate the indices
  of commands.
* `Commit.time()` - The approximate `Instant` at which the commit was logged by the leader through which it was committed. The commit
  time is guaranteed never to decrease.
* `Commit.session()` - The [Session](#sessions) that submitted the operation to the cluster. This can be used to send events back
  to the client.
* `Commit.operation()` - The operation that was committed.

```java
protected Object get(Commit<GetQuery> commit) {
  return map.get(commit.operation().key());
}
```

#### Sessions

Sessions are representative of a single client's connection to the cluster. For each `Commit` applied to the state machine,
an associated `Session` is provided. State machines can use sessions to associate clients with state changes or even send
events back to the client through the session:

```java
protected Object put(Commit<PutCommand> commit) {
  commit.session().publish("putteded");
  return map.put(commit.operation().key(), commit.operation().value());
}
```

The `StateMachineContext` provides a view of the local server's state at the time a [command](#command) or [query](#queries)
is applied to the state machine. Users can use the context to access, for instance, the list of `Session`s currently registered
in the cluster.

To get the context, call the protected `context()` getter from inside the state machine:

```java
for (Session session : context().sessions()) {
  session.publish("Hello world!");
}
```

#### Commit cleaning

As commands are submitted to the cluster and applied to the Raft state machine, the underlying [log](#log) grows.
Without some mechanism to reduce the size of the log, the log would grow without bound and ultimately servers would
run out of disk space. Raft suggests a few different approaches of handling log compaction. Copycat uses the
[log cleaning](#log-cleaning) approach.

`Commit` objects are backed by entries in Copycat's replicated log. When a `Commit` is no longer needed by the
`StateMachine`, the state machine should clean the commit from Copycat's log by calling the `clean()` method:

```java
protected void remove(Commit<RemoveCommand> commit) {
  map.remove(commit.operation().key());
  commit.clean();
}
```

Internally, the `clean()` call will be proxied to Copycat's underlying log:

```java
log.clean(commit.index());
```

As commits are cleaned by the state machine, entries in the underlying log will be marked for deletion. *Note
that it is not safe to assume that once a commit is cleaned it is permanently removed from the log*. Cleaning
an entry only *marks* it for deletion, and the entry won't actually be removed from the log until a background
thread cleans the relevant log segment. This means in the event of a crash-recovery and replay of the log,
a previously `clean`ed commit may still exists. For this reason, if a commit is dependent on a prior commit,
state machines should only `clean` those commits if no prior related commits have been seen. (More on this
later)

Once the underlying `Log` has grown large enough, and once enough commits have been `clean`ed from the log,
a pool of background threads will carry out their task to rewrite segments of the log to remove commits
(entries) for which `clean()` has been called:

#### Deterministic scheduling

In addition to registering operation callbacks, the `StateMachineExecutor` also facilitates deterministic scheduling based on
the Raft replicated log.

```java
executor.schedule(() -> System.out.println("Every second"), Duration.ofSeconds(1), Duration.ofSeconds(1));
```

Because of the complexities of coordinating distributed systems, time does not advance at the same rate on all servers in
the cluster. What is essential, though, is that time-based callbacks be executed at the same point in the Raft log on all
nodes. In order to accomplish this, the leader writes an approximate `Instant` to the replicated log for each command.
When a command is applied to the state machine, the command's timestamp is used to invoke any outstanding scheduled callbacks.
This means the granularity of scheduled callbacks is limited by the minimum time between commands submitted to the cluster,
including session register and keep-alive requests. Thus, users should not rely on `StateMachineExecutor` scheduling for
accuracy.

### Raft implementation details

Copycat's implementation of the [Raft consensus algorithm][Raft] has been developed over a period of over two years. In most
cases, it closely follows the recommendations of the Diego Ongaro's [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf),
but sometimes it diverges from the norm. For instance, Raft dictates that all reads and writes be executed through the leader
node, but Copycat's Raft implementation supports per-request consistency levels that allow clients to sacrifice linearizability
and read from followers. Similarly, Raft literature recommends snapshots as the simplest approach to log compaction, but Copycat
prefers log cleaning to promote more consistent performance throughout the lifetime of a cluster.

It's important to note that when Copycat does diverge from the Raft norm, it does so using well-understood alternative
methods that are described in the Raft literature and frequently discussed on Raft discussion forums. Copycat does not
attempt to alter the fundamental correctness of the algorithm but rather extends it to promote usability in real-world
use cases.

The following documentation details Copycat's implementation of the Raft consensus algorithm and in particular the areas
in which the implementation diverges from the recommendations in Raft literature and the reasoning behind various decisions.

#### Clients

Copycat's Raft client is responsible for connecting to a Raft cluster and submitting [commands](#commands-1) and
[queries](#queries-1).

The pattern with which clients communicate with servers diverges slightly from that which is described in the Raft
literature. Copycat's Raft implementation uses client communication patterns that are closely modeled on those of
[ZooKeeper](https://zookeeper.apache.org/). Clients are designed to connect to and communicate with a single
server at a time. There is no correlation between the client and the Raft cluster's leader. In fact, clients never
even learn about the leader.

When a client is started, the client connects to a random server and attempts to [register a new session](#session-1).
If the registration fails, the client attempts to connect to another random server and register a new session again. In the
event that the client fails to register a session with any server, the client fails and must be restarted. Alternatively,
once the client successfully registers a session through a server, the client continues to submit [commands](#commands-1) and
[queries](#queries-1) through that server until a failure or shutdown event.

Once the client has successfully registered its session, it begins sending periodic *keep alive* requests to the cluster.
Clients are responsible for sending a keep alive request at an interval less than the cluster's *session timeout* to
ensure their session remains open.

If the server through which a client is communicating fails (the client detects a disconnection when sending a 
command, query, or keep alive request), the client will connect to another random server and immediately attempt to send
a new *keep alive* request. The client will continue attempting to commit a keep alive request until it locates another
live member of the Raft cluster.

#### Servers

Raft servers are responsible for participating in elections and replicating state machine [commands](#commands-1) and
[queries](#queries-1) through the Raft log.

Each Raft server maintains a single [Transport](#transport) *server* and *client* which is connected to each other
member of the Raft cluster at any given time. Each server uses a single-thread event loop internally to handle
requests. This reduces complexity and ensures that order is strictly enforced on handled requests.

#### State machines

Each server is configured with a [state machine](#state-machines-1) to which it applies committed [commands](#commands-1)
and [queries](#queries). State machines operations are executed in a separate *state machine* thread to ensure that
blocking state machine operations do not block the internal server event loop.

Servers maintain both an internal state machine and a user state machine. The internal state machine is responsible for
maintaining internal system state such as [sessions](#sessions-1) and [membership](#membership-changes) and applying
*commands* and *queries* to the user-provided `StateMachine`.

#### Elections

In addition to necessarily adhering to the typical Raft election process, Copycat's Raft implementation uses a pre-vote
protocol to improve availability after failures. The pre-vote protocol (described in section `4.2.3` of the
[Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf)) ensures that only followers that are eligible to
become leaders can participate in elections. When followers elections timeout, prior to transitioning to candidates and
starting a new election, each follower polls the rest of the cluster to determine whether their log is up-to-date. Only
followers with up-to-date logs will transition to *candidate* and begin a new election, thus ensuring that servers that
can't win an election cannot disrupt the election process by resetting election timeouts for servers that can win an election.

#### Commands

Copycat's Raft implementation separates the concept of *writes* from *reads* in order to optimize the handling of each.
*Commands* are state machine operations which alter the state machine state. All commands submitted to a Raft cluster are
proxied to the leader, written to disk, and replicated through the Raft log.

When the leader receives a command, it writes the command to the log along with a client provided *sequence number*,
the *session ID* of the session which submitted the command, and an approximate *timestamp*. Notably, the *timestamp* is
used to provide a deterministic approximation of time on which state machines can base time-based command handling like
TTLs or other timeouts.

There are certain scenarios where sequential consistency can be broken by clients submitting commands via disparate
followers. If a client submits a command to server `A` which forwards it to server `B` (the leader), and then switches
servers and submits a command to server `C` which also forwards it to server `B`, it is conceivable that the command
submitted to server `C` could reach the leader prior to the command submitted via server `A`. If those commands are
committed to the Raft log in the order in which they're received by the leader, that will violate sequential consistency
since state changes will no longer reflect the client's program order.

Because of the pattern with which clients communicate with servers, this may be an unlikely occurrence. Clients only
switch servers in the event of a server failure. Nevertheless, failures are when it is most critical that a systems
maintain their guarantees, so leaders are responsible for ensuring that commands received by a client are logged in
sequential order as specified by that client.

When a client submits a command to the cluster, it tags the command with a monotonically increasing *sequence* number.
The sequence number is used for two purposes. First, it is used to sequence commands as they're written to the Raft
log. If a leader receives a command with a sequence number greater than `1 + previousSequence` then the command request
will be queued for handling once the commands are properly sequenced. This ensures that commands are written to the
Raft log in the order in which they were sent by the client regardless of the route through which they travelled to the
leader.

Note, however, that commands are not rejected if the *sequence* number is less than that of commands previously submitted
by the client. The reasoning behind this is to handle a specific failure scenario. [Sessions](#sessions-1) provide linearizability
for commands submitted to the cluster by clients by using the same *sequence* number to store command output and deduplicate
commands as they're applied to the state machine. If a client submits a command to a server that fails, the client doesn't
necessarily know whether or not the command succeeded. Indeed, the command could have been replicated to a majority of the
cluster prior to the server failure. In that case, the command would ultimately be committed and applied to the state machine,
but the client would never receive the command output. Session-based linearizability ensures that clients can still read output
for commands resubmitted to the cluster, but that requires that leaders allow commands with old *sequence* numbers to be logged
and replicated.

Finally, [queries](#queries-1) are optionally allowed to read stale state from followers. In order to do so in a manner that
ensures serializability (state progresses monotonically) when the client switches between servers, the client needs to have a
view of the most recent state for which it has received output. When commands are committed and applied to the user-provided
state machine, command output is [cached in memory for linearizability](#sessions-1) and the command output returned to the
client along with the *index* of the command. Thereafter, when the client submits a query to a follower, it will ensure that
it does not see state go back in time by indicating to the follower the highest index for which it has seen state.

*For more on linearizable semantics, see the [sessions](#sessions-1) documentation*

#### Queries

*Queries* are state machine operations which read state machine state but do not alter it. This is critical because queries
are never logged to the Raft log or replicated. Instead, queries are applied either on a follower or the leader based on the
configured per-query *consistency level*.

When a query is submitted to the Raft cluster, as with all other requests the query request is sent to the server to which
the client is connected. The server that receives the query request will handle the query based on the query's configured
*consistency level*. If the server that receives the query request is not the leader, it will evaluate the request to
determine whether it needs to be proxied to the leader:

If the query is `LINEARIZABLE` or `LINEARIZABLE_LEASE`, the server will forward the query to the leader.

`LINEARIZABLE` queries are handled by the leader by contacting a majority of the cluster before servicing the query.
When the leader receives a linearizable read, if the leader is in the process of sending *AppendEntries* RPCs to followers
then the query is queued for the next heartbeat. On the next heartbeat iteration, once the leader has successfully contacted
a majority of the cluster, queued queries are applied to the user-provided state machine and the leader responds to their
respective requests with the state machine output. Batching queries during heartbeats reduces the overhead of synchronously
verifying the leadership during reads.

`LINEARIZABLE_LEASE` queries are handled by the leader under the assumption that once the leader has verified its leadership
with a majority of the cluster, it can assume that it will remain the leader for at least an election timeout. When a
lease-based linearizable query is received by the leader, it will check to determine the last time it verified its leadership
with a majority of the cluster. If more than an election timeout has elapsed since it contacted a majority of the cluster,
the leader will immediately attempt to verify its leadership before applying the query to the user-provided state machine.
Otherwise, if the leadership was verified within an election timeout, the leader will immediately apply the query to the
user-provided state machine and respond with the state machine output.

If the query is `SERIALIZABLE`, the receiving server performs a consistency check to ensure that its log is not too far
out-of-sync with the leader to reliably service a query. If the receiving server's log is in-sync, it will wait until
the log is caught up until the last index seen by the requesting client before servicing the query. When queries are
submitted to the cluster, the client provides a *version* number which specifies the highest index for which
it has seen a response. Awaiting that index when servicing queries on followers ensures that state does not go back
in time if a client switches servers. Once the server's state machine has caught up to the client's *version*
number, the server applies the query to its state machine and response with the state machine output.

Clients' *version* numbers are based on feedback received from the cluster when submitting commands and queries.
Clients receive *version* numbers for each command and query submitted to the cluster. When a client submits a command
to the cluster, the command's *index* in the Raft replicated log will be returned to the client along with the output. This
is the client's *version* number. Similarly, when a client submits a query to the cluster, the server that services the query
will respond with the query output and the server's *lastApplied* index as the *version* number.

Log consistency for inconsistent queries is determined  by checking whether the server's log's `lastIndex` is greater than
or equal to the `commitIndex`. That is, if the last *AppendEntries* RPC received by the server did not contain a `commitIndex`
less than or equal to the log's `lastIndex` after applying entries, the server is considered out-of-sync and queries are
forwarded to the leader.

#### Sessions

Copycat's Raft implementation uses sessions to provide linearizability for commands submitted to the cluster. Sessions
represent a connection between a `RaftClient` and a `RaftServer` and are responsible for tracking communication between
them.

Certain failure scenarios can conceivably result on client commands being applied to the state machine more than once. For
instance, if a client submits a command to the cluster and the leader logs and replicates the command before failing, the
command may actually be committed and applied to state machines on each node. In that case, if the client resubmits the
command to another node, the command will be applied twice to the state machine. Sessions solve this problem by temporarily
storing command output in memory and deduplicating commands as they're applied to the state machine.

##### How it works

When a client connects to Copycat's Raft cluster, the client chooses a random Raft server to which to connect and
submits a *register* request to the cluster. The *register* request is forwarded to the Raft cluster leader if one exists,
and the leader logs and replicates the registration through the Raft log. Entries are logged and replicated with an
approximate *timestamp* generated by the leader.

Once the *register* request has been committed, the leader replies to the request with the *index* of the registration
entry in the Raft log. Thereafter, the registration *index* becomes the globally unique *session ID*, and the client must
submit commands and queries using that index.

Once a session has been registered, the client must periodically submit *keep alive* requests to the Raft cluster. As with
*register* requests, *keep alive* requests are logged and replicated by the leader and ultimately applied to an internal
state machine. Keep alive requests also contain an additional `sequence` number which specifies the last command for which
the client received a successful response, but more on that in a moment.

Once a session has been registered, the client must submit all commands to the cluster with an active *session ID* and
a monotonically increasing *sequence number* for the session. The *session ID* is used to associate the command with a
set of commands stored in memory on the server, and the *sequence number* is used to deduplicate commands committed to the
Raft cluster. When commands are applied to the user-provided [state machine](#state-machines), the command output is stored
in an in-memory map of results. If a command is committed with a *sequence number* that has already been applied to the
state machine, the previous output will be returned to the client and the command will not be applied to the state machine
again.

On the client side, in addition to tagging requests with a monotonically increasing *sequence number*, clients store the
highest sequence number for which they've received a successful response. When a *keep alive* request is sent to the cluster,
the client sends the last sequence number for which they've received a successful response, thus allowing servers to remove
command output up to that number.

##### Server events

In addition to providing linearizable semantics for commands submitted to the cluster by clients, sessions are also used
to allow servers to send events back to clients. To do so, Copycat exposes a `Session` object to the Raft state machine for
each [command](#commands) or [query](#queries) applied to the state machine:

```java
protected Object get(Commit<GetQuery> commit) {
  commit.session().publish("got it!");
  return map.get(commit.operation().key());
}
```

Rather than connecting to the leader, Copycat's Raft clients connect to a random node and writes are proxied to the leader.
When an event is published to a client by a state machine, only the server to which the client is connected will send the
event ot the client, thus ensuring the client only receives one event from the cluster. In the event that the client is
disconnected from the cluster (e.g. switching servers), events published through sessions are linearized in a manner similar
to that of commands.

When an event is published to a client by a state machine, the event is queue in memory with a sequential ID for the session.
Clients keep track of the highest sequence number for which they've received an event and send that sequence number back to
the cluster via *keep alive* requests. As keep alive requests are logged and replicated, servers clear acknowledged events
from memory. This ensures that all servers hold unacknowledged events in memory until they've been received by the client
associated with a given session. In the event that a session times out, all events are removed from memory.

*For more information on sessions in Raft, see section 6.3 of Diego Ongaro's
[Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf)*

#### Membership changes

Membership changes are the process through which members are added to and removed from the Raft cluster. This is a notably
fragile process due to the nature of consensus. Raft requires that an entry be stored on a majority of servers in order to
be considered committed. But if new members are added to the cluster too quickly, this guarantee can be broken. If 3 members
are added to a 2-node cluster and immediately begin participating in the voting protocol, the three new members could potentially
form a consensus and any commands that were previously committed to the cluster (requiring `1` node for commitment) would no
longer be guaranteed to persist following an election.

Throughout the evolution of the Raft consensus algorithm, two major approaches to membership changes have been suggested
for handling membership changes. The approach originally suggested in Raft literature used joint-consensus to ensure that
two majorities could not overlap each other during a membership change. But more recent literature suggests adding or removing
a single member at a time in order to avoid the join-consensus problem altogether. Copycat takes the latter approach.

Copycat's configuration change algorithm is designed to allow servers to arbitrarily join and leave the cluster. When a cluster
is started for the first time, the configuration provided to each server at startup is used as the base cluster configuration.
Thereafter, servers that are joining the cluster are responsible for coordinating with the leader to join the cluster.

Copycat performs membership changes by adding two additional states to Raft servers: the *join* and *leave* states.
When a Raft server is started, the server first transitions into the *join* state. While in the join state, the server
attempts to determine whether a cluster is already available by attempting to contact a leader of the cluster. If the
server fails to contact a leader, it transitions into the *follower* state and continues with normal operation of the
Raft consensus protocol.

If a server in the *join* state does successfully contact a leader, it submits a *join* request to the leader, requesting
to join the cluster. The leader may or may not already know about the joining member. When the leader receives a *join*
request from a joining member, the leader immediately logs a *join* entry, updates its configuration, and replicates the
entry to the rest of the cluster.

The leader is responsible for maintaining two sets of members: *passive* members and *active* members. *Passive* members
are members that are in the process of joining the cluster but cannot yet participate in elections, but in all other functions,
including replication via *AppendEntries* RPCs, they function as normal Raft servers. The period in which a member is in
the *passive* state is intended to catch up the joining member's log enough that it can safely transition to a full member
of the cluster and participate in elections. The leader is responsible for determining when a *passive* member has caught
up to it based on the passive member's log. Once the passive member's log contains the last *commitIndex* sent to that member,
it is considered to be caught up. Once a member is caught up to the leader, the leader will log a second entry to the log
and replicate the configuration, resulting in the joining member being promoted to *active* state. Once the *passive* member
receives the configuration change, it transitions into the *follower* state and continues normal operation.

#### Log compaction

From the [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf):

> Raft’s log grows during normal operation as it incorporates more client requests. As it grows larger,
> it occupies more space and takes more time to replay. Without some way to compact the log, this
> will eventually cause availability problems: servers will either run out of space, or they will take too
> long to start. Thus, some form of log compaction is necessary for any practical system.

Raft literature suggests several ways to address the problem of logs growing unbounded. The most common of the log
compaction methodologies is snapshots. Snapshotting compacts the Raft log by storing a snapshot of the state machine
state and removing all commands applied to create that state. As simple as this sounds, though, there are some complexities.
Servers have to ensure that snapshots are reflective of a specific point in the log even while continuing to service
commands from clients. This may require that the process be forked for snapshotting or leaders step down prior to
taking a snapshot. Additionally, if a follower falls too far behind the leader (the follower's log's last index is
less than the leader's snapshot index), additional mechanisms are required to replicate snapshots from the leader to the
follower.

Alternative methods suggested in the Raft literature are mostly variations of log cleaning. Log cleaning is the process
of removing individual entries from the log once they no longer contribute to the state machine state. The disadvantage
of log cleaning - in particular for an abstract framework like Copycat - is that it adds additional complexity in requiring
state machines to keep track of commands that no longer apply to the state machine's state. This complexity is multiplied
by the delicacy handling tombstones. Commands that result in the absence of state must be carefully managed to ensure they're
applied on *all* Raft servers. Nevertheless, log cleaning provides significant performance advantages by writing logs
efficiently in long sequential strides.

Copycat opted to sacrifice some complexity to state machines in favor of more efficient log compaction. Copycat's Raft
log is written to a series of segment files and individually represent a subset of the entries in the log. As entries
are written to the log and associated commands are applied to the state machine, state machines are responsible for
explicitly cleaning the commits from the log. The log compaction algorithm is optimized to select segments based on the
number of commits marked for cleaning. Periodically, a series of background threads will rewrite segments of the
log in a thread-safe manner that ensures all segments can continue to be read and written. Whenever possible, neighboring
segments are combined into a single segment.

![Raft log compaction](http://s21.postimg.org/fvlvlg9lz/Raft_Compaction_New_Page_3.png)

*For more information on how commits are cleaned see the [log documentation](#log).*

This compaction model means that Copycat's Raft protocol must be capable of accounting for entries missing from the log.
When entries are replicated to a follower, each entry is replicated with its index so that the follower can write entries
to its own log in the proper sequence. Entries that are not present in a server's log or in an *AppendEntries* RPC are simply
skipped in the log. In order to maintain consistency, it is critical that state machines implement log cleaning correctly.

The most complex case for state machines to handle is tombstone commands. It's fairly simple to determine when a stateful
command has been superseded by a more recent command. For instance, consider this history:

```
put 1
put 3
```

In the scenario above, once the second `put` command has been applied to the state machine, it's safe to remove the first
`put` from the log. However, for commands that result in the absence of state (tombstones), cleaning the log is not as simple:

```
put 1
put 3
delete 3
```

In the scenario above, the first two `put` commands must be cleaned from the log before the final `delete` command can be
cleaned. If the `delete` is cleaned from the log prior to either `put` and the server fails and restarts, the state machine
will result in a non-deterministic state. Thus, state machines must ensure that commands that created state are cleaned
before a command that results in the absence of that state.

Furthermore, it is essential that the `delete` command be replicated on *all* servers in the cluster prior to being cleaned
from any log. If, for instance, a server is partitioned when the `delete` is committed, and the `delete` is cleaned from the
log prior to the partition healing, that server will never receive the tombstone and thus not clean all prior `put` commands.

Some systems like [Kafka](http://kafka.apache.org/) handle tombstones by aging them out of the log after a large interval
of time, meaning tombstones must be handled within a bounded timeframe. Copycat opts to ensure that tombstones have been
persisted on all servers prior to cleaning them from the log.

In order to handle log cleaning for tombstones, Copycat extends the Raft protocol to keep track of the highest index in the
log that has been replicated on *all* servers in the cluster. During normal *AppendEntries* RPCs, the leader sends a
*global index* which indicates the highest index represented on all servers in the cluster based on the leader's
`matchIndex` for each server. This global index represents the highest index for which tombstones can be safely removed from
the log.

Given the global index, state machines must use the index to determine when it's safe to remove a tombstone from the log.
But Copycat doesn't actually even expose the global index to the state machine. Instead, Copycat's state machines are designed
to clean tombstones only when there are no prior commits that contribute to the state being deleted by the tombstone. It does
so by periodically replaying globally committed commands to the state machine, allowing it to remove commits that have no
prior state.

Consider the tombstone history again:

```
put 1
put 3
delete 3
```

The first time that the final `delete` command is applied to the state machine, it will have marked the first two
`put` commands for deletion from the log. At some point in the future after segment to which the associated entries
belong are cleaned, the history in the log will contain only a single command:

```
delete 3
```

At that point, if commands are replayed to the state machine, the state machine will see that the `delete` does not
actually result in the absence of state since the state never existed to begin with. Each server in the cluster will
periodically replay early entries that have been persisted on all servers to a clone of the state machine to allow
it to clean tombstones that relate to invalid state. This is a clever way to clean tombstones from the log by essentially
*never* cleaning tombstones that delete state, and instead only cleaning tombstones that are essentially irrelevant.

*See chapter 5 of Diego Ongaro's [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf) for more on
log compaction*