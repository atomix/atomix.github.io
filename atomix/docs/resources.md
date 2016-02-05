---
layout: docs
project: atomix
menu: docs
title: Distributed Resources
pitch: Common abstractions for distributed coordination
first-section: what-are-resources
---

The true power of Atomix comes from [Resource][Resource] implementations. Resources are named distributed objects that are replicated and persisted in the Atomix cluster. Each name can be associated with a single resource, and each resource is backed by a replicated state machine managed by Atomix's underlying [implementation of the Raft consensus protocol][raft-framework].

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

### Consistency levels

When performing operations on resources, Atomix separates the types of operations into two categories:

* *commands* - operations that alter the state of a resource
* *queries* - operations that query the state of a resource

The [Raft consensus algorithm][raft-framework] on which Atomix is built provides strict linearizability requirements for all commands and queries submitted to the cluster. When a command is submitted to the cluster, the command will always be forwarded to the cluster leader and replicated to a majority of servers before being applied to the resource's state machine and completed.

But real-world systems often must relax reliability and consistency constraints in order to acheive better performance. Thus, Atomix provides simple tools to empower users to modify the behavior of Atomix's consensus algorithm according to their needs. When a resource operation is submitted to the cluster, the operation is handled according to the resource's configurable `Consistency` setting.

To configure the `Consistency` for a resource, use the `with(Consistency)` method:

```java
DistributedLock lock = atomix.getLock("my-lock").get();

lock.with(Consistency.ATOMIC).lock().thenRun(() -> System.out.println("Lock acquired!"));
```

Atomix provides four consistency levels for controlling the behavior of read and write operations submitted to the cluster:

* `Consistency.ATOMIC` - Provides guaranteed [linearizability][Linearizability] by sequencing and deduplicating writes submitted to the cluster by each client and sequencing and deduplicating events sent from server-side replicated resource state machines back to the client. This means all state changes and events are guaranteed to occur in the order specified by the client and at some time between the invocation and response of the respective operation.
* `Consistency.SEQUENTIAL` - Provides probable [linearizability][Linearizability] for write operations submitted to the cluster via a leader-lease algorithm and [sequential consistency][SequentialConsistency] for reads and events sent from server-side replicated resource state machines. This means all state changes and events are guaranteed to occur in the order specified by the client, writes will be applied some time between the invocation and response of the respective write operation, and the client will see state progress monotonically (never back in time).
* `Consistency.PROCESS` - Provides probable [linearizability][Linearizability] for write operations submitted to the cluster via a leader-lease algorithm, [sequential consistency][SequentialConsistency] for events sent from server-side replicated resource state machines, and [causal consistency][CausalConsistency] for reads submitted by a single client. This means non-overlapping state changes and events are guaranteed to occur in the order specified by the client, writes will be applied some time between the invocation and response of the respective write operation, and the client will see state progress monotonically (never back in time).
* `Consistency.NONE` - Provides no linearizability, sequential consistency, or causal consistency guarantees for clients. This means that while Atomix's internal commit log will remain consistent, from the client's perspective state can move arbitrarily forward or backward in time.

Overloaded methods with `ConsistencyLevel` parameters are provided throughout Atomix's resources wherever it makes sense. In many cases, resources dictate the strongest consistency levels - e.g. [coordination] - and so weaker consistency levels are not allowed.

{% include common-links.html %}