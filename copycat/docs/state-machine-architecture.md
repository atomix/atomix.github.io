---
layout: docs
project: copycat
menu: docs
title: State Machine Architecture
pitch: Raft architecture and implementation
first-section: state-machine-architecture
---

<h2 id="state-machines">4 State Machines</h2>

Each server is configured with a state machine to which it applies committed commands and queries. State machine operations are executed in a separate state machine thread to ensure that blocking state machine operations do not block the internal server event loop.

Servers maintain both an internal state machine and a user state machine. The internal state machine is responsible for maintaining internal system state such as sessions and membership and applying commands and queries to the user-provided `StateMachine`.

<h3 id="deterministic-scheduling">4.1 Deterministic Scheduling</h3>

Because of the complexities of coordinating distributed systems, time does not advance at the same rate on all servers in the cluster. What is essential, though, is that time-based callbacks be executed at the same point in the Raft log on all nodes. In order to accomplish this, the leader writes an approximate Instant to the replicated log for each command. When a command is applied to the state machine, the command's timestamp is used to invoke any outstanding scheduled callbacks. This means the granularity of scheduled callbacks is limited by the minimum time between commands submitted to the cluster, including session register and keep-alive requests.

{% include common-links.html %}
