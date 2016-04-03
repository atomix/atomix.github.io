---
layout: docs
project: copycat
menu: docs
title: Cluster Architecture
pitch: Raft architecture and implementation
first-section: cluster-architecture
---

<h2 id="the-copycat-cluster">2 The Copycat Cluster</h2>

The structure of Copycat clusters differs significantly from typical Raft clusters primarily due to the need to support greater flexibility in systems in which Copycat is embedded. High-availability systems cannot be constrained by the strict quorum-based requirements of consensus algorithms, so Copycat provides several node types to address scalability issues.

Copycat clusters consist of three node types: active, passive, and reserve.

 * *active* nodes are stateful servers that fully participate in the Raft consensus algorithm
 * *passive* nodes are stateful servers that do not participate in the Raft consensus algorithm but receive only committed log entries from followers
 * *reserve* nodes are stateless servers that can be transitioned in and out of stateful states

The architecture of clusters allows Copycat to be embedded within highly-available systems without significant impact to availability. Copycat provides an interface to allow any node in the cluster to add, remove, promote, or demote nodes at will. Systems that embed Copycat can use Raft's membership change algorithm to coordinate modifications to the cluster's structure. The use of stateful Raft nodes and stateful asynchronous nodes allows systems to quickly replace Raft nodes by promoting and demoting members.

All cluster membership and member state changes are committed as configuration changes through the Raft portion of the cluster. We implement the single member approach to configuration changes to simplify safety requirements during [configuration changes](#membership-changes).

Each stateful server in a cluster maintains two logical state machines. An internal state machine on each server is responsible for managing sessions, connections, and scheduling within the user state machine, and the user state machine contains application logic. Commands submitted by clients are forwarded to the Raft leader where they're logged, replicated, and applied to the user state machine on each server. Queries submitted by clients are handled either by the server to which the client is connected or forwarded to the Raft leader depending on [consistency constraints](#client-queries).

{% include common-links.html %}
