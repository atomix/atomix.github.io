---
layout: docs
project: copycat
menu: docs
title: Architecture Introduction
pitch: Raft architecture and implementation
first-section: architecture-introduction
---

Copycat is an advanced, feature complete implementation of the [Raft consensus algorithm][Raft] which has been developed over a period of nearly three years. The implementation goes well beyond the [original Raft paper][raft-paper] and includes a majority of the full implementation described in Diego Ongaro's [Raft dissertation][raft-dissertation] in addition to several extensions to the algorithm.

In some cases, Copycat's Raft implementation diverges from recommendations. For instance, Raft dictates that all reads and writes be executed through the leader node, but Copycat's Raft implementation supports per-request consistency levels that allow clients to sacrifice linearizability and read from followers. Similarly, Raft literature recommends snapshots as the simplest approach to log compaction, but Copycat prefers an incremental log compaction approach to promote more consistent performance throughout the lifetime of a cluster. In other cases, Copycat's Raft implementation extends those described in the literature. For example, Copycat's Raft implementation extends the concept of sessions to allow server state machines to publish events to clients.

It's important to note that wherever Copycat diverges from standards and recommendations with respect to the Raft consensus algorithm, it does so using well-understood algorithms and methodologies that are either described in the Raft literature or frequently discussed within the Raft community. Copycat does not attempt to alter the fundamental correctness of the algorithm but rather seeks to extend it to promote usability in real-world use cases.

The following documentation details Copycat's implementation of the Raft consensus algorithm and in particular the areas in which the implementation diverges from the recommendations in Raft literature and the reasoning behind various decisions.

<h2 id="raft-basics">1 Raft Basics</h2>

In order to understand the context within which Copycat was developed, it's important to understand the core concepts of the Raft consensus algorithm. This section provides a brief overview of the core concepts of the algorithm, including leader election, log replication, and membership changes. Of course, the best place to read about the basics of the Raft algorithm is in the original [Raft paper][raft-paper].

Raft is a consensus algorithm designed from the ground up for understandability. It achieves this by using concepts that are relatively easy to understand and implement. At the core of Raft is a replicated log that's managed by a leader through which writes are funneled to the log and replicated throughout the cluster. The log is closely integrated with the leader election algorithm to ensure consistency.

A Raft cluster consists of three different types of nodes: *followers*, *candidates*, and *leaders*. Each server can transition between these three states given that certain conditions are met. That is, any server can be a follower, candidate, or leader. The roles of the three states are as follows:

* *follower* - the state in which a server receives replication from leaders and upon failing to receive a heartbeat from the leader for a randomized interval of time, transitions to candidate to start a new election
* *candidate* - the state in which a server attempts to be elected leader
* *leader* - the state in which a server receives commands from clients, logs and replicates commands to followers, and determines when commands have been stored on a majority of servers

Raft is typically used to model replicated state machines. Leaders receive state machine commands and write them to a local log which is then replicated to followers in batch. Once a command submitted to a leader has been logged and replicated to a majority of the cluster, the command is considered *committed* and the leader applies the command to its own state machine and responds to the client. In the event of a server restart, the server replays the committed entries in its logs to rebuild the state of the server state machine.

<h3 id="leader-election-basics">1.1 Leader Election</h3>

Raft clusters use a logical concept of time referred as a term, also known as an epoch in some other algorithms. For each term, Raft may or may not elect a leader, and only one leader may exist for any given term. Servers use a variety of timers and consistency checks to elect a leader. Once a leader is elected, all writes to the cluster go through the leader and are replicated to a majority of the cluster.

Raft's leader election algorithm is heavily dependent on the log. When a follower fails to receive a heartbeat from an existing leader for some configurable time period (the *election timeout*), the follower transitions to the candidate state and starts a new election. Raft allows any server to become a candidate and start a new election. Upon transitioning, a candidate increments the term and requests votes from all other members of the cluster. Servers vote for candidates based on simple consistency checks comparing the candidate's log with the voter's log. If a candidate requests a vote from a server whose log is more up-to-date than the candidate's or which has already voted for another candidate, the vote request is rejected, otherwise it's accepted. Once a candidate receives votes from a majority of the cluster (including itself), it transitions to leader and begins replicating entries. The integration of the Raft log directly into the election protocol ensure that only candidates whose logs contain all committed entries can be elected leader.

<h3 id="log-replication-basics">1.2 Log Replication</h3>

Logs are replicated from leaders to followers. When a command is submitted to the cluster, the leader appends the command as an entry in its log. Leaders periodically sends entries to each available follower in batches. Each batch of entries is sent with the index and term of the previous entry in the leader's log, and followers use that information to perform consistency checks against their own logs. If a follower's log is inconsistent with the leader's log, the follower will truncate entries from its log and the leader will resend missing entries to the follower. Once a majority of the servers have acknowledged receipt of a given entry, it is considered committed and is applied to the leader's state machine. Eventually, followers are notified of the commitment of the command and apply it to their own logs as well.

<h3 id="membership-changes-basics">1.3 Membership Changes</h3>

Raft supports the concept of cluster membership changes through special configuration entries in the Raft log. Configuration changes are logged and replicated like any other state change. However, in order to prevent "split brain", Raft only allows a single member to be added to or removed from the cluster at any given time, and no two configuration changes may overlap in commitment.

<h3 id="log-compaction-basics">1.4 Log Compaction</h3>

As commands are submitted to a Raft cluster and logged and replicated, the replicated log grows unbounded. In order to prevent servers from eventually running out of disk space, Raft provides a mechanism for servers to compact their logs independently of one another. The canonical form of log compaction in Raft is snapshots. Snapshots work by storing the state of the state machine at a specific point in logical time for recovery from disk. By storing the complete state of the server on disk, servers can safely remove all applied entries from their logs. In the event of a server restart, the server first installs the snapshot from disk before replaying its log to the state machine.

{% include common-links.html %}
