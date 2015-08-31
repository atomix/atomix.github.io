---
layout: content
menu: user-manual
title: Raft consensus algorithm
---

# Raft implementation details

Copycat's implementation of the [Raft consensus algorithm][Raft] has been developed over a period of over two years. In most cases, it closely follows the recommendations of the Diego Ongaro's [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf), but sometimes it diverges from the norm. For instance, Raft dictates that all reads and writes be executed through the leader node, but Copycat's Raft implementation supports per-request consistency levels that allow clients to sacrifice linearizability and read from followers. Similarly, Raft literature recommends snapshots as the simplest approach to log compaction, but Copycat prefers log cleaning to promote more consistent performance throughout the lifetime of a cluster.

It's important to note that when Copycat does diverge from the Raft norm, it does so using well-understood alternative methods that are described in the Raft literature and frequently discussed on Raft discussion forums. Copycat does not attempt to alter the fundamental correctness of the algorithm but rather extends it to promote usability in real-world use cases.

The following documentation details Copycat's implementation of the Raft consensus algorithm and in particular the areas in which the implementation diverges from the recommendations in Raft literature and the reasoning behind various decisions.

## Clients

Copycat's Raft client is responsible for connecting to a Raft cluster and submitting [commands](#commands-1) and [queries](#queries-1).

The pattern with which clients communicate with servers diverges slightly from that which is described in the Raft literature. Copycat's Raft implementation uses client communication patterns that are closely modeled on those of [ZooKeeper](https://zookeeper.apache.org/). Clients are designed to connect to and communicate with a single server at a time. There is no correlation between the client and the Raft cluster's leader. In fact, clients never even learn about the leader.

![Client communication](http://s24.postimg.org/cnl5uo6hh/IMG_0006.png)

This illustration depicts the pattern in which clients communicate with Copycat's Raft cluster. Each client connects to a random server in the cluster and submits commands and queries through that server. Clients make every attempt to remain connected to the same server, but may switch servers if the one to which they're connected dies, is partitioned from the leader, or is otherwise behaving poorly (based on timeouts).

When a client is started, the client connects to a random server and attempts to [register a new session](#session-1). If the registration fails, the client attempts to connect to another random server and register a new session again. In the event that the client fails to register a session with any server, the client fails and must be restarted. Alternatively, once the client successfully registers a session through a server, the client continues to submit [commands](#commands-1) and [queries](#queries-1) through that server until a failure or shutdown event.

Once the client has successfully registered its session, it begins sending periodic *keep alive* requests to the cluster. Clients are responsible for sending a keep alive request at an interval less than the cluster's *session timeout* to ensure their session remains open.

If the server through which a client is communicating fails (the client detects a disconnection when sending a command, query, or keep alive request), the client will connect to another random server and immediately attempt to send a new *keep alive* request. The client will continue attempting to commit a keep alive request until it locates another live member of the Raft cluster.

## Servers

Raft servers are responsible for participating in elections and replicating state machine [commands](#commands-1) and [queries](#queries-1) through the Raft log.

Each Raft server maintains a single [Transport](#transport) *server* and *client* which is connected to each other member of the Raft cluster at any given time. Each server uses a single-thread event loop internally to handle requests. This reduces complexity and ensures that order is strictly enforced on handled requests.

## State machines

Each server is configured with a [state machine](#state-machines-1) to which it applies committed [commands](#commands-1) and [queries](#queries). State machines operations are executed in a separate *state machine* thread to ensure that blocking state machine operations do not block the internal server event loop.

Servers maintain both an internal state machine and a user state machine. The internal state machine is responsible for maintaining internal system state such as [sessions](#sessions-1) and [membership](#membership-changes) and applying *commands* and *queries* to the user-provided `StateMachine`.

## Elections

Copycat's Raft implementation relies on a typical implementation of Raft's election protocol to elect a leader for the cluster.
Leaders are responsible for receiving and replicating state changes (i.e. [commands](#commands)) to followers.

![Raft cluster](http://s24.postimg.org/3jrc7yuad/IMG_0007.png)

This illustration depicts the structure of a Raft cluster.

In addition to necessarily adhering to the typical Raft election process, Copycat's Raft implementation uses a pre-vote protocol to improve availability after failures. The pre-vote protocol (described in section `4.2.3` of the [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf)) ensures that only followers that are eligible to become leaders can participate in elections. When followers elections timeout, prior to transitioning to candidates and starting a new election, each follower polls the rest of the cluster to determine whether their log is up-to-date. Only followers with up-to-date logs will transition to *candidate* and begin a new election, thus ensuring that servers that can't win an election cannot disrupt the election process by resetting election timeouts for servers that can win an election.

## Commands

Copycat's Raft implementation separates the concept of *writes* from *reads* in order to optimize the handling of each. *Commands* are state machine operations which alter the state machine state. All commands submitted to a Raft cluster are proxied to the leader, written to disk, and replicated through the Raft log.

![Client commands](http://s24.postimg.org/y8q8ia385/IMG_0010.png)

This illustration depicts the route through which commands travel in the cluster. Commands are submitted to the server to which the client is connected and forwarded to the leader for persistence and replication.
 
When the leader receives a command, it writes the command to the log along with a client provided *sequence number*, the *session ID* of the session which submitted the command, and an approximate *timestamp*. Notably, the *timestamp* is used to provide a deterministic approximation of time on which state machines can base time-based command handling like TTLs or other timeouts.

There are certain scenarios where sequential consistency can be broken by clients submitting commands via disparate followers. If a client submits a command to server `A` which forwards it to server `B` (the leader), and then switches servers and submits a command to server `C` which also forwards it to server `B`, it is conceivable that the command submitted to server `C` could reach the leader prior to the command submitted via server `A`. If those commands are committed to the Raft log in the order in which they're received by the leader, that will violate sequential consistency since state changes will no longer reflect the client's program order.
 
Because of the pattern with which clients communicate with servers, this may be an unlikely occurrence. Clients only switch servers in the event of a server failure. Nevertheless, failures are when it is most critical that a systems maintain their guarantees, so leaders are responsible for ensuring that commands received by a client are logged in sequential order as specified by that client.

When a client submits a command to the cluster, it tags the command with a monotonically increasing *sequence* number. The sequence number is used for two purposes. First, it is used to sequence commands as they're written to the Raft log. If a leader receives a command with a sequence number greater than `1 + previousSequence` then the command request will be queued for handling once the commands are properly sequenced. This ensures that commands are written to the Raft log in the order in which they were sent by the client regardless of the route through which they travelled to the leader.

Note, however, that commands are not rejected if the *sequence* number is less than that of commands previously submitted by the client. The reasoning behind this is to handle a specific failure scenario. [Sessions](#sessions-1) provide linearizability for commands submitted to the cluster by clients by using the same *sequence* number to store command output and deduplicate commands as they're applied to the state machine. If a client submits a command to a server that fails, the client doesn't necessarily know whether or not the command succeeded. Indeed, the command could have been replicated to a majority of the cluster prior to the server failure. In that case, the command would ultimately be committed and applied to the state machine, but the client would never receive the command output. Session-based linearizability ensures that clients can still read output for commands resubmitted to the cluster, but that requires that leaders allow commands with old *sequence* numbers to be logged and replicated.

Finally, [queries](#queries-1) are optionally allowed to read stale state from followers. In order to do so in a manner that ensures serializability (state progresses monotonically) when the client switches between servers, the client needs to have a view of the most recent state for which it has received output. When commands are committed and applied to the user-provided state machine, command output is [cached in memory for linearizability](#sessions-1) and the command output returned to the client along with the *index* of the command. Thereafter, when the client submits a query to a follower, it will ensure that it does not see state go back in time by indicating to the follower the highest index for which it has seen state.

*For more on linearizable semantics, see the [sessions](#sessions-1) documentation*

## Queries

*Queries* are state machine operations which read state machine state but do not alter it. This is critical because queries are never logged to the Raft log or replicated. Instead, queries are applied either on a follower or the leader based on the configured per-query *consistency level*.

When a query is submitted to the Raft cluster, as with all other requests the query request is sent to the server to which the client is connected. The server that receives the query request will handle the query based on the query's configured *consistency level*. If the server that receives the query request is not the leader, it will evaluate the request to determine whether it needs to be proxied to the leader:

If the query is `LINEARIZABLE` or `LINEARIZABLE_LEASE`, the server will forward the query to the leader.

![Consistent queries](http://s24.postimg.org/y8q8ia385/IMG_0010.png)

This illustration depicts the route through which linearizable queries travel in Copycat's Raft cluster. Linearizable queries are submitted to the server to which the client is connected and forwarded to the leader for evaluation.

`LINEARIZABLE` queries are handled by the leader by contacting a majority of the cluster before servicing the query. When the leader receives a linearizable read, if the leader is in the process of sending *AppendEntries* RPCs to followers then the query is queued for the next heartbeat. On the next heartbeat iteration, once the leader has successfully contacted a majority of the cluster, queued queries are applied to the user-provided state machine and the leader responds to their respective requests with the state machine output. Batching queries during heartbeats reduces the overhead of synchronously verifying the leadership during reads.

`LINEARIZABLE_LEASE` queries are handled by the leader under the assumption that once the leader has verified its leadership with a majority of the cluster, it can assume that it will remain the leader for at least an election timeout. When a lease-based linearizable query is received by the leader, it will check to determine the last time it verified its leadership with a majority of the cluster. If more than an election timeout has elapsed since it contacted a majority of the cluster, the leader will immediately attempt to verify its leadership before applying the query to the user-provided state machine. Otherwise, if the leadership was verified within an election timeout, the leader will immediately apply the query to the user-provided state machine and respond with the state machine output.

![Inconsistent queries](http://s24.postimg.org/5ln88h2vp/IMG_0011.png)

This illustration depicts the route through which serializable (potentially stale) queries travel in Copycat's Raft cluster. Serializable queries are evaluated directly on the server to which the client is connected.

If the query is `SERIALIZABLE`, the receiving server performs a consistency check to ensure that its log is not too far out-of-sync with the leader to reliably service a query. If the receiving server's log is in-sync, it will wait until the log is caught up until the last index seen by the requesting client before servicing the query. When queries are submitted to the cluster, the client provides a *version* number which specifies the highest index for which it has seen a response. Awaiting that index when servicing queries on followers ensures that state does not go back in time if a client switches servers. Once the server's state machine has caught up to the client's *version* number, the server applies the query to its state machine and response with the state machine output.

Clients' *version* numbers are based on feedback received from the cluster when submitting commands and queries. Clients receive *version* numbers for each command and query submitted to the cluster. When a client submits a command to the cluster, the command's *index* in the Raft replicated log will be returned to the client along with the output. This is the client's *version* number. Similarly, when a client submits a query to the cluster, the server that services the query will respond with the query output and the server's *lastApplied* index as the *version* number.

Log consistency for inconsistent queries is determined  by checking whether the server's log's `lastIndex` is greater than or equal to the `commitIndex`. That is, if the last *AppendEntries* RPC received by the server did not contain a `commitIndex` less than or equal to the log's `lastIndex` after applying entries, the server is considered out-of-sync and queries are forwarded to the leader.

## Sessions

Copycat's Raft implementation uses sessions to provide linearizability for commands submitted to the cluster. Sessions represent a connection between a `RaftClient` and a `RaftServer` and are responsible for tracking communication between them.

Certain failure scenarios can conceivably result on client commands being applied to the state machine more than once. For instance, if a client submits a command to the cluster and the leader logs and replicates the command before failing, the command may actually be committed and applied to state machines on each node. In that case, if the client resubmits the command to another node, the command will be applied twice to the state machine. Sessions solve this problem by temporarily storing command output in memory and deduplicating commands as they're applied to the state machine.

### How it works

When a client connects to Copycat's Raft cluster, the client chooses a random Raft server to which to connect and submits a *register* request to the cluster. The *register* request is forwarded to the Raft cluster leader if one exists, and the leader logs and replicates the registration through the Raft log. Entries are logged and replicated with an approximate *timestamp* generated by the leader.

Once the *register* request has been committed, the leader replies to the request with the *index* of the registration entry in the Raft log. Thereafter, the registration *index* becomes the globally unique *session ID*, and the client must submit commands and queries using that index.

Once a session has been registered, the client must periodically submit *keep alive* requests to the Raft cluster. As with *register* requests, *keep alive* requests are logged and replicated by the leader and ultimately applied to an internal state machine. Keep alive requests also contain an additional `sequence` number which specifies the last command for which the client received a successful response, but more on that in a moment.

Once a session has been registered, the client must submit all commands to the cluster with an active *session ID* and a monotonically increasing *sequence number* for the session. The *session ID* is used to associate the command with a set of commands stored in memory on the server, and the *sequence number* is used to deduplicate commands committed to the Raft cluster. When commands are applied to the user-provided [state machine](#state-machines), the command output is stored in an in-memory map of results. If a command is committed with a *sequence number* that has already been applied to the state machine, the previous output will be returned to the client and the command will not be applied to the state machine again.
 
On the client side, in addition to tagging requests with a monotonically increasing *sequence number*, clients store the highest sequence number for which they've received a successful response. When a *keep alive* request is sent to the cluster, the client sends the last sequence number for which they've received a successful response, thus allowing servers to remove command output up to that number.

### Server events

In addition to providing linearizable semantics for commands submitted to the cluster by clients, sessions are also used to allow servers to send events back to clients. To do so, Copycat exposes a `Session` object to the Raft state machine for each [command](#commands) or [query](#queries) applied to the state machine:

```java
protected Object get(Commit<GetQuery> commit) {
  commit.session().publish("got it!");
  return map.get(commit.operation().key());
}
```

Rather than connecting to the leader, Copycat's Raft clients connect to a random node and writes are proxied to the leader. When an event is published to a client by a state machine, only the server to which the client is connected will send the event ot the client, thus ensuring the client only receives one event from the cluster.

![Session events](http://s24.postimg.org/9w1w427yt/IMG_0012.png)

This illustration depicts the how session events can be produced to one client or set of clients based on the input of another client, similar to a message queue. The client furthest to the left submits a command to the cluster, and once the command is applied to the server on the right, the two clients connected to it receive a `publish`ed event.

In the event that the client is disconnected from the cluster (e.g. switching servers), events published through sessions are linearized in a manner similar to that of commands.

When an event is published to a client by a state machine, the event is queue in memory with a sequential ID for the session. Clients keep track of the highest sequence number for which they've received an event and send that sequence number back to the cluster via *keep alive* requests. As keep alive requests are logged and replicated, servers clear acknowledged events from memory. This ensures that all servers hold unacknowledged events in memory until they've been received by the client associated with a given session. In the event that a session times out, all events are removed from memory.

*For more information on sessions in Raft, see section 6.3 of Diego Ongaro's [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf)*

## Membership changes

Membership changes are the process through which members are added to and removed from the Raft cluster. This is a notably fragile process due to the nature of consensus. Raft requires that an entry be stored on a majority of servers in order to be considered committed. But if new members are added to the cluster too quickly, this guarantee can be broken. If 3 members are added to a 2-node cluster and immediately begin participating in the voting protocol, the three new members could potentially form a consensus and any commands that were previously committed to the cluster (requiring `1` node for commitment) would no longer be guaranteed to persist following an election.

Throughout the evolution of the Raft consensus algorithm, two major approaches to membership changes have been suggested for handling membership changes. The approach originally suggested in Raft literature used joint-consensus to ensure that two majorities could not overlap each other during a membership change. But more recent literature suggests adding or removing a single member at a time in order to avoid the join-consensus problem altogether. Copycat takes the latter approach.

Copycat's configuration change algorithm is designed to allow servers to arbitrarily join and leave the cluster. When a cluster is started for the first time, the configuration provided to each server at startup is used as the base cluster configuration. Thereafter, servers that are joining the cluster are responsible for coordinating with the leader to join the cluster.

Copycat performs membership changes by adding two additional states to Raft servers: the *join* and *leave* states. When a Raft server is started, the server first transitions into the *join* state. While in the join state, the server attempts to determine whether a cluster is already available by attempting to contact a leader of the cluster. If the server fails to contact a leader, it transitions into the *follower* state and continues with normal operation of the Raft consensus protocol.

If a server in the *join* state does successfully contact a leader, it submits a *join* request to the leader, requesting to join the cluster. The leader may or may not already know about the joining member. When the leader receives a *join* request from a joining member, the leader immediately logs a *join* entry, updates its configuration, and replicates the entry to the rest of the cluster.

The leader is responsible for maintaining two sets of members: *passive* members and *active* members. *Passive* members are members that are in the process of joining the cluster but cannot yet participate in elections, but in all other functions, including replication via *AppendEntries* RPCs, they function as normal Raft servers. The period in which a member is in the *passive* state is intended to catch up the joining member's log enough that it can safely transition to a full member of the cluster and participate in elections. The leader is responsible for determining when a *passive* member has caught up to it based on the passive member's log. Once the passive member's log contains the last *commitIndex* sent to that member, it is considered to be caught up. Once a member is caught up to the leader, the leader will log a second entry to the log and replicate the configuration, resulting in the joining member being promoted to *active* state. Once the *passive* member receives the configuration change, it transitions into the *follower* state and continues normal operation.

## Log compaction

From the [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf):

> Raft’s log grows during normal operation as it incorporates more client requests. As it grows larger, it occupies more space and takes more time to replay. Without some way to compact the log, this will eventually cause availability problems: servers will either run out of space, or they will take too long to start. Thus, some form of log compaction is necessary for any practical system.

Raft literature suggests several ways to address the problem of logs growing unbounded. The most common of the log compaction methodologies is snapshots. Snapshotting compacts the Raft log by storing a snapshot of the state machine state and removing all commands applied to create that state. As simple as this sounds, though, there are some complexities. Servers have to ensure that snapshots are reflective of a specific point in the log even while continuing to service commands from clients. This may require that the process be forked for snapshotting or leaders step down prior to taking a snapshot. Additionally, if a follower falls too far behind the leader (the follower's log's last index is less than the leader's snapshot index), additional mechanisms are required to replicate snapshots from the leader to the follower.

Alternative methods suggested in the Raft literature are mostly variations of log cleaning. Log cleaning is the process of removing individual entries from the log once they no longer contribute to the state machine state. The disadvantage of log cleaning - in particular for an abstract framework like Copycat - is that it adds additional complexity in requiring state machines to keep track of commands that no longer apply to the state machine's state. This complexity is multiplied by the delicacy handling tombstones. Commands that result in the absence of state must be carefully managed to ensure they're applied on *all* Raft servers. Nevertheless, log cleaning provides significant performance advantages by writing logs efficiently in long sequential strides.

Copycat opted to sacrifice some complexity to state machines in favor of more efficient log compaction. Copycat's Raft log is written to a series of segment files and individually represent a subset of the entries in the log. As entries are written to the log and associated commands are applied to the state machine, state machines are responsible for explicitly cleaning the commits from the log. The log compaction algorithm is optimized to select segments based on the number of commits marked for cleaning. Periodically, a series of background threads will rewrite segments of the log in a thread-safe manner that ensures all segments can continue to be read and written. Whenever possible, neighboring segments are combined into a single segment.

![Raft log compaction](http://s21.postimg.org/fvlvlg9lz/Raft_Compaction_New_Page_3.png)

*For more information on how commits are cleaned see the [log documentation](#log).*

This compaction model means that Copycat's Raft protocol must be capable of accounting for entries missing from the log. When entries are replicated to a follower, each entry is replicated with its index so that the follower can write entries to its own log in the proper sequence. Entries that are not present in a server's log or in an *AppendEntries* RPC are simply skipped in the log. In order to maintain consistency, it is critical that state machines implement log cleaning correctly.

The most complex case for state machines to handle is tombstone commands. It's fairly simple to determine when a stateful command has been superseded by a more recent command. For instance, consider this history:

```
put 1
put 3
```

In the scenario above, once the second `put` command has been applied to the state machine, it's safe to remove the first `put` from the log. However, for commands that result in the absence of state (tombstones), cleaning the log is not as simple:

```
put 1
put 3
delete 3
```

In the scenario above, the first two `put` commands must be cleaned from the log before the final `delete` command can be cleaned. If the `delete` is cleaned from the log prior to either `put` and the server fails and restarts, the state machine will result in a non-deterministic state. Thus, state machines must ensure that commands that created state are cleaned before a command that results in the absence of that state.

Furthermore, it is essential that the `delete` command be replicated on *all* servers in the cluster prior to being cleaned from any log. If, for instance, a server is partitioned when the `delete` is committed, and the `delete` is cleaned from the log prior to the partition healing, that server will never receive the tombstone and thus not clean all prior `put` commands.

Some systems like [Kafka](http://kafka.apache.org/) handle tombstones by aging them out of the log after a large interval of time, meaning tombstones must be handled within a bounded timeframe. Copycat opts to ensure that tombstones have been persisted on all servers prior to cleaning them from the log.

In order to handle log cleaning for tombstones, Copycat extends the Raft protocol to keep track of the highest index in the log that has been replicated on *all* servers in the cluster. During normal *AppendEntries* RPCs, the leader sends a *global index* which indicates the highest index represented on all servers in the cluster based on the leader's `matchIndex` for each server. This global index represents the highest index for which tombstones can be safely removed from the log.

Given the global index, state machines must use the index to determine when it's safe to remove a tombstone from the log. But Copycat doesn't actually even expose the global index to the state machine. Instead, Copycat's state machines are designed to clean tombstones only when there are no prior commits that contribute to the state being deleted by the tombstone. It does so by periodically replaying globally committed commands to the state machine, allowing it to remove commits that have no prior state.

Consider the tombstone history again:

```
put 1
put 3
delete 3
```

The first time that the final `delete` command is applied to the state machine, it will have marked the first two `put` commands for deletion from the log. At some point in the future after segment to which the associated entries belong are cleaned, the history in the log will contain only a single command:

```
delete 3
```

At that point, if commands are replayed to the state machine, the state machine will see that the `delete` does not actually result in the absence of state since the state never existed to begin with. Each server in the cluster will periodically replay early entries that have been persisted on all servers to a clone of the state machine to allow it to clean tombstones that relate to invalid state. This is a clever way to clean tombstones from the log by essentially *never* cleaning tombstones that delete state, and instead only cleaning tombstones that are essentially irrelevant.

*See chapter 5 of Diego Ongaro's [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf) for more on log compaction*

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