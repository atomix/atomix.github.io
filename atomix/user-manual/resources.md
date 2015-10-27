---
layout: content
project: atomix
menu: user-manual
title: Distributed Resources
pitch: Common abstractions for distributed coordination
first-section: what-are-resources
---

The true power of Atomix comes from [Resource][Resource] implementations. Resources are named distributed objects that are replicated and persisted in the Atomix cluster. Each name can be associated with a single resource, and each resource is backed by a replicated state machine managed by Atomix's underlying [implementation of the Raft consensus protocol][raft-framework].

Resources are created by simply passing a `Resource` class to one of Atomix's `create` methods:

```java
DistributedMap<String, String> map = atomix.create("test-map", DistributedMap.class).get();
```

Atomix uses the provided `Class` to create an associated [StateMachine][state-machines] on each replica. This allows users to create and integrate [custom resources](/atomix/user-manual/custom-resources).

Atomix provides a number of resource implementations for common distributed systems problems. Currently, the provided resources are divided into three subsets that are represented as Maven submodules:

* [Distributed collections](#distributed-collections) - `DistributedSet`, `DistributedMap`, etc
* [Distributed atomic variables](#distributed-atomic-variables) - `DistributedAtomicValue`, etc
* [Distributed coordination tools](#distributed-coordination) - `DistributedLock`, `DistributedLeaderElection`, etc

### Consistency levels

When performing operations on resources, Atomix separates the types of operations into two categories:

* *commands* - operations that alter the state of a resource
* *queries* - operations that query the state of a resource

The [Raft consensus algorithm][raft-framework] on which Atomix is built provides strict linearizability requirements for all commands and queries submitted to the cluster. When a command is submitted to the cluster, the command will always be forwarded to the cluster leader and replicated to a majority of servers before being applied to the resource's state machine and completed.

But real-world systems often must relax reliability and consistency constraints in order to acheive better performance. Thus, Atomix provides simple tools to empower users to modify the behavior of Atomix's consensus algorithm according to their needs. When a resource operation is submitted to the cluster, the operation is handled according to the resource's configurable `Consistency` setting.

To configure the `Consistency` for a resource, use the `with(Consistency)` method:

```java
DistributedLock lock = atomix.create("lock", DistributedLock::new).get();

lock.with(Consistency.ATOMIC).lock().thenRun(() -> System.out.println("Lock acquired!"));
```

Atomix provides four consistency levels for controlling the behavior of read and write operations submitted to the cluster:

* `Consistency.ATOMIC` - Provides guaranteed [linearizability][Linearizability] by sequencing and deduplicating writes submitted to the cluster by each client and sequencing and deduplicating events sent from server-side replicated resource state machines back to the client. This means all state changes and events are guaranteed to occur in the order specified by the client and at some time between the invocation and response of the respective operation.
* `Consistency.SEQUENTIAL` - Provides probable [linearizability][Linearizability] for write operations submitted to the cluster via a leader-lease algorithm and [sequential consistency][SequentialConsistency] for reads and events sent from server-side replicated resource state machines. This means all state changes and events are guaranteed to occur in the order specified by the client, writes will be applied some time between the invocation and response of the respective write operation, and the client will see state progress monotonically (never back in time).
* `Consistency.CAUSAL` - Provides probable [linearizability][Linearizability] for write operations submitted to the cluster via a leader-lease algorithm, [sequential consistency][SequentialConsistency] for events sent from server-side replicated resource state machines, and [causal consistency][CausalConsistency] for reads submitted by a single client. This means non-overlapping state changes and events are guaranteed to occur in the order specified by the client, writes will be applied some time between the invocation and response of the respective write operation, and the client will see state progress monotonically (never back in time).
* `Consistency.NONE` - Provides no linearizability, sequential consistency, or causal consistency guarantees for clients. This means that while Atomix's internal commit log will remain consistent, from the client's perspective state can move arbitrarily forward or backward in time.

Overloaded methods with `ConsistencyLevel` parameters are provided throughout Atomix's resources wherever it makes sense. In many cases, resources dictate the strongest consistency levels - e.g. [coordination] - and so weaker consistency levels are not allowed.

{% include common-links.html %}