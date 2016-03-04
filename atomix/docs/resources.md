---
layout: docs
project: atomix
menu: docs
title: Distributed Resources
pitch: Common abstractions for distributed coordination
first-section: what-are-resources
---

The true power of Atomix comes from [Resource] implementations. Resources are named distributed objects that are replicated and persisted in the Atomix cluster. Each name can be associated with a single resource, and each resource is backed by a replicated state machine managed by Atomix's underlying [implementation of the Raft consensus protocol](/copycat/docs/internals).

Resources are created by simply using one of `Atomix`'s `get` methods or passing a custom `Resource` class to `get`:

```java
DistributedMap<String, String> map = atomix.getMap("my-map").get();
```

Atomix create a replicated [StateMachine][StateMachine] on each replica in the cluster. Operations performed on the resource are submitted as state changes to the cluster where they're replicated and persisted before being applied to the replicated state machine.

Atomix provides a number of resource implementations for common distributed systems problems. Currently, the provided resources are divided into three subsets that are represented as Maven submodules:

* [Distributed collections](#distributed-collections) - `DistributedSet`, `DistributedMap`, `DistributedMultiMap`, `DistributedQueue`
* [Distributed atomic variables](#distributed-variables) - `DistributedValue`, `DistributedLong`
* [Distributed coordination tools](#distributed-coordination) - `DistributedLock`, `DistributedGroup`
* [Distributed messaging](#distributed-messaging) - `DistributedTopic`, `DistributedMessageBus`

### Consistency Levels

When performing operations on resources, Atomix separates the types of operations into two categories:

* *commands* - operations that alter the state of a resource
* *queries* - operations that query the state of a resource

The [Raft consensus algorithm][raft-framework] on which Atomix is built provides strict linearizability requirements for all commands and queries submitted to the cluster. When a command is submitted to the cluster, the command will always be forwarded to the cluster leader and replicated to a majority of servers before being applied to the resource's state machine and completed.

But real-world systems often must relax reliability and consistency constraints in order to acheive better performance. Thus, Atomix provides simple tools to empower users to modify the behavior of Atomix's consensus algorithm according to their needs. When a resource operation is submitted to the cluster, the operation is handled according to the resource's configurable consistency setting.

To configure the [ReadConsistency] or [WriteConsistency] for a resource, use the `with` method:

```java
DistributedLock lock = atomix.getLock("my-lock").get();

lock.with(WriteConsistency.ATOMIC).lock().thenRun(() -> System.out.println("Lock acquired!"));
```

Atomix provides different consistency levels for controlling the behavior of write operations submitted to the cluster:

* `WriteConsistency.ATOMIC` - Guarantees atomicity ([linearizability]) for write operations and events. Atomic write consistency enforces sequential consistency for concurrent commands from a single client by sequencing commands as they're applied to the Raft state machine. If a client submits writes a, b, and c in that order, they're guaranteed to be applied to the Raft state machine and client futures are guaranteed to be completed in that order. Additionally, linearizable commands are guaranteed to be applied to the server state machine some time between invocation and response, and command-related session events are guaranteed to be received by clients prior to completion of the command.
* `WriteConsistency.SEQUENTIAL_EVENT` - Guarantees atomicity ([linearizability]) for write operations and sequential consistency for events triggered by a command. All commands are applied to the server state machine in program order and at some point between their invocation and response (linearization point). But session events related to commands can be controlled by this consistency level. The sequential consistency level guarantees that all session events related to a command will be received by the client in sequential order. However, it does not guarantee that the events will be received during the invocation of the command.

Similarly, Atomix provides different consistency levels for read operations:

* `ReadConsistency.ATOMIC` - Guarantees atomicity ([linearizability]) for read operations. The atomic consistency level guarantees linearizability by contacting a majority of the cluster on every read. When a Query is submitted to the cluster with linearizable consistency, it must be forwarded to the current cluster leader. Once received by the leader, the leader will contact a majority of the cluster before applying the query to its state machine and returning the result. Note that if the leader is already in the process of contacting a majority of the cluster, it will queue the Query to be processed on the next round trip. This allows the leader to batch expensive quorum based reads for efficiency.
* `ReadConsistency.ATOMIC_LEASE` - Guarantees atomicity ([linearizability]) for read operations. The atomic consistency level guarantees linearizablearizability by contacting a majority of the cluster on every read. When a Query is submitted to the cluster with linearizable consistency, it must be forwarded to the current cluster leader. Once received by the leader, the leader will contact a majority of the cluster before applying the query to its state machine and returning the result. Note that if the leader is already in the process of contacting a majority of the cluster, it will queue the Query to be processed on the next round trip. This allows the leader to batch expensive quorum based reads for efficiency.
* `ReadConsistency.SEQUENTIAL` - Guarantees sequential consistency for read operations. Sequential read consistency requires that clients always see state progress in monotonically increasing order. Note that this constraint allows reads from followers. When a sequential Query is submitted to the cluster, the first server that receives the query will handle it. However, in order to ensure that state does not go back in time, the client must submit its last known index with the query as well. If the server that receives the query has not advanced past the provided client index, it will queue the query and await more entries from the leader.
* `ReadConsistency.CAUSAL` - Guarantees causal consistency for read operations. Causal consistency requires that clients always see non-overlapping state progress monotonically. This constraint allows reads from followers. When a causally consistent Query is submitted to the cluster, the first server that receives the query will attempt to handle it. If the server that receives the query is more than a heartbeat behind the leader, the query will be forwarded to the leader. If the server that receives the query has not advanced past the client's last write, the read will be queued until it can be satisfied.

Overloaded methods with consistency parameters are provided throughout Atomix's resources wherever it makes sense. In many cases, resources dictate the strongest consistency levels - e.g. [coordination] - and so weaker consistency levels are not allowed.

{% include common-links.html %}