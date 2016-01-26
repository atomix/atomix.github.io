---
layout: content
project: copycat
menu: user-manual
title: Raft Implementation Details
pitch: Raft architecture and implementation
first-section: internals
---

Copycat is an advanced, feature complete implementation of the [Raft consensus algorithm] which has been developed over a period of nearly three years. The implementation goes well beyond the [original Raft paper](https://www.usenix.org/system/files/conference/atc14/atc14-paper-ongaro.pdf) and includes a majority of the full implementation described in Diego Ongaro's [Raft dissertation](https://ramcloud.stanford.edu/~ongaro/thesis.pdf) in addition to several extensions to the algorithm.

In some cases, Copycat's Raft implementation diverges from recommendations. For instance, Raft dictates that all reads and writes be executed through the leader node, but Copycat's Raft implementation supports per-request consistency levels that allow clients to sacrifice linearizability and read from followers. Similarly, Raft literature recommends snapshots as the simplest approach to log compaction, but Copycat prefers log cleaning to promote more consistent performance throughout the lifetime of a cluster. In other cases, Copycat's Raft implementation extends those described in the literature. For example, Copycat's Raft implementation extends the concept of sessions to allow server state machines to publish events to clients.

It's important to note that wherever Copycat diverges from standards and recommendations with relation to the Raft consensus algorithm, it does so using well-understood alternative methods that are either described in the Raft literature or frequently discussed within the Raft community. Copycat does not attempt to alter the fundamental correctness of the algorithm but rather seeks to extend it to promote usability in real-world use cases.

The following documentation details Copycat's implementation of the Raft consensus algorithm and in particular the areas in which the implementation diverges from the recommendations in Raft literature and the reasoning behind various decisions.

<h2 id="raft-basics">1 Raft basics</h2>

Raft synchronizes state changes across a cluster by electing a leader and funneling writes through the leader to followers. The algorithm uses a replicated log to coordinate both leader elections and replication.

A Raft cluster primarily consists of three different types of nodes: followers, candidates, and leaders. Each server can transition between these three states given that certain conditions are met. That is, any server can be a follower, candidate, or leader. The roles of the three states are as follows:

* follower - the state in which a server receives replication from leaders and upon failing to receive a heartbeat from the leader for a randomized interval of time, transitions to candidate to start a new election
* candidate - the state in which a server attempts to be elected leader
* leader - the state in which a server receives commands from clients, logs and replicates commands to followers, and determines when commands have been stored on a majority of servers

Leaders receive commands and write them to a local log which is then replicated to followers in batch. Once a command submitted to a leader has been logged and replicated to a majority of the cluster, the leader applies the command to its own state machine and responds to the client.

<h3 id="leader-election-basics">1.1 Leader election</h3>

Raft clusters use a logical concept of time referred as a term, also known as an epoch in some other algorithms. For each term, Raft may or may not elect a leader, and only one leader may exist for any given term. Servers use a variety of timers and consistency checks to elect a leader. Once a leader is elected, all writes to the cluster go through the leader and are replicated to a majority of the cluster.

<h3 id="log-replication-basics">1.2 Log replication</h3>

Logs are replicated from leaders to followers. When a command is submitted to the cluster, the leader appends the command as an entry in its log. The leader periodically sends entries to each available follower in batches. Once a majority of the servers have acknowledged receipt of a given entry it is considered committed and is applied to the leader's state machine.

<h3 id="membership-changes-basics">1.3 Membership changes</h3>

Raft supports the concept of cluster membership changes through special configuration entries in the Raft log. Configuration changes are logged and replicated like any other state change. However, in order to prevent "split brain", Raft only allows a single member to be added to or removed from the cluster at any given time, and no two configuration changes may overlap in commitment.

<h2 id="the-copycat-cluster">2 The Copycat cluster</h2>

The structure Copycat clusters differ significantly from typical Raft clusters primarily due to the need to support greater flexibility in systems in which Copycat is embedded. High-availability systems cannot be constrained by the strict quorum-based requirements of consensus algorithms, and so Copycat provides several node types to address scalability issues.

Copycat clusters consist of three node types: active, passive, and reserve.

* *active* nodes are stateful servers that fully participate in the Raft consensus algorithm
* *passive* nodes are stateful servers that do not participate in the Raft consensus algorithm but receive only committed log entries from followers
* *reserve* nodes are stateless servers that can be transitioned in and out of stateful states

The architecture of clusters allows Copycat to be embedded within highly-available systems without significant impact to availability. Copycat provides an interface to allow any node in the cluster to add, remove, promote, or demote nodes at will. Systems that embed Copycat can use Raft’s leader election algorithm to coordinate modifications to the cluster’s structure. The use of stateful Raft nodes and stateful asynchronous nodes allows systems to quickly replace Raft nodes by promoting and demoting members.

All cluster membership and member state changes are committed as configuration changes through the Raft portion of the cluster. We implement the single member approach to configuration changes to simplify safety requirements during configuration changes (see section 11 for more on configuration changes).

Each stateful server in a cluster maintains two logical state machines. An internal state machine on each server is responsible for managing sessions, connections, and scheduling within the user state machine, and the user state machine contains application logic. Commands submitted by clients are forwarded to the Raft leader where they're logged, replicated, and applied to the user state machine on each server. Queries submitted by clients are handled either by the server to which the client is connected or forwarded to the Raft leader depending on consistency constraints. See section 6 on session for more information about how commands and queries are handled by the cluster.

<h2 id="client-interaction">3 Client interaction</h2>

The basic Raft consensus algorithm dictates that clients should communicate directly with the leader to submit reads and writes to the cluster. The leader services writes by committing commands to the Raft log, and in linearizable systems the leader services reads by synchronously verifying its leadership with a majority of the cluster before applying them to the state machine. But practical systems can benefit from relaxed consistency models, and indeed the Raft literature does describe some ways to achieve this. Clients can submit read-only queries to followers without losing sequential consistency. In fact, there are even ways to make reads on followers linearizable, albeit at significant cost.

Typically, will initially connect to a pseudo-random server to register their session and then reconnect to the leader once it has been discovered. In the event that the client cannot locate a leader it continues to retry against random servers until one is found. In Copycat, client connections are spread across the cluster by default. Clients are allowed to connect to any server, and clients are responsible for choosing a server. Once connected to a server, clients try to maintain their connections for as long as possible. Reducing the frequency with which clients switch servers improves latency in bi-directional communication between clients and servers since servers typically know the route through which a client can be reached.

<h3 id="client-sessions">3.1 Sessions</h3>

Clients interact with the cluster within the context of a session. Sessions provide a mechanism through which interactions between a single client and the cluster can be managed. Once a session is registered by a client, all future interactions between the client and any server are associated with the client’s session. Session aid in sequencing client operations for FIFO order, providing linearizable semantics for operations submitted multiple times, and notifying clients about changes in state machine state.

Clients’ sessions are managed through the Raft log and state machine, affording servers a deterministic view of the active sessions in the cluster. Sessions are registered by committing an entry to the Raft log and kept alive over time with periodic commits. In the event that a client fails to keep its session alive, each server will expire the client’s session deterministically.

<h3 id="session-lifecycle-management">3.2 Session lifecycle management</h3>

Client sessions are managed through entries committed to the Raft log and applied to internal server state machines. When a client first connects to a cluster, the client connects to a random server and attempts to register a new session. If the registration fails, the client attempts to connect to another random server and register a new session again. In the event that the client fails to register a session with any server, the client fails and must be restarted. Alternatively, once the client successfully registers a session through a server, the client continues to submit commands and queries through that server until a failure or shutdown event.

Once the client has successfully registered its session, it begins sending periodic keep alive requests to the cluster. Clients are responsible for sending a keep alive request at an interval less than the cluster’s session timeout to ensure their session remains open. Keep Alice's are written to the Raft log, replicated and committed. This gives state machines a consistent view of the active sessions and allows servers to timeout sessions deterministically.

If the server through which a client is communicating fails (the client detects a disconnection when sending a command, query, or keep alive request), the client will connect to another random server and immediately attempt to send a new keep alive request. The client will continue attempting to commit a keep alive request until it locates another live member of the Raft cluster.

<h3 id="client-commands">3.3 Commands</h3>

Copycat’s Raft implementation separates the concept of writes from reads in order to optimize the handling of each. Commands are state machine operations which alter the state machine state. All commands submitted to a Raft cluster are proxied to the leader, written to disk, and replicated through the Raft log.

When the leader receives a command, it writes the command to the log along with a client provided sequence number, the session ID of the session which submitted the command, and an approximate timestamp. Notably, the timestamp is used to provide a deterministic approximation of time with which state machines can support time-based command handling like TTLs or other timeouts.

<h4 id="preserving-program-order">3.3.1 Preserving program order</h4>

There are certain scenarios where sequential consistency can be broken by clients submitting concurrent commands via disparate followers. If a client submits a command to server A which forwards it to server B (the leader), and then switches servers and submits a command to server C which also forwards it to server B, it is conceivable that the command submitted to server C could reach the leader prior to the command submitted via server A. If those commands are committed to the Raft log in the order in which they’re received by the leader, that will violate sequential consistency since state changes will no longer reflect the client’s program order.

Because of the pattern with which clients communicate with servers, this may be an unlikely occurrence. Clients only switch servers in the event of a server failure. Nevertheless, failures are when it is most critical that systems maintain their guarantees, so servers ensure that commands are applied in the order in which they were sent by the client regardless of the order in which they were received by the leader.

When the leader receives a command, it sequences the command based on the current session state and the sequence number provided in the request. The basic algorithm is as follows:

* If the command sequence number is greater than the next expected sequence number for the session, queue the request to be handled in sequence. 
* Otherwise, write the command to the log and commit it (no need to log again)
* Once the command has been written to the log, handle any queued commands for `sequence + 1`

When a client submits a command to the cluster, it tags the command with a monotonically increasing sequence number. The sequence number is used for two purposes. First, it is used to sequence commands as they’re applied to the user state machine. When a command is committed and applied to the state machine, if the command’s sequence number is greater than one plus the previously applied sequence number, the command is queued and applied in sequence order. Otherwise, the command is handled normally and is committed to the log. The leader uses a recursive algorithm to process commands in order.

<h4 id="linearizable-semantics">3.3.2 Linearizable semantics</h4>

Sequence numbers are also used to provide linearizability for commands submitted to the cluster by clients by storing command output by sequence number and deduplicate commands as they’re applied to the state machine. If a client submits a command to a server that fails, the client doesn’t necessarily know whether or not the command succeeded. Indeed, the command could have been replicated to a majority of the cluster prior to the server failure. In that case, the command would ultimately be committed and applied to the state machine, but the client would never receive the command output. Session-based linearizability ensures that clients can still read output for commands resubmitted to the cluster, but that requires that leaders allow commands with old sequence numbers to be logged and replicated.

<h3 id="client-queries">3.4 Queries</h3>

Queries are state machine operations which read state machine state but do not alter it. This is critical because queries are never logged to the Raft log or replicated[?]. Instead, queries are applied either on a follower or the leader based on the configured per-query consistency level.

When a query is submitted to the Raft cluster, as with all other requests the query request is sent to the server to which the client is connected. The server that receives the query request will handle the query based on the query’s configured consistency level. If the server that receives the query request is not the leader, it will evaluate the request to determine whether it needs to be proxied to the leader:

Queries are optionally allowed to read stale state from followers. In order to do so in a manner that maintains sequential consistency (clients see state progress monotonically) when the client switches between servers, the client needs to have a view of the most recent state for which it has received output. When commands are committed and applied to the user-provided state machine, command output is cached in memory for linearizability and the command output returned to the client along with the index of the command. Thereafter, when the client submits a query to a follower, it will ensure that it does not see state go back in time by indicating to the follower the highest index for which it has seen state.

<h4 id="processing-queries-on-followers">3.4.1 Processing queries on followers</h4>

When queries are submitted to the cluster, the client provides a version number which specifies the highest index for which it has seen a response. Awaiting that index when servicing queries on followers ensures that state does not go back in time if a client switches servers. Once the server’s state machine has caught up to the client’s version number, the server applies the query to its state machine and response with the state machine output.

Clients’ version numbers are based on feedback received from the cluster when submitting commands and queries. Clients receive version numbers for each command and query submitted to the cluster. When a client submits a command to the cluster, the command’s index in the Raft replicated log will be returned to the client along with the output. This is the client’s version number. Similarly, when a client submits a query to the cluster, the server that services the query will respond with the query output and the server’s lastApplied index as the version number.

Log consistency for inconsistent queries is determined by checking whether the server’s log’s lastIndex is greater than or equal to the `commitIndex`. That is, if the last AppendEntries RPC received by the server did not contain a `commitIndex` less than or equal to the log’s lastIndex after applying entries, the server is considered out-of-sync and queries are forwarded to the leader.

<h4 id="ensuring-state-progresses-monotonically">3.4.2 Ensuring state progresses monotonically</h4>

While Copycat allows clients’ queries to be processed on followers and ensures sequential consistency even when switching servers, in some cases this can still result in significant delay. If a client switches to a server that is far behind its previous server, it can block the client’s queries for some indeterminate amount of time. Clients should place an upper-bound on the amount of time within which a query must be handled by a server. If a query request times out, the client should switch to a new server and resubmit the query. All operations submitted to the cluster are idempotent and guaranteed to be sequentially consistent, so there's no risk of loss of consistency using this approach. But servers also have a mechanism to reject queries from clients if their state is too far behind. When a follower receives a query from a client, it checks to determine whether the last known `commitIndex` is present in its log. If the follower’s last log index is less than the `commitIndex`, it forwards the query to the leader.

<h3 id="session-expiration">3.5 Session expiration</h3>

When a new session is registered, the session is assigned a timeout. The session timeout is the time after which the session may be expired by the cluster. Clients are responsible for submitting keep alive requests to the cluster at intervals less than the session timeout. State machines determine when sessions time out based on the state machine time elapsed since the last keep-alive for a given session. Note that this depends on the existence of some mechanism for managing a deterministic representation of time in the state machine. In Copycat, this is done by writing the leader’s timestamp to a variety of log entries.

<h3 id="replicating-server-configurations">3.6 Replicating server configurations</h3>

When a session is registered with Copycat cluster, the client begins submitting periodic keep alive requests to the cluster according to the configured session timeout. However, session timeouts may be configured differently on each server. In order to account for inconsistencies in session configurations in the cluster, we append the leader’s configured session timeout to the log entry registering the session. When a session registration is applied to internal state machines, the state machines set the session timeout based on the timeout in the log rather than their local server configuration. This ensures that all servers have a consistent view of timeouts for each individual session and can therefore expire sessions deterministically. Once a RegisterEntry is committed and a new session is registered, the leader sends the logged timeout back to the client.

Alternatively, servers could replicate their session timeouts in special configuration change entries. This could allow servers’ session timeouts to be reconfigured without impacting existing sessions. Servers would still have to provide a session timeout in keep-alive responses. When a leader logged and committed a keep-alive entry, it would respond with the next keep-alive interval based on the last committed session timeout.

<h3 id="ensuring-time-progresses-monotonically">3.7 Ensuring time progresses monotonically</h3>

Sessions are expired in the internal state machine on each server based on log times. In Copycat, all session-related entries are written to the log with the leader’s timestamp. The timestamp is used as an approximation of wall-clock time in the state machine. We assume that a leader change can result in log time decreasing; a new leader may log an entry with a timestamp prior to the last timestamp logged by the previous leader. Thus, in order to ensure that state machine time progresses monotonically, when a session entry is applied to the internal state machine the state machine time is updated. Because we assume time can differ on different servers, state machine time could potentially decrease after a leader change. To prevent such a scenario, state machine time is always updated with max(oldTime, newTime). When the state machine time is updated by a session-related entry (register, keep-alive, or unregister), all existing sessions are checked for expiration.

<h3 id="preventing-disruptions-due-to-leader-changes">3.8 Preventing disruptions due to leader changes</h3>

In the event of a network partition or other loss of quorum, Raft can require an arbitrary number of election rounds to elect a new leader. In practice, the number of election rounds is normally low, particularly with the pre-vote protocol. Nevertheless, clients cannot keep their sessions alive during election periods since they can’t write to the leader. In order to ensure client sessions don’t expire during elections, Copycat expands upon the Raft election protocol to reset all session timeouts when a new leader is elected as part of the process for committing commands from prior terms. When a new leader is elected, the leader’s first action is to commit a no-op entry. The no-op entry contains a timestamp to which all session timeouts will be reset when the entry is committed and applied to the internal state machine on each server. This ensures that even if a client cannot communicate with the cluster for more than a session timeout during an election, the client can still maintain its session as long as it commits a keep alive request within a session timeout after the new leader is elected.

<h2 id="state-machines">4 State machines</h2>

Each server is configured with a state machine to which it applies committed commands and queries. State machines operations are executed in a separate state machine thread to ensure that blocking state machine operations do not block the internal server event loop.

Servers maintain both an internal state machine and a user state machine. The internal state machine is responsible for maintaining internal system state such as sessions and membership and applying commands and queries to the user-provided `StateMachine`.

<h3 id="deterministic-scheduling">4.1 Deterministic scheduling</h3>

Because of the complexities of coordinating distributed systems, time does not advance at the same rate on all servers in the cluster. What is essential, though, is that time-based callbacks be executed at the same point in the Raft log on all nodes. In order to accomplish this, the leader writes an approximate Instant to the replicated log for each command. When a command is applied to the state machine, the command’s timestamp is used to invoke any outstanding scheduled callbacks. This means the granularity of scheduled callbacks is limited by the minimum time between commands submitted to the cluster, including session register and keep-alive requests. Thus, users should not rely on StateMachineExecutor scheduling for accuracy.

<h2 id="session-events">5 Session events</h2>

Typical implementations of the Raft consensus algorithm expose an API to allow users to alter state in the state machine. But more complex coordination may often require that clients learn about changes in the state machine as well. A naive implementation of this is polling. Polling requires that clients periodically request any state changes from the cluster, but it also implies greater latency and load on the cluster. In order for a client to learn about a state change event, the client must first make a request to the cluster, and all clients must poll the cluster regardless of whether there are any notifications waiting.

Alternatively, systems can push state change notifications to clients. These systems are called “wait-free” systems.

In many cases, clients can essentially behave as extensions of the replicated state machine by receiving notifications from the cluster. For instance, continuing with the lock example, a lock state machine may push lock and unlock events to clients. This implies that order and fault-tolerance are important. If a client receives a lock and then unlock event, it will believe the state of the lock to be unlocked. Conversely, if a client receives an unlock and then lock event, the final state will be locked. The same is true of reliability. If a client receives only a lock or unlock event without its opposite, it can result in an inconsistent state across clients.

For these reasons, session event notifications cannot be implemented as simple messages to the client. Networks are unreliable, and we must assume that messages may be arbitrarily lost or reordered. Fortunately, Raft provides the primitives on which events can be pushed to clients in a fault-tolerant manner. In order to do so, we simply extended Raft’s sessions to encapsulate the framework for guaranteeing order in session events.

<h3 id="publishing-events-from-the-state-machine">5.1 Publishing events from the state machine</h3>

State machines push event notifications to clients as part of their normal operation. Referred to as session events, messages are published to clients during the application of normal operations to the state machine. For instance, while a lock is held by one session, a lock state machine might queue additional sessions waiting for the lock to be released. Once the lock is released, the state machine could push a release notification to the next session in the queue. By publishing session events in response to commands being applied to the state machine, we can infer order among the events across the different servers in the cluster.

Session events are typically pushed to the client by the server to which the client is connected. If the client is connected to a follower, that follower will push session events to the client. If the client is connected to the leader, the leader will push session events to the client. However, for fault tolerance and consistency, it’s still critical that all servers store session events in memory. State machines should behave deterministically regardless of whether a client is connected to the server managing any given state machine.

{% include lightbox.html href="/assets/img/docs/session_event_consistency.png" desc="Session event fault-tolerance" %}

*This figure illustrates why it’s important that events be stored in memory on each server even though they may be sent to the client by only one server. In (a) S1 sends three events to the client. The client acknowledges two of the three events before S1 crashes in (b). The client submits a KeepAlive RPC which acknowledges events up to index 3 on S2 and S3 as is depicted in (c). Finally, in (d) the client reconnects to S2 which sends events for indexes 4 and 5 to the client.*

All events are sent to and received by the client in sequential order. This makes it easier to reason about events and aids in tracking which events have been received by the client. In order to track events, each event is sent to the client with the index of the state machine command that triggered the event. The client expects to receive events in monotonically increasing order. However, because not all commands applied to the state machine may result in events published to any given session, the protocol must account for skipped indexes as well.

Sending only the index of each event published to the client provides the client with the context necessary to determine that it received some events in order, but not that it received all events.  If a server publishes event indexes 1 and 3 to a client, the client can ensure that those events were received in order, but without additional metadata it doesn’t know whether it should have received an event for index 2. Thus, in order to handle missing indexes in the order of events for any given session, servers must include the index of the previous event sent to the client, aptly called `prevIndex`. The `prevIndex` provides clients the necessary context to determine whether all events have been received in order. If a client receives an event message with a `prevIndex` greater than the last index for which it received an event, it can reject the event and request missing messages. 


[![Session event sequencing](/assets/img/docs/session_event_sequencing.png){: height="500px" }]
*This figure illustrates how session event messages are sequenced when sent from a server to a client. For each command applied to the state machine, zero or more session event messages can be pushed to the client. The client sequences the events in the order in which they were published by the stat machine.*

Similarly, some commands may result in multiple event messages being published to the same session, and order may still be important within multiple events for a single index. For instance, in a lock state machine, it may be possible for a session to passively listen for lock state change events. The release of the lock may result in two events related to a single command — release the lock from one session and then acquire the lock for another session — and order remains important for this binary state machine. Servers must ensure that clients can determine the order in which to handle events within a single index.

The simplest and most efficient approach to ensuring order among event messages within a single index is to send messages in batches to the client. Using this approach, messages for one or more indices could be sent in a single batch and in the order in which they were produced on the server. The server would await the completion of the command before sending the batch.

However, in cases where the number of event messages for a single index may exceed a reasonable batch size, messages must be explicitly ordered within indexes. To order many messages within a single index, Publish RPCs to the client must include a starting offset and `prevOffset` which denote the offset of the first message within the index in the RPC and the offset of the end of the previous message. The latter is necessary because there is no fixed number of event messages per batch. Thus, when a batch crosses indexes, the `prevOffset` effectively indicates the number of messages in the batch for the previous index.

<h3 id="sequencing-events-on-the-client">5.2 Sequencing events on the client</h3>

While event messages are in transit between the server and client, we assume messages can be arbitrarily lost or reordered. Individual requests can take several paths to the client depending on the cluster and client configurations, and different messages from the same server can travel different routes to the client. But as with other areas of the system, our goal was to implement sequential consistency for session events. Strict ordering simplifies reasoning about a system and allows the client to essentially act as an extension of the replicated state machine.

A prime example of the need for strict ordering in session events is distributed locks. Locks represent a binary state machine; a lock is either in the locked or unlocked state. If a state machine publishes two events — lock and unlock — to a client, the order is critical. If the client receives lock and then unlock it will believe the final state of the lock to be unlocked; conversely, if the client receives unlock and then lock it will believe the opposite. For this reason, it’s crucial that clients receive event messages in the order in which they were sent by the state machine.

In order to guarantee ordering of session events published to a client, the client tracks the index of the last event batch received in sequence and uses it to validate that future events are received in sequence. The algorithm for receiving an event batch on the client is as follows:

* Compare the batch’s previousIndex with the local eventIndex
* If eventIndex is less than previousIndex respond with eventIndex indicating the last event batch received in sequence
* If eventIndex is equal to or greater than previousIndex ignore the event batch and respond successfully
* If eventIndex is equal to previousIndex update the local event index with the current batch index and process the event batch
* Update the local eventIndex with the batch index

The client initializes its eventIndex to 0. When the client receives a batch of events, it validates the request’s previousIndex against its local eventIndex to verify that the batch is the next in the sequence. If the batch was received out of order, it responds immediately indicating the index of the last event batch received in sequence. This allows the sending server to resend batches from that point.

{% include lightbox.html href="/assets/img/docs/session_event_coordination.png" desc="Client session event coordination" %}

*This figure depicts the process with which a client coordinates with a server pushing event messages to the client. In (a) the server sends event messages for index `5` to the client with a ``prevIndex`` of `2`. However, because the client last received events for index `2`, the client rejects the events in (b) and sends its ``prevIndex`` `2` back to the server. The server then sends entries for index `3` with a ``prevIndex`` of `2` (c) and the client acknowledges receipt of the events in sequence in (d).*

Requirements for responding to session event messages is dependent upon the event consistency model. Clients can safely respond to session event messages before processing them, but in some cases linearizability for session events is desired. For instance, when a lock is released, it may be important that the next lock holder is notified before the lock release is complete. If linearizability is a requirement, clients must fully process all messages in a batch prior to responding to the Publish RPC. Responding to a Publish RPC prior to processing the messages therein can result in the triggering command being completed before event message handlers are completed.

<h3 id="managing-server-memory">5.3 Managing server memory</h3>

As commands are committed to the Raft log and applied to server state machines, servers may push an arbitrary number of event messages to any session in response to any given command. In order to maintain fault-tolerance, each server must hold session events in memory even if the client to which an event was published is not connected to that server. This ensures that in the event of the failure of the server to which a client is connected, the client can reconnect to another server and continue to receive events for its session.

However, as session events are received by the clients, servers need a way to remove unneeded events from memory. The session expiration process described in section 6.2 ensures that events are only retained in memory as long as a session is alive. When a session is unregistered or expires, so too should event messages published to that session be removed from memory. But for long-running sessions which receive a large number of events, servers should be able to remove events that have already been received by the client.

Clients only ever have direct communication with a single server. The client exchanges sufficient information with that server to remove acknowledged events from that server’s memory. When a client responds successfully to a Publish RPC, the publishing server can safely remove events for that session up to the ackIndex provided by the client. But this doesn't account for the other servers in the cluster.

In order to ensure all servers clear acknowledged events from memory, each client must include in its periodic KeepAlive RPCs the highest index for which it has received events in sequential order. When the leader logs and commits a KeepAlive entry, state machines on each server can remove events up to the provided eventIndex.

<h3 id="linearizable-session-events">5.4 Linearizable session events</h3>

Clients are designed to favor connections to specific servers. Many implementations of the Raft consensus algorithm tend to favor communicating directly with the leader, but Copycat’s clients are designed to spread the load across the cluster. This means clients requests are often proxied through a follower to the leader. However, this poses a particularly daunting challenge for pushing event messages from servers to the client.

Many use cases require linearizability for session events. Linearizability dictates that an operation takes place exactly once between its invocation and response. In the case of session events, this means when a client submits a command, any associated session events triggered by the command must be received and processed by their respective clients prior to the completion of the original command.

As described thus far, the algorithm for publishing events to clients handles linearizability poorly. Because clients may be connected to any server in the cluster, and because events are pushed to the client only from the server to which the client is connected, an event will not be published to a client until the server to which it’s connected applies the triggering command. In order to guarantee linearizability for session events using this approach, the leader would have to block to await a command to be applied to all required servers (servers to which associated clients are connected) and for published events to be received and acknowledged by clients. Because clients can only acknowledge events through KeepAlive RPCs, this would require nearly a session timeout to complete. Furthermore, network partitions could result in a session event taking significantly longer than a session timeout to be received by the client. Clearly this is impractical.

In order to provide linearizable semantics for session event messages while retaining the existing client communication patterns wherein clients communicate directly with followers, leaders need a way to proxy event messages through the server to which a client is connected. This requires the introduction of a new mechanism for tracking client connections through the Raft log. Each client is assigned a globally unique UUID. The UUID is used to associate clients and their sessions with specific servers. Whenever a client connects to a new server, its first responsibility is to submit a Connect RPC to the server. The Connect RPC is then forwarded to the current leader as an internal Accept RPC and the leader commits the connection change to the Raft log as a connect entry. Connect entries are applied on each server as they’re written to the log. This helps reduce the frequency of stale connection information when clients switch servers. Each connect entry indicates the session and server relationship.

Given the association of sessions to servers, we can implement linearizable session events by proxying event messages through the server to which the client is connected. When an event is published by the leader’s state machine, the leader attempts to proxy the event batch through the appropriate follower based on the last known connection for the session. If the client is no longer connected to that follower, it will eventually establish a new connection, and the leader can resend the lost event messages.

<h3 id="recovering-messages-after-a-server-failure">5.5 Recovering messages after a server failure</h3>

Many implementations of the Raft consensus algorithm allow certain operations to be executed on a single node in the cluster. Read-only operations can safely be evaluated on a follower without losing sequential consistency by tracking the index of the last entry seen by the client. But because session events rely on replication of commands through the Raft log for fault tolerance, state machines must publish events only in response to operations that have been written and committed to the Raft log. This ensures that events are published by a majority of the cluster and will not be lost in the event of a failure because, once committed, commands themselves are guaranteed to be stored on a majority of servers.

In the event that a majority of the cluster fails, session events can be lost from memory. However, once a majority of the cluster recovers, the replay of commands to the state machine will result in session events being regenerated in memory and resent to the appropriate clients. For this reason, we allow clients to maintain their sessions while a majority of the cluster is down so that they can still receive delayed event messages once a quorum is re-established. Though the loss of quorum means clients cannot acknowledge receipt of new events through keep alive requests, this is still safe since new events cannot be created either and thus resource usage will not increase during long outages.

<h3 id="managing-log-compaction">5.6 Managing log compaction</h3>

Session event messages are retained in server state machines until the client acknowledges receipt or the client’s session times out. In the event of a server crash, servers must be able to recover session events to retain fault tolerance. For this reasons, state machines must ensure that commands which create session event messages are retained in the log until those events are received by their respective clients. If servers remove commands from their logs before related event messages have been acknowledged by clients, this can result in a liveness (good things will eventually happen) violation. Session events are ordered on the client based on the index of the previous event sent to the client. But servers lose contextual information when compacting their logs.

Once an event has been acknowledged by a client either directly to the server that pushed the event message or via the application of a KeepAlive entry, the triggering command can be safely removed from the log. Given that multiple sessions may be open at any given time, this means the log can be safely compacted only up to the lowest index for which events have been received by all clients. We call this the completeIndex. When a KeepAlive entry is applied to a state machine, the completeIndex is calculated. Given the lowest index for which events have been received by all sessions, we can then safely compact logs up to that index.

But using the eventIndex provided by each client in KeepAlive RPCs will not suffice to properly track the completeIndex. Sessions are designed to allow indexes to be arbitrarily skipped as it pertains to session events. Indeed, some sessions could conceivably publish only a single event in their lifetime. In that case, if a single event is ever published to a session, the session’s eventAckIndex will remain at the index of that single event until another event is published or the session is unregistered or expired. Thus, in order to ensure completeIndex continues to advance in the absence of session events, the lowest eventAckIndex for each session should be calculated as n - 1 where n is the lowest index for which an event has not been acknowledged. If no events are awaiting acknowledgement, the eventAckIndex for the session is equal to lastApplied.

The complete algorithm for tracking completeIndex is as follows:

* When a KeepAlive entry is applied, remove events from the appropriate session up to and including eventAckIndex
* If events are still waiting for acknowledgement, recalculate the eventAckIndex for the session as n - 1 where n is the index of the first event waiting to be acknowledged
* If no events remain in memory, set eventAckIndex to lastApplied
* Recalculate completeIndex as the minimum of eventAckIndex for all sessions

For sessions where no events are waiting to be acknowledged, eventAckIndex must increase with lastApplied in order to ensure completeIndex is properly recalculated. Additionally, completeIndex may be recomputed each time lastApplied is incremented, or it may be recomputed at regular intervals according to the log compaction schedule.

Given the lowest index for which events have been received by all clients, it is safe to remove related commands from the log. Log compaction processes must use the completeIndex to dictate which sections of their logs can be safely removed. For log cleaning (described in Section 13) this means only entries up to the completeIndex may be removed from the log. This ensures that in the event of a crash and recovery, the state machine can safely recreate all events that have yet to be acknowledged by their respective clients.

For systems that do snapshot-based log compaction, servers could persist pending event messages with the snapshot. However, because events are based on commands that are already present in the log, we feel it would be redundant to store the event messages themselves and is ideal to instead exclude events from log compaction altogether. The session expiration feature ensures liveness — that each session will either receive its events or expire — so awaiting the receipt of events during log compaction should be not significantly slow the process down. Excluding events from snapshots both reduces the size of snapshots and ensures that events related to later-expired sessions are not retained in the log. To persist a snapshot after related events have been received by their clients, servers should store a snapshot of their log at a specific index and then wait for the snapshotIndex and completeIndex to converge before removing entries from the log. In other words, the snapshot should only become effectively committed and entries should only be removed from the log once all event messages up to the snapshot index have been received by clients.

The drawback to this approach to log cleaning is that commands for which no events were published or for which events were already acknowledged by clients often cannot be removed from the log because earlier events may still be pending. However, we feel the liveness properties of sessions make this an acceptable tradeoff. Still, we have conceived an optimized approach for log cleaning that does not require waiting for events for unrelated commands to be received by clients. By checking each entry against in-memory session events, commands for which no events were published or for which published events were acknowledged by receiving clients can be safely removed from the log. We suspect this algorithm would work well with log cleaning since entries are evaluated and removed on an individual basis, but unfortunately it cannot be applied to snapshot-based approaches since a snapshot implies a fixed point in time and operates only on chunks of entries in the log.

<h2 id="membership-changes">6 Membership changes</h2>

The Raft consensus algorithm is designed explicitly with the goal of supporting cluster membership changes without downtime. However, because of the restrictions on commitment of state changes to a Raft cluster, configuration changes are nevertheless an expensive operation. When new servers join the cluster, their logs must be caught up to the leader before they can begin actively participating in the commitment of entries to the Raft log. This implicit overhead in replacing voting Raft members makes systems that dynamically replace failed Raft servers impractical. Nevertheless, we sought an approach that could quickly replace failed voting members. This section proposes an algorithm wherein Raft voting members can be quickly replaced by maintaining standby servers.

Membership changes in Raft are typically implemented via one of the two means described in the Raft literature. The original Raft paper proposed a two-step process wherein a combination of the old and new configuration was committed to the Raft log as an intermediate step. This so called joint consensus approach allowed for arbitrary configuration changes while preventing two majorities from forming during the configuration change. However, this approach was later replaced by a simpler single-server configuration change process. The single server configuration change approach allows only individual servers to be added to or removed from the cluster at any given time. This significantly simplifies the configuration change process as it does not require multiple stages.

But even with the advancements in configuration change processes in the Raft consensus algorithm, some challenges still remain in implementing configuration changes in practical systems. If not done carefully, the rapid addition of servers to a configuration can result in effective downtime for the cluster. For example, if three servers are added to a two node cluster, the cluster will essentially be blocked until at least one of the new servers catches up with the leader. Thus, practical systems must still implement multi-stage configuration change processes wherein new servers join in a non-voting state and are later promoted to full voting members once they’ve caught up to the leader.

The time it takes for a new server to join the cluster and catch up to the leader makes dynamically replacing failed servers impractical. Thus, we propose reducing the latency of catching up new servers by maintaining a hierarchical network of servers wherein standby servers are always available to become active voting members. The network contains three different types of servers — active, passive, and reserve members — each of which play some role in supporting rapid replacement of failed servers.

<h3 id="active-members">6.1 Active members</h3>

Active members are full voting members which participate in all aspects of the Raft consensus algorithm. Active servers are always in one of the Raft states — follower, candidate, or leader — at any given time.

<h3 id="passive-members">6.2 Passive members</h3>

When a new server is added to a Raft cluster, the server typically must be caught up to within some bound of the leader before it can become a full voting member of the cluster. Adding a new server without first warming up its log will result in some period of decreased availability. Still, even in implementations that avoid availability problems by catching up servers before they join, the process of catching up a new server is not insignificant. The leader must send its entire log to the joining server, and for systems that take snapshots, the snapshot must be installed on the new server as well. Thus, there is significant overhead in terms of time and load to dynamically replacing a failed server.

However, systems can maintain servers that are virtually kept in sync with the rest of the cluster at all times. We call these servers passive servers. The concept of passive servers essentially builds on the approach for catching up new servers as has previously been described in Raft literature [Consensus: Bridging Theory and Practice - Section 4.2.1]. Passive servers are essentially kept in sync with the voting members of the cluster in order to facilitate fast replacement of voting members. When a voting member is partitioned, a passive member can be immediately promoted to active and the unavailable voting member will be removed.

Passive servers can also be useful in other contexts. For instance, our implementation optionally allows reads to be executed on passive servers with relaxed consistency requirements. Systems can still maintain sequential consistency on passive servers with the same mechanisms as those used for querying followers (described in Section 8.1).

<h3 id="reserve-members">6.3 Reserve members</h3>

Thus far, we’ve described active voting members and the process of replacing them with passive members. This provides a mechanism for rapidly recovering the full cluster of voting members so long as a majority of the voting members is not lost at the same time. For large clusters, though, the overhead of maintaining passive servers can by itself become a drain on the cluster’s resources. Each additional passive server imposes the overhead of replicating all committed log entries, and this is significant even if done by followers. Thus, to ease the load on large clusters, we introduce the reserve member type.

Reserve members serve as standbys to passive members. When an active server fails and a passive server is promoted, the leader can simultaneously promote a reserve server to passive. This ensures that as the cluster evolves and the pool of passive servers shrinks, new servers can take their place.

Reserve servers do not maintain state machines and need not known about committed entries. However, because reserve servers can be promoted to passive, they do need to have some mechanism for learning about configuration changes.

<h3 id="passive-replication">6.4 Passive replication</h3>

The process of replicating to passive servers parallels that of the process of catching up new servers during configuration changes. However, the implication of catching up new servers is that practically speaking it doesn’t place any additional load on the cluster. Once the server is caught up, it will become a full voting member and so will continue to receive AppendEntries RPCs from the leader at normal intervals anyways. Thus, it makes sense for the leader to  include new servers in AppendEntries RPCs. Conversely, passive servers persist for significantly longer than the time it takes to catch up a new server and the replication of entries to passive servers represents additional load on the cluster. Additionally, little is gained from the leader replicating entries to passive servers directly. Thus, we propose moving responsibility for replicating entries to passive servers from the leader to followers.

Each follower is responsible for sending AppendEntries RPCs to a subset of passive servers at regular intervals. The algorithm for sending AppendEntries RPCs from followers to passive members is identical to that of the standard process for sending AppendEntries RPCs aside from a few relevant factors:

* Each follower sends AppendEntries RPCs only to a subset of passive servers
* Followers send only committed entries to passive servers

In order to spread the load across the cluster and prevent conflicts in passive replication, each follower is responsible for replicating entries to a subset of the available passive members. This seems to imply that followers must have some sense of the availability of both active and passive servers in the cluster so that they can determine the relationship between followers and passive members. However, because the algorithm is designed to promote passive servers when an active server is unavailable, followers need not have any mechanism for determining the state of active members.

<h3 id="promoting-passive-members">6.5 Promoting passive members</h3>

Any server can promote any other server. Passive servers are promoted by simply committing a single-server configuration change adding the passive server to the quorum. As with all configuration changes, the updated configuration is applied on each server as soon as it’s written to the log to prevent so-called “split brain.”

Because passive servers receive configuration changes as part of normal replication of entries via AppendEntries RPCs, passive servers that are promoted in a given configuration must be able to continue receiving entries. However, the failure of a follower can result in the halting of AppendEntries RPCs to a passive server. If that passive server is then promoted, it will never receive the configuration change and thus will never actually transition to the active member state. For this reason, leaders must take over responsibilities for sending AppendEntries RPCs to any server promoted from passive to active immediately after the configuration change is written to the leader’s log. Indeed, this is the expected behavior as configuration changes are immediately applied when written to the log. However, note that if the follower responsible for sending AppendEntries RPCs to the promoted server for cold is alive, for some period of time both the leader and the follower will send AppendEntries RPCs to the server being promoted. This, however, should not pose safety issues as the AppendEntries protocol ensures entries will not be duplicated in the promoted server’s logs.

<h3 id="demoting-active-members">6.6 Demoting active members</h3>

The ultimate goal of the dynamic configuration change process is to replace an unavailable voting member with an available voting member. However, in order to ensure a further loss of availability is not incurred, it’s critical that the failed active server not be demoted until it has been fully replaced by the promotion of a passive server. This ensures that the quorum size is not decreased in the event of a failure to commit the initial configuration change promoting the passive server. Once the promotion of the passive server has been committed, the unavailable active server can be demoted from the quorum.

<h3 id="determining-availability">6.7 Determining availability</h3>

The dynamic membership change algorithm as described thus far replaces unreachable active members with arbitrary passive members and passive members with reserve members. However, this algorithm does not account for cases where passive or reserve servers are themselves reachable. Thus, some extension needs to be made to provide a consistent view of the availability of each server in the cluster.

The basic Raft consensus algorithm provides leaders a clear view of all followers. Leaders are responsible for sending periodic AppendEntries RPCs to followers at regular intervals, and the responses, or lack thereof, to AppendEntries RPCs can be used to deduce the availability of followers. Leaders can use the availability of followers to determine when to promote a passive server to active and remove an unavailable follower. However, the passive member may itself be unavailable. Without accounting for availability, this can result in an infinite loop of promotion and demotion wherein two unavailable servers continuously replace one another as active servers. 

In order to facilitate promoting available members and demoting unavailable members, we introduce modifications to the *AppendEntries* requests that leaders send to followers to additionally track availability. The leader periodically sends empty heartbeats to all servers - including passive and reserve servers - to determine their availability. If a server fails to respond to an empty `AppendRequest` for several rounds of heartbeats, the leader commits a configuration change setting the member's status to `UNAVAILABLE`. The leader continues to send empty `AppendRequest`s to unavailable members to attempt to determine when they become reachable again. Once an unavailable member responds successfully to an empty `AppendRequest`, the leader commits another configuration change to update that member's status to `AVAILABLE` again.

As is the case with session expiration described in Section 6.2, no-op entries committed at the beginning of a new leader’s term effectively reset the timeout for all members. This ensures that members do not appear unavailable due to leadership changes. Additionally, each time a Heartbeat entry is applied to the state machine, heartbeats for all other servers are checked to determine availability.

<h2 id="the-copycat-log">7 The Copycat log</h2>

At the core of the Raft consensus algorithm is the log. As commands are submitted to the cluster, entries representing state changes are written to an ordered log on disk. Logs provide the mechanism through which persistence and consistency is achieved in Raft.

But logs pose particular challenges in managing disk consumption. As commands are written to the logs on each server, entries in the log consume an ever increasing amount of disk space. Eventually, logs on each server will run out of disk space.

Typical implementations of the Raft consensus algorithm use a snapshot-based approach to compacting server logs. But because of the unique needs of Copycat’s session events, we opted to simplify the implementation of log compaction by implementing log cleaning.

<h3 id="log-structure">7.1 Structure of the log</h3>

Copycat logs are broken into segments. Each segment of a log is backed by a single file on disk (or block of memory) and represents a sequence of entries in the log. Once a segment becomes full - either determined by its size or the number of entries - the log rolls over to a new segment. At the head of each segment is a 64-byte header that describes the segment's starting index, timestamp, version, and other information relevant to log compaction and recovery.

![Log structure](/assets/img/docs/log_structure.png)

*This illustration depicts the structure of the log. The log is broken into segments with each segment holding a count- or size-based range of entries. Segmenting the log allows sections of the log to be compacted independently.*

Each entry in the log is written with a 16-bit unsigned length, a 64-bit index, and an optional 64-bit term. Because Raft guarantees that terms in the log are monotonically increasing, the term is written only to the first entry in a segment for a given term, and all later entries inherit the term. When an entry with a new term is appended, that entry is written with the new log term and subsequent entries inherit the term.

<h3 id="log-indexes">7.2 Log indexes</h3>

Log segments are indexed in an in-memory map of 64-bit offsets to 32-bit unsigned positions in the segment. When a segment is loaded from disk, Copycat iterates through all entries in the segment to recreate the index.

Because Copycat allows segments to be missing arbitrary entries, entry positions are referenced in the index using a binary search algorithm. However, in order to optimize index lookups for the majority of cases, indexes keep track of whether any offsets have been skipped in the current segment. If no offsets have been skipped then index lookups are performed in O(1) time simply by reading the position for the given offset in the index. Because Raft servers typically read from and write to only the last segment in the log, this tends to be very efficient for servers operating normally. Binary search only becomes necessary when replaying entries in segments that have already been compacted. For those cases, the index is further optimized to always check the next entry in the log for a match before performing a binary search. This means iterating a segment is also done in O(1) time after the first lookup.

<h2 id="log-compaction">8 Log compaction</h2>

The Raft literature suggests several ways to address the problem of logs growing unbounded. The most common of the log compaction methodologies is snapshots. Snapshotting compacts the Raft log by storing a snapshot of the state machine state and removing all commands applied to create that state. As simple as this sounds, though, there are some complexities. Servers have to ensure that snapshots are reflective of a specific point in the log even while continuing to service commands from clients. This may require that the process be forked for snapshotting or leaders step down prior to taking a snapshot. Additionally, if a follower falls too far behind the leader (the follower’s log’s last index is less than the leader’s snapshot index), additional mechanisms are required to replicate snapshots from the leader to the follower.

Alternative methods suggested in the Raft literature are mostly variations of log cleaning. Log cleaning is the process of removing individual entries from the log once they no longer contribute to the state machine state. The disadvantage of log cleaning is that it adds additional complexity in requiring state machines to keep track of commands that no longer apply to the state machine’s state. This complexity is multiplied by the delicacy handling tombstones; commands that result in the absence of state must be carefully managed to ensure they’re applied on all Raft servers. Nevertheless, log cleaning provides significant performance advantages by writing logs efficiently in long sequential strides.

We opted to sacrifice some complexity to state machines in favor of more efficient log compaction. The reasoning behind this decision is log cleaning provides a lower level mechanism for log compaction than does snapshots, and higher level approaches can co-opt the log cleaning process for different use cases. 

As entries are written to the log and associated commands are applied to the state machine, state machines are responsible for explicitly cleaning the commits from the log. The log compaction algorithm is optimized to select segments of the log for compaction based on the number of commits marked for removal. Periodically, a series of background threads will rewrite segments of the log in a thread-safe manner that ensures all segments can continue to be read and written. Whenever possible, neighboring segments are combined into a single segment to reduce the number of open file descriptors.

Typically, a Raft log contains non-null entries from the point of the last compaction through the commit index and to the end of the log. But this compaction model means that Copycat’s Raft protocol must be capable of accounting for entries missing from the log. When entries are replicated to a follower, each entry is replicated with its index so that the follower can write entries to its own log in the proper sequence. Entries that are not present in a server’s log or in an AppendEntries RPC are simply skipped in the log. In order to maintain consistency, it is critical that state machines implement log cleaning correctly. We can safely assume that if an entry is missing from the log due to compaction, it must have already been committed and so the consistency checks inherent in handling AppendEntries RPCs are largely irrelevant and can be bypassed.

While log cleaning is a form of log compaction, the following sections refer to cleaning and compaction in separate contexts. Cleaning refers to the process of the state machine marking a particular log entry for removal from the log. Compaction refers to the process of physically removing an entry from disk.

<h3 id="log-cleaning">8.1 Cleaning entries from the log</h3>

With log cleaning, state machines are ultimately responsible for specifying which entries may safely be removed from the log. As entries are committed and commands are applied to the state machine, the state machine must indicate when prior commands no longer contribute to its state. For instance, if the commands `x←1` and then `x←2` are applied to the state machine in that order, the first command `x←1` no longer contributes to the state machine’s state. That is, we can arrive at the final state `x=2` without applying the command `x←1`. Therefore, it’s safe to remove `x←1` from the log.

{% include lightbox.html href="/assets/img/docs/major_compaction.png" desc="Major Compaction" %}

*This figure illustrates the process of cleaning entries from the log. As entries are committed and commands are applied, the state machine marks entries that no longer contribute to the system's state for removal from the log. Grey boxes represent entries that have been marked for removal (i.e. cleaned) but haven't yet been removed by log compaction processes.*

When a state machine indicates a command no longer contributes to its state and is safe to remove from the log, the index of the associated entry is set in a memory-compact bit array used during log compaction to determine the liveness of each individual entry. Therefore, the overhead to log cleaning in terms of memory is equivalent to the number of entries stored on disk.

<h3 id="log-compaction-basics">8.2 Basics of log compaction</h3>

Up until now we have described the methods by which commands are applied to the state machine and the state machine indicates which commands no longer contribute to the state machine state. But this does not suffice to solve the problem of an ever growing amount of disk space being consumed by cleaned entries.

In order to ensure the log does not grow unbounded, a series of background tasks periodically select and rewrite segments of the log. The basic algorithm is as follows:

1. Select a set of segments to compact based on some set of configurable criteria
2. For each segment, iterate through entries in the segment file and rewrite live entries to a new segment on disk
3. Discard the old segment file

The criteria by which segments are selected for compaction can have significant impact on the overall performance of the log compaction algorithm. Ideally, segments which would result in the greatest disk space savings should be selected for compaction, but several criteria can be used to select segments according to the needs of the system. In our implementation, we use a combination of the number of times a segment has been compacted and the percentage of entries that will be removed from the segment by compaction. This is known as a generational compaction strategy and borrows from the algorithms defined by Log-Structured Merge (LSM) trees.

The removal of entries from the log necessitates some minor modifications to the Raft consensus protocol. In particular, AppendEntries RPCs must be capable of sending missing entries to followers. If a server does a consistency check and an entry is missing from its log, it can safely assume that the log is consistent with an AppendEntries request since only committed entries can be cleaned and compacted from the log, and the Log Matching Property guarantees that no other server could have applied an entry from a different term or with a different value.

<h3 id="log-segment-compaction">8.3 Combining log segments</h3>

As the cluster progresses and entries are written to and removed from the log, each segment will shrink and the overall number of segments will increase. Eventually, the number of open resources can cause performance and fault tolerance issue. Therefore, in addition to reducing the size of individual segments, some mechanism is required to reduce the number of overall segments as well.

During log compaction, multiple neighboring segments can be rewritten into a single segment to reduce the number of files on disk. When segments are selected for compaction, segments that are parallel to one another — such that the tail of one segment flows into the head of another segment — are given priority over disjointed segments. In our implementation, we select and combine neighboring segments iff the resulting compact segment will be smaller than the configured maximum segment size.

<h3 id="log-tombstones">8.4 Removing tombstones from the log</h3>

The log compaction algorithm as described thus far is safe for removing commands that update state machine state. But this does not account for entries that remove state (called tombstones) from the state machine. Tombstones are entries in the log which amount to state changes that remove state. In other words, tombstones are an indicator that some set of prior entries no longer contribute to the state of the system, including the tombstone entry itself. Thus, it is critical that tombstones remain in the log as long as any prior related entries do. If a tombstone is removed from the log before its prior related entries, rebuilding a state machine from the log will result in inconsistencies.

{% include lightbox.html href="/assets/img/docs/major_compaction.png" desc="Major Compaction" %}

*This figure illustrates the process of major compaction. The grey boxes represent entries that have been marked for removal (cleaned) from the log. To compact the log, the major compaction task iterates through committed segments and rewrites each segment with cleaned entries removed (c) resulting in a compacted segment(d). The same process is then performed on the next segment (c)(d) until all committed segments have been compacted.

A significant objective of the major compaction task is to remove tombstones from the log in a manner that ensures failures before, during, or after the compaction task will not result in inconsistencies when state is rebuilt from the log. In order to ensure tombstones are removed only after any prior related entries, the major compaction task simply compacts segments in sequential order from the first index of the first segment to the last index of the last committed segment. This ensures that if a failure occurs during the compaction process, only entries earlier in the log will have been removed, and potential tombstones which erase the state of those entries will remain.

<h3 id="log-tombstone-safety">8.5 Ensuring tombstones are applied on all servers</h3>

Typically, as commands are stored on a majority of servers, committed, and applied to the state machine, they can be safely removed from the log once they no longer contribute to the state machine’s state. But a particular nuance in tombstones necessitates that they be applied on all servers prior to being removed from the log. Tombstones are typically cleaned immediately after they’re applied to the state machine and after any prior related commands are cleaned.

{% include lightbox.html href="/assets/img/docs/tombstone_compaction.png" desc="Tombstone compaction" %}

*This figure illustrates the inconsistencies that can occur if tombstones are not stored on all servers. Entries that assign the value nil are tombstones. When a tombstone is applied, the entry and any prior related entries are cleaned. The leader replicates entries up to the tombstone to server B and compacts its log before sending entries to server C and server C fails to remove the entry at index 4 from its log.*

Some systems like Kafka handle tombstones by aging them out of the log after a large interval of time. If we translate this approach to Raft, tombstones must be stored on all servers within a bounded time frame. This ensures that systems have an opportunity to receive and apply tombstones prior to being removed from the log. However, we found this time bound to be less than ideal and wanted to instead ensure that tombstones have been persisted on all servers prior to cleaning them from the log. Instead, we extend the Raft algorithm to keep track of which entries have been applied on all servers. By keep track of the highest index stored on all servers, servers can safely compact tombstones from their logs sooner.

Just as with the `commitIndex`, the leader is responsible for tracking which entries have been stored on all servers — known as the `globalIndex` — and sharing that information with followers through AppendEntries RPCs. The `globalIndex` is calculated simply as the minimum matchIndex for all servers in the cluster. Servers only perform major compaction to remove tombstones for segments for which all indices are less than the `globalIndex`. This ensures that tombstones are not removed from the log until they have been stored on all servers, and once stored each server will not remove any tombstone until it has been applied to and cleaned by the state machine.

<h3 id="major-compaction-safety">8.6 Preventing race conditions in major compaction</h3>

The major log compaction process as described thus far poses a potential issue for active servers. We wanted to allow the state machine to safely clean entries from the log at any point in time. This means we cannot assume once a tombstone is applied to the state machine it will be immediately cleaned. For instance, a command that sets a time-to-live (TTL) on a key is actually a tombstone since it ultimately results in the removal of state, but it won’t be cleaned from the log until the amount of time specified by the TTL has expired. Because segments of the log are compacted sequentially, if the state machine continues to clean entries from the log during major compaction, inconsistencies can result.

In order to ensure consistency, major compaction processes must ensure that if a tombstone is removed from the log, all prior related entries have been removed as well. If the state machine continues to mark entries for cleaning from the log during the major compaction process, a race condition can cause inconsistencies in the log. The state of cleaned entries in the log is not persisted to disk for performance reasons, and so it’s important to note that the state of the log should always reflect the state of the state machine even if the state machine has marked entries for removal from the log since in the event of a crash and recovery, the log will lose information about which entries were cleaned.

{% include lightbox.html href="/assets/img/docs/major_compaction_race.png" desc="Major Compaction Race" %}

*This figure illustrates how allowing state machines to continue cleaning logs during major compaction can result in inconsistencies in the log. After the major compaction process writes the first segment, the state machine cleans tombstones from the second segment. The major compaction process rewrites the second segment without tombstones, resulting in an inconsistent state in the log.*

In order to prevent race conditions while removing tombstones from the log, we take an immutable snapshot of the state of cleaned entries at the start of log compaction. This ensures that the scenario in figure n cannot occur.

<h3 id="major-compaction-liveness">8.7 Liveness in major compaction</h3>

The algorithm for ensuring log state remains consistent by storing tombstones on all servers introduces a liveness issue. If any server is down, `globalIndex` cannot increase and thus individual servers cannot continue to remove tombstones from their logs. In order to ensure servers can progress during temporary failures, we propose that leaders keep track of which servers are actively participating in replication and effectively demote servers that can’t be reached for some time period. If the leader fails to successfully heartbeat a follower for some time bound — for instance, ten heart beats — it demotes the follower by committing a configuration change. Once the configuration change has been applied, the next AppendEntries RPC to that follower will truncate the follower’s log and begin resending entries. This allows live servers to continue to compact their logs, including removing tombstones, and ensures that servers are caught up safely once they rejoin the cluster.

One concern with this algorithm is that it requires servers to be caught up from the start of their logs after falling too far behind the leader. But this is effectively not very different from a similar restriction placed on snapshotted logs. In a cluster that uses snapshots for log compaction, if any server crashes for some period of time or otherwise falls too far behind the leader, the leader will ultimately have to send its snapshot to the follower once it rejoins the cluster. In Copycat, the log effectively represents a snapshot of the state machine at any point in time — albeit with greater overhead in most cases — so we contend that the performance impact of sending complete logs to followers is minimal as compared to snapshotting.

<h3 id="log-compaction-time">8.8 Managing time and timeouts in a compacted log</h3>

Many Raft implementations use the replicated Raft log to provide a consistent view of time. To do so, implementations append the leader’s timestamp to certain entries in the log. When an entry is applied to the state machine, the entry’s timestamp is used to increment a monotonically increasing logical clock. This approach can be used to expire keys or sessions. Indeed, sessions as described in the Raft literature use leader timestamps to remove expired session information from memory when a client fails to send a keep-alive request to the cluster in a timely manner.

But log cleaning poses a particularly daunting challenge with respect to handling time through the Raft log. Because servers can compact their logs independently of one another and commit and other indexes progress independently as well, state machines on different servers may see large gaps in time in the log. For example, session keep-alive RPCs are committed to the log as special keep-alive entries, and sessions are expired when the log time progresses at least a session timeout beyond the last keep-alive entry committed for a given session. This means in order to ensure sessions are not improperly expired on a replay of the log, we would have to retain every keep-alive entry from every live session. If a keep-alive entry were compacted from the log, that could result in a session being improperly expired. But retaining all keep-alive entries for all live sessions is simply not practical.

In order to handle time based expirations in conjunction with log cleaning, we impose the requirement that only the leader can expire a session by committing a special entry to unregister the session. Leaders always see all log entries after the start of their term, and session expirations are always reset at the beginning of a leader’s term. By committing a separate entry to unregister a session, we ensure that sessions can only be expired by the server with the most consistent view of time and sessions will never be expired as a result of missing entries that have been compacted from the log.

Nevertheless, it's clear to us that managing time and expirations through the Raft log poses significant challenges for systems that rely on log cleaning. Thus, we recommend that compaction for time-based commands be managed through snapshots as described in section [8.10](#snapshots-via-log-cleaning).

<h3 id="log-compaction-membership-changes">8.9 Handling configuration changes</h3>

Any implementation of the Raft consensus algorithm would incomplete without support for cluster configuration changes. Raft literature suggests a couple well-defined approaches to configuration changes. But configuration changes pose particular issues with the concept of tracking the index of globally replicated entries. When a new server joins the cluster, its log is empty. Thus, any previous `globalIndex` is effectively invalidated by a new member.

![Global index unsafe](/assets/img/docs/global_index_unsafe.png){: height="500px"}

*This figure illustrates a case wherein replicating cleaned entries to a joining server can result in inconsistent logs. The grey boxes represent entries that have been cleaned but not removed from the log, and the write boxes represent entries that have been both cleaned and removed from the log. Server 1 begins replicating entries to the new member, Server 4, and crashes after replicating entries up to index 6. Server 2 is then elected leader and continues replicating entries to Server 4. However, because server 2 compacted entries from its log before Server 1, Server 1 ended up sending entries to Server 4 that were already removed from Server 2. This results in Server 1 sending entries that will never be compacted on Server 4 and thus results in an inconsistent state. By excluding cleaned entries where the entry index is less than the `globalIndex`, servers can ensure this type of inconsistency cannot result from catching up a joining server.*

In a typical Raft cluster, the `commitIndex` is monotonically increasing. However, there are certain scenarios where the `commitIndex` can be decreased, such as in the case of a full cluster restart, and that does not break any of the guarantees of Raft. Similarly, it is safe to decrease the `globalIndex` without impacting the safety of the log compaction algorithm.

![Global index safe](/assets/img/docs/global_index_safe.png){: height="500px"}

*This figure illustrates how servers replicate logs without cleaned entries to members joining the cluster. By removing cleaned entries when they're sent to a new server, the new server cannot receive globally committed entries that would otherwise have been compacted given the full context of the log, and so switching servers is safe.*

<h3 id="snapshots">8.10 Implementing snapshots via log cleaning</h3>

Snapshots are the typical mechanism by which Raft servers compact their logs. Snapshots work by periodically writing the state machine’s state to a snapshot on disk and then removing all entries up to the last index applied to the state machine. While snapshots can impact performance, they do provide a significantly simpler approach for managing system state with respect to log compaction. Indeed, some types of state machines - such as counting state machines - necessitate snapshotting. With snapshots, state machines do not have to keep track of which commands apply to their state since a snapshot represents the complete state machine state at a point in logical time. Thus, we wanted to find a way to take advantage of the simplicity of snapshots while maintaining the performance advantages of sequential writes during log compaction.

Snapshots are implemented on top of Copycat’s log cleaning algorithm. A snapshot of the state machine’s state is taken each time the log rolls over to a new segment and the `commitIndex` surpasses the last index of the previous segment, thus making the prior segment compactable. When a snapshot is taken, the state machine writes its state to a snapshot file on disk and Copycat cleans all snapshottable entries (entries which indicate they're compacted via snapshots) up to the last applied index.

<h3 id="log-cleaning-snapshots">8.11 Combining snapshots and log cleaning</h3>

Snapshottable commands are commands applied to the state machine for which associated state is persisted in a snapshot once taken. In contrast to typical snapshotting in Raft, though, there is some potential in Copycat for snapshottable commands to be applied to the state machine after a later snapshot has already been taken. If a server stores a snapshot of its state and crashes before it can compact prior snapshottable commands from its log, snapshottable commands will be replayed to the state machine on recovery. Thus, state machine implementations must take care to overwrite state from snapshottable commands when installing a snapshot just as state from snapshottable commands is stored in a snapshot.

<h3 id="snapshot-session-events">8.12 Managing session events for snapshotted logs</h3>

Session event messages are derived from individual commands applied to the state machine. Event messages are stored in memory for fault tolerance, and in the event of a crash and replay of the Raft log event messages must be recreated from the commands on disk. This means individual commands must must be retained in the log until related events have been received by all clients. If a snapshot is taken of the state machine state and snapshotted entries are removed from disk before being received by all clients, a failure of the server can result in lost session event messages.

State machines could potentially store session event messages in snapshots, but this seems impractical considering the entries needed to rebuild the event messages are already stored in the Raft log, and the interval of time between an event message being sent and acknowledge is typically short. Thus, we opted to ensure event messages can be rebuilt from the log by waiting to persist snapshots until all prior related messages have been received.

When a snapshot of the state machine’s state is taken, the snapshot is stored on disk but is not effectively committed until all session events up to the snapshot index have been acknowledged by clients. Once all events have been acknowledged, the server commits the snapshot and cleans snapshottable entries from the log.

{% include common-links.html %}