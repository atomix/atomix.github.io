---
layout: docs
project: copycat
menu: docs
title: Session Events
pitch: Raft architecture and implementation
first-section: session-events
---

<h2 id="session-events">5 Session Events</h2>

Typical implementations of the Raft consensus algorithm expose an API to allow users to alter state in the state machine. But more complex coordination may often require that clients learn about changes in the state machine as well. A naive implementation of this is polling. Polling requires that clients periodically request any state changes from the cluster, but it also implies greater latency and load on the cluster. In order for a client to learn about a state change event, the client must first make a request to the cluster, and all clients must poll the cluster regardless of whether there are any notifications waiting. Long polling can reduce the number latency of receiving events from the cluster, but it precludes pipelining events to the client. Alternatively, systems can push state change notifications to clients. Copycat servers use this approach to push state machine events to clients.

In many cases, clients can essentially behave as extensions of the replicated state machine by receiving notifications from the cluster. For instance, continuing with the lock example, a lock state machine may push lock and unlock events to clients. This implies that order and fault-tolerance are important. If a client receives a lock and then unlock event, it will believe the state of the lock to be unlocked. Conversely, if a client receives an unlock and then lock event, the final state will be locked. The same is true of reliability. If a client receives only a lock or unlock event without its opposite, it can result in an inconsistent state across clients.

For these reasons, session event notifications cannot be implemented as simple messages to the client. Networks are unreliable, and we must assume that messages may be arbitrarily lost or reordered. Fortunately, Raft provides the primitives on which events can be pushed to clients in a fault-tolerant manner. In order to do so, we simply extended Raft's sessions to encapsulate the framework for guaranteeing order in session events.

<h3 id="publishing-events-from-the-state-machine">5.1 Publishing Events from the State Machine</h3>

State machines push event messages to clients as part of their normal operation. Referred to as session events, messages are published to clients during the application of normal operations to the state machine. For instance, while a lock is held by one session, a lock state machine might queue additional sessions waiting for the lock to be released. Once the lock is released, the state machine could push a release notification to the next session in the queue. By publishing session events in response to commands being applied to the state machine, we can infer order among the events across the different servers in the cluster.

Session events are typically pushed to the client by the server to which the client is connected. If the client is connected to a follower, that follower will push session events to the client. If the client is connected to the leader, the leader will push session events to the client. However, for fault tolerance and consistency, it's still critical that all servers store session events in memory. State machines should behave deterministically regardless of whether a client is connected to the server managing any given state machine.

{: class="text-center"}
{% include lightbox.html href="/assets/img/docs/session_event_consistency.png" desc="Session event fault-tolerance" %}
*This figure illustrates why it's important that events be stored in memory on each server even though they may be sent to the client by only one server. In (a) `S1` sends three events to the client. The client acknowledges two of the three events before `S1` crashes in (b). The client submits a KeepAlive RPC which acknowledges events up to index `3` on `S2` and `S3` as is depicted in (c). Finally, in (d) the client reconnects to `S2` which sends events for indexes `4` and `5` to the client.*

All events are sent to and received by the client in sequential order. This makes it easier to reason about events and aids in tracking which events have been received by the client. In order to track events, each event is sent to the client with the index of the state machine command that triggered the event. The client expects to receive events in monotonically increasing order. However, because not all commands applied to the state machine may result in events published to any given session, the protocol must account for skipped indexes as well.

Sending only the index of each event published to the client provides the client with the context necessary to determine that it received some events in order, but not that it received all events.  If a server publishes event indexes `1` and `3` to a client, the client can ensure that those events were received in order, but without additional metadata it doesn't know whether it should have received an event for index `2`. Thus, in order to handle missing indexes in the order of events for any given session, servers must include the index of the previous event sent to the client, aptly called `prevIndex`. The `prevIndex` provides clients the necessary context to determine whether all events have been received in order. If a client receives an event message with a `prevIndex` greater than the last index for which it received an event, it can reject the event and request missing messages.

{: class="text-center"}
{% include lightbox.html href="/assets/img/docs/session_event_sequencing.png" desc="Session event sequencing" height="400px" %}
*This figure illustrates how session event messages are sequenced when sent from a server to a client. For each command applied to the state machine, zero or more session event messages can be pushed to the client. The client sequences the events in the order in which they were published by the stat machine.*

Similarly, some commands may result in multiple event messages being published to the same session, and order may still be important within multiple events for a single index. For instance, in a lock state machine, it may be possible for a session to passively listen for lock state change events. The release of the lock may result in two events related to a single command — release the lock from one session and then acquire the lock for another session — and order remains important for this binary state machine. Servers must ensure that clients can determine the order in which to handle events within a single index.

The simplest and most efficient approach to ensuring order among event messages within a single index is to send messages in batches to the client. Using this approach, messages for one or more indices could be sent in a single batch and in the order in which they were produced on the server. The server would await the completion of the command before sending the batch.

However, in cases where the number of event messages for a single index may exceed a reasonable batch size, messages must be explicitly ordered within indexes. To order many messages within a single index, Publish RPCs to the client must include a starting offset and `prevOffset` which denote the offset of the first message within the index in the RPC and the offset of the end of the previous message. The latter is necessary because there is no fixed number of event messages per batch. Thus, when a batch crosses indexes, the `prevOffset` effectively indicates the number of messages in the batch for the previous index.

<h3 id="sequencing-events-on-the-client">5.2 Sequencing Events on the Client</h3>

While event messages are in transit between the server and client, we assume messages can be arbitrarily lost or reordered. Individual requests can take several paths to the client depending on the cluster and client configurations, and different messages from the same server can travel different routes to the client. But as with other areas of the system, our goal was to implement sequential consistency for session events. Strict ordering simplifies reasoning about a system and allows the client to essentially act as an extension of the replicated state machine.

A prime example of the need for strict ordering in session events is distributed locks. Locks represent a binary state machine; a lock is either in the locked or unlocked state. If a state machine publishes two events — lock and unlock — to a client, the order is critical. If the client receives lock and then unlock it will believe the final state of the lock to be unlocked; conversely, if the client receives unlock and then lock it will believe the opposite. For this reason, it's crucial that clients receive event messages in the order in which they were sent by the state machine.

In order to guarantee ordering of session events published to a client, the client tracks the index of the last event batch received in sequence and uses it to validate that future events are received in sequence. The algorithm for receiving an event batch on the client is as follows:

* Compare the batch's `prevIndex` with the local `eventIndex`
* If `eventIndex` is less than `prevIndex` respond with `eventIndex` indicating the last event batch received in sequence
* If `eventIndex` is equal to or greater than `prevIndex` ignore the event batch and respond successfully
* If `eventIndex` is equal to `prevIndex` update the local event index with the current batch index and process the event batch
* Update the local `eventIndex` with the batch index

The client initializes its `eventIndex` to its session ID. When the client receives a batch of events, it validates the request's `prevIndex` against its local `eventIndex` to verify that the batch is the next in the sequence. If the batch was received out of order, it responds immediately indicating the index of the last event batch received in sequence. This allows the sending server to resend batches from that point.

{: class="text-center"}
{% include lightbox.html href="/assets/img/docs/session_event_coordination.png" desc="Client session event coordination" %}
*This figure depicts the process with which a client coordinates with a server pushing event messages to the client. In (a) the server sends event messages for index `5` to the client with a ``prevIndex`` of `2`. However, because the client last received events for index `2`, the client rejects the events in (b) and sends its ``prevIndex`` `2` back to the server. The server then sends entries for index `3` with a ``prevIndex`` of `2` (c) and the client acknowledges receipt of the events in sequence in (d).*

Once events have been sequenced on the client, they must also be sequenced according to the order of responses received from the cluster. Clients should receive responses and events in the order in which they occur in state machines. In the event that a command, event, and query all occur at the same state machine index, the order of precendence for the operations is:
* command
* event
* query

This means if a client submits a command that publishes an event back to the same client and concurrently submits a query, the client should first see the command response, then the event, then the query response.

Because operation responses and events are sent to the client separately, it's the responsibility of the client to place them in the appropriate order. To facilitate this process, all command and query responses contain an `eventIndex` that indicates the last index for which an event was published to the client. Command responses will always contain an `eventIndex` less than the command index since events published by the command occur *after* the command. Queries may contain an `eventIndex` less than or equal to the query index.

To sequence operation responses and events, when a response is received clients first sequence the response according to their request order. Leaders are followers guarantee that operations will be applied to state machines in the order in which they were sent by the client, so ensuring the responses for those operations are placed in the order in which they were sent ensures that operation state is monotonically increasing. Once placed in sequential order on the client, if a response is received with an `eventIndex` greater than the last received event index, the response is enqueued until events are received. When an event is received, pending responses are checked to determine whether the next response has met the criteria for completion. Once events up to a response's `eventIndex` have been received, those events are completed in the client's event thread before completing the response in the same thread. To ensure that events can be received independent of responses, if an event is received when no requests from the client are pending, the event is immediately completed.

<h3 id="managing-server-memory">5.3 Managing Server Memory</h3>

As commands are committed to the Raft log and applied to server state machines, servers may push an arbitrary number of event messages to any session in response to any given command. In order to maintain fault-tolerance, each server must hold session events in memory even if the client to which an event was published is not connected to that server. This ensures that in the event of the failure of the server to which a client is connected, the client can reconnect to another server and continue to receive events for its session.

However, as session events are received by the clients, servers need a way to remove unneeded events from memory. The [session expiration process](#session-expiration) ensures that events are only retained in memory as long as a session is alive. When a session is unregistered or expires, so too should event messages published to that session be removed from memory. But for long-running sessions which receive a large number of events, servers should be able to remove events that have already been received by the client.

Clients only ever have direct communication with a single server. The client exchanges sufficient information with that server to remove acknowledged events from that server's memory. When a client responds successfully to a *Publish* RPC, the publishing server can safely remove events for that session up to the `ackIndex` provided by the client. But this doesn't account for the other servers in the cluster.

In order to ensure all servers clear acknowledged events from memory, each client must include in its periodic *KeepAlive* RPCs the highest index for which it has received events in sequential order. When the leader logs and commits a *KeepAlive* entry, state machines on each server can remove events up to the provided `eventIndex`.

<h3 id="recovering-messages-after-a-server-failure">5.4 Recovering Messages After a Server Failure</h3>

Many implementations of the Raft consensus algorithm allow certain operations to be executed on a single node in the cluster. Read-only operations can safely be evaluated on a follower without losing sequential consistency by tracking the index of the last entry seen by the client. But because session events rely on replication of commands through the Raft log for fault tolerance, state machines must publish events only in response to operations that have been written and committed to the Raft log. This ensures that events are published by a majority of the cluster and will not be lost in the event of a failure because, once committed, commands themselves are guaranteed to be stored on a majority of servers.

<h3 id="managing-log-compaction">5.5 Managing Log Compaction</h3>

Session event messages are retained in server state machines until the client acknowledges receipt or the client's session times out. In the event of a server crash, servers must be able to recover session events to retain fault tolerance. For this reasons, state machines must ensure that commands which create session event messages are retained in the log until those events are received by their respective clients. If servers remove commands from their logs before related event messages have been acknowledged by clients, this can result in a liveness (good things will eventually happen) violation. Session events are ordered on the client based on the index of the previous event sent to the client. But servers lose contextual information when compacting their logs.

Once an event has been acknowledged by a client either directly to the server that pushed the event message or via the application of a *KeepAlive* entry, the triggering command can be safely removed from the log. Given that multiple sessions may be open at any given time, this means the log can be safely compacted only up to the lowest index for which events have been received by all clients. We call this the `completeIndex`. When a *KeepAlive* entry is applied to a state machine, the `completeIndex` is calculated. Given the lowest index for which events have been received by all sessions, we can then safely compact logs up to that index.

But using the `eventIndex` provided by each client in *KeepAlive* RPCs will not suffice to properly track the `completeIndex`. Sessions are designed to allow indexes to be arbitrarily skipped as it pertains to session events. Indeed, some sessions could conceivably publish only a single event in their lifetime. In that case, if a single event is ever published to a session, the session's `ackIndex` will remain at the index of that single event until another event is published or the session is unregistered or expired. Thus, in order to ensure `completeIndex` continues to advance in the absence of session events, the lowest `ackIndex` for each session should be calculated as `n - 1` where `n` is the lowest index for which an event has not been acknowledged. If no events are awaiting acknowledgment, the `ackIndex` for the session is equal to `lastApplied`.

The complete algorithm for tracking `completeIndex` is as follows:

* When a *KeepAlive* entry is applied, remove events from the appropriate session up to and including `ackIndex`
* If events are still waiting for acknowledgment, recalculate the `ackIndex` for the session as n - 1 where n is the index of the first event waiting to be acknowledged
* If no events remain in memory, set `ackIndex` to `lastApplied`
* Recalculate `completeIndex` as the minimum of `ackIndex` for all sessions

For sessions where no events are waiting to be acknowledged, `ackIndex` must increase with `lastApplied` in order to ensure `completeIndex` is properly recalculated. Additionally, `completeIndex` may be recomputed each time `lastApplied` is incremented, or it may be recomputed at regular intervals according to the log compaction schedule.

Given the lowest index for which events have been received by all clients, it is safe to remove related commands from the log. Log compaction processes must use the `completeIndex` to dictate which sections of their logs can be safely removed. For [log compaction](#log-compaction) this means only entries up to the `completeIndex` may be removed from the log. This ensures that in the event of a crash and recovery, the state machine can safely recreate all events that have yet to be acknowledged by their respective clients.

For systems that do snapshot-based log compaction, servers could persist pending event messages with the snapshot. However, because events are based on commands that are already present in the log, we feel it would be redundant to store the event messages themselves and is ideal to instead exclude events from log compaction altogether. The session expiration feature ensures liveness — that each session will either receive its events or expire — so awaiting the receipt of events during log compaction should be not significantly slow the process down. Excluding events from snapshots both reduces the size of snapshots and ensures that events related to later-expired sessions are not retained in the log. To persist a snapshot after related events have been received by their clients, servers should store a snapshot of their log at a specific index and then wait for the `snapshotIndex` and `completeIndex` to converge before removing entries from the log. In other words, the snapshot should only become effectively committed and entries should only be removed from the log once all event messages up to the snapshot index have been received by clients.

The drawback to this approach to log compaction is that commands for which no events were published or for which events were already acknowledged by clients often cannot be removed from the log because earlier events may still be pending. However, we feel the liveness properties of sessions make this an acceptable trade-off. Still, we have conceived an optimized approach for incremental log compaction that does not require waiting for events for unrelated commands to be received by clients. By checking each entry against in-memory session events, commands for which no events were published or for which published events were acknowledged by receiving clients can be safely removed from the log. We suspect this algorithm would work well with incremental log compaction since entries are evaluated and removed on an individual basis, but unfortunately it cannot be applied to snapshot-based approaches since a snapshot implies a fixed point in time and operates only on chunks of entries in the log.

{% include common-links.html %}
