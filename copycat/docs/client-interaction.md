---
layout: docs
project: copycat
menu: docs
title: Client Interaction
pitch: Raft architecture and implementation
first-section: client-interaction
---

<h2 id="client-interaction">3 Client Interaction</h2>

The basic Raft consensus algorithm dictates that clients should communicate directly with the leader to submit reads and writes to the cluster. The leader services writes by committing commands to the Raft log, and in linearizable systems the leader services reads by synchronously verifying its leadership with a majority of the cluster before applying them to the state machine. But practical systems can benefit from relaxed consistency models, and indeed the Raft literature does describe some ways to achieve this. Clients can submit read-only queries to followers without losing sequential consistency. In fact, there are even ways to make reads on followers linearizable, albeit at significant cost.

Typically, clients will initially connect to a pseudo-random server to register their session and then reconnect to the leader once it has been discovered. In the event that the client cannot locate a leader it continues to retry against random servers until one is found. In Copycat, client connections are spread across the cluster by default. Clients are allowed to connect to any server, and clients are responsible for choosing a server. Once connected to a server, clients try to maintain their connections for as long as possible. Reducing the frequency with which clients switch servers improves latency in bi-directional communication between clients and servers since servers typically know the route through which a client can be reached.

<h3 id="sessions">3.1 Sessions</h3>

Clients interact with the cluster within the context of a session. Sessions provide a mechanism through which interactions between a single client and the cluster can be managed. Once a session is registered by a client, all future interactions between the client and any server are associated with the client's session. Sessions aid in sequencing client operations for FIFO ordering, providing linearizable semantics for operations submitted multiple times, and notifying clients about changes in state machine state.

Clients' sessions are managed through the Raft log and state machine, affording servers a deterministic view of the active sessions in the cluster. Sessions are registered by committing an entry to the Raft log and kept alive over time with periodic commits. In the event that a client fails to keep its session alive, each server will expire the client's session deterministically.

<h3 id="session-lifecycle-management">3.2 Session Life-Cycle Management</h3>

Client sessions are managed through entries committed to the Raft log and applied to internal server state machines. When a client first connects to a cluster, the client connects to a random server and attempts to register a new session. If the registration fails, the client attempts to connect to another random server and register a new session again. In the event that the client fails to register a session with any server, the client fails and must be restarted. Alternatively, once the client successfully registers a session through a server, the client continues to submit commands and queries through that server until a failure or shutdown event.

Once the client has successfully registered its session, it begins sending periodic *keep-alive* requests to the cluster. Clients are responsible for sending a keep alive request at an interval less than the cluster's session timeout to ensure their session remains open. *Keep-alive* requests are written to the Raft log as special entries and replicated and committed. This gives state machines a consistent view of the active sessions and allows servers to timeout sessions deterministically.

If the server through which a client is communicating fails (the client detects a disconnection when sending a command, query, or keep-alive request), the client will connect to another random server and immediately attempt to send a new keep alive request. The client will continue attempting to commit a keep alive request until it locates another live member of the Raft cluster.

<h3 id="client-commands">3.3 Commands</h3>

Copycat's Raft implementation separates the concept of writes from reads in order to optimize the handling of each. Commands are state machine operations which alter the state machine state. All commands submitted to a Raft cluster are proxied to the leader, written to disk, and replicated through the Raft log.

When the leader receives a command, it writes the command to the log along with a client provided sequence number, the session ID of the session which submitted the command, and an approximate timestamp. Notably, the timestamp is used to provide a deterministic approximation of time with which state machines can support time-based command handling like TTLs or other timeouts.

<h4 id="preserving-program-order">3.3.1 Preserving Program Order</h4>

There are certain scenarios where sequential consistency can be broken by clients submitting concurrent commands via disparate followers. If a client submits a command to server `A` which forwards it to server `B` (the leader), and then before receiving a reply switches servers and submits a command to server `C` which also forwards it to server `B`, it is conceivable that the command submitted to server `C` could reach the leader prior to the command submitted via server `A`. If those commands are committed to the Raft log in the order in which they're received by the leader, that will violate sequential consistency since state changes will no longer reflect the client's program order.

Because of the pattern with which clients communicate with servers, this may be an unlikely occurrence. Clients only switch servers in the event of a server failure. Nevertheless, failures are when it is most critical that systems maintain their guarantees, so servers ensure that commands are applied in the order in which they were sent by the client regardless of the order in which they were received by the leader.

When the leader receives a command, it sequences the command based on the current session state and the sequence number provided in the request. The basic algorithm is as follows:

* If the command `sequence` number is greater than the next expected sequence number for the session, queue the request to be handled in sequence
* Otherwise, write the command to the log and commit it (no need to log again)
* Once the command has been written to the log, handle any queued commands for `sequence + 1`

<h4 id="linearizable-semantics">3.3.2 Linearizable Semantics</h4>

Sequence numbers are also used to provide linearizability for commands submitted to the cluster by clients by storing command output by sequence number and deduplicating commands as they're applied to the state machine. If a client submits a command to a server but disconnects from the server before receiving a response, or if the server to which the client submitted the command itself fails, the client doesn't necessarily know whether or not the command succeeded. Indeed, the command could have been replicated to a majority of the cluster prior to the server failure. In that case, the command would ultimately be committed and applied to the state machine, but the client may never receive the command output. Session-based linearizability ensures that clients can still read output for commands resubmitted to the cluster. Servers simply log and commit all commands submitted to the cluster, and in the event a command from the same client with the same sequence number is applied to the state machine more than once, the state machine returns the result from the original application of the command, thus preventing it from being applied multiple times. Effectively, state machines in Copycat are idempotent.

<h3 id="client-queries">3.4 Queries</h3>

Queries are state machine operations which read state machine state but do not alter it. This is critical because queries are never logged to the Raft log or replicated. Instead, queries are applied either on a follower or the leader based on the configured per-query consistency level.

When a query is submitted to the Raft cluster, as with all other requests the query request is sent to the server to which the client is connected. The server that receives the query request will handle the query based on the query's configured consistency level. If the server that receives the query request is not the leader, it will evaluate the request to determine whether it needs to be proxied to the leader:

Queries are optionally allowed to read stale state from followers. In order to do so in a manner that maintains sequential consistency (clients see state progress monotonically) when the client switches between servers, the client needs to have a view of the most recent state for which it has received output. When commands are committed and applied to the user-provided state machine, command output is cached in memory for linearizability and the command output returned to the client along with the index of the command. Thereafter, when the client submits a query to a follower, it will ensure that it does not see state go back in time by indicating to the follower the highest index for which it has seen state.

<h4 id="processing-queries-on-followers">3.4.1 Processing Queries on Followers</h4>

When queries are submitted to the cluster, the client specifies the highest `index` for which it has received a response. Awaiting that index when servicing queries on followers ensures that state does not go back in time if a client switches servers. Once the server's state machine has caught up to the client's `index`, the server applies the query to its state machine and responds with the state machine output.

Clients' indexes are based on feedback received from the cluster when submitting commands and queries. Clients receive indexes for each command and query submitted to the cluster. When a client submits a command to the cluster, the command's index in the Raft replicated log will be returned to the client along with the output. This is the client's last read index. Similarly, when a client submits a query to the cluster, the server that services the query will respond with the query output and the server's `lastApplied` index as the read index.

Log consistency for inconsistent queries is determined by checking whether the server's log's `lastIndex` is greater than or equal to the `commitIndex`. That is, if the last *AppendEntries* RPC received by the server did not contain a `commitIndex` less than or equal to the log's `lastIndex` after applying entries, the server is considered out-of-sync and queries are forwarded to the leader.

<h4 id="ensuring-state-progresses-monotonically">3.4.2 Ensuring State Progresses Monotonically</h4>

While Copycat allows clients' queries to be processed on followers and ensures sequential consistency even when switching servers, in some cases this can still result in significant delay. If a client switches to a server that is far behind its previous server, it can block the client's queries for some indeterminate amount of time. Clients should place an upper-bound on the amount of time within which a query must be handled by a server. If a query request times out, the client should switch to a new server and resubmit the query. All operations submitted to the cluster are idempotent and guaranteed to be sequentially consistent, so there's no risk of loss of consistency using this approach. But servers also have a mechanism to reject queries from clients if their state is too far behind. When a follower receives a query from a client, it checks to determine whether the last known `commitIndex` is present in its log. If the follower's last log index is less than the `commitIndex`, it forwards the query to the leader.

<h3 id="session-expiration">3.5 Session Expiration</h3>

When a new session is [registered](#session-lifecycle-management), the session is assigned a timeout. The session timeout is the time after which the session may be expired by the cluster. Clients are responsible for submitting keep alive requests to the cluster at intervals less than the session timeout. State machines determine when sessions time out based on the state machine time elapsed since the last keep-alive for a given session. Note that this depends on the existence of some mechanism for managing a deterministic representation of time in the state machine. In Copycat, this is done by writing the leader's timestamp to a variety of log entries.

<h3 id="replicating-server-configurations">3.6 Replicating Server Configurations</h3>

When a session is [registered](#session-lifecycle-management) with Copycat cluster, the client begins submitting periodic keep-alive requests to the cluster according to the configured session timeout. However, session timeouts may be configured differently on each server. In order to account for inconsistencies in session configurations in the cluster, we append the leader's configured session timeout to the log entry registering the session. When a session registration is applied to internal state machines, the state machines set the session timeout based on the timeout in the log rather than their local server configuration. This ensures that all servers have a consistent view of timeouts for each individual session and can therefore expire sessions deterministically. Once a `RegisterEntry` is committed and a new session is registered, the leader sends the logged timeout back to the client.

Alternatively, servers could replicate their session timeouts in special configuration change entries. This could allow servers' session timeouts to be reconfigured without impacting existing sessions. Servers would still have to provide a session timeout in keep-alive responses. When a leader logged and committed a keep-alive entry, it would respond with the next keep-alive interval based on the last committed session timeout.

<h3 id="ensuring-time-progresses-monotonically">3.7 Ensuring Time Progresses Monotonically</h3>

Sessions are expired in the internal state machine on each server based on log times. In Copycat, all session-related entries are written to the log with the leader's timestamp. The timestamp is used as an approximation of wall-clock time in the state machine. We assume that a leader change can result in log time decreasing; a new leader may log an entry with a timestamp prior to the last timestamp logged by the previous leader. Thus, in order to ensure that state machine time progresses monotonically, when a session entry is applied to the internal state machine the state machine time is updated. Because we assume time can differ on different servers, state machine time could potentially decrease after a leader change. To prevent such a scenario, state machine time is always updated with max(oldTime, newTime). When the state machine time is updated by a session-related entry (register, keep-alive, or unregister), all existing sessions are checked for expiration.

<h3 id="preventing-disruptions-due-to-leader-changes">3.8 Preventing Disruptions Due to Leader Changes</h3>

In the event of a network partition or other loss of quorum, Raft can require an arbitrary number of election rounds to elect a new leader. In practice, the number of election rounds is normally low, particularly with the pre-vote protocol. Nevertheless, clients cannot keep their sessions alive during election periods since they can't write to the leader. In order to ensure client sessions don't expire during elections, Copycat expands upon the Raft election protocol to reset all session timeouts when a new leader is elected as part of the process for committing commands from prior terms. When a new leader is elected, the leader's first action is to commit a no-op entry. The no-op entry contains a timestamp to which all session timeouts will be reset when the entry is committed and applied to the internal state machine on each server. This ensures that even if a client cannot communicate with the cluster for more than a session timeout during an election, the client can still maintain its session as long as it commits a keep alive request within a session timeout after the new leader is elected.

{% include common-links.html %}
