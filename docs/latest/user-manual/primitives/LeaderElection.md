---
layout: user-manual
project: atomix
menu: user-manual
title: LeaderElection
---

The [`LeaderElection`][LeaderElection] primitive is a utility for electing a single leader among a set of candidates. Leader elections are managed by a replicated state machine which orders and elects candidates and detects failures. The leader election algorithm is fair. When a process runs for leadership, the candidate will be added to a queue, and the top candidate is always the leader. However, candidates can also be reordered by any node, and nodes can be anointed leader or have their leadership revoked.

Leader elections should always be managed by a strongly consistent [replication protocol][primitive-protocols].

## Configuration

The [`LeaderElection`][LeaderElection] can be configured programmatically using the [`LeaderElectionBuilder`][LeaderElectionBuilder]. To create a new election builder, use the `electionBuilder` method, passing the name of the election to construct:

```java
LeaderElectionBuilder electionBuilder = atomix.electionBuilder("my-election");
```

The election can be configured with a `PrimitiveProtocol` to use to replicate changes. Since `LeaderElection` is a consistent primitive, the only protocols supported are:
* [`MultiRaftProtocol`][MultiRaftProtocol]
* [`MultiPrimaryProtocol`][MultiPrimaryProtocol]

Additionally, when using partitioned protocols, the election will be replicated only within a single partition for consistency.

```java
LeaderElection<MemberId> election = atomix.<MemberId>electionBuilder("my-election")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.LINEARIZABLE)
    .build())
  .build();
```

{:.callout .callout-warning}
It's important that distributed leadership elections can tolerate network partitions without split brain, so it is strongly recommended that users configure at least one [Raft partition group][partition-groups] to use for leader elections.

The generic parameter in the election configuration is the candidate type. By default, arbitrary candidate types may be used. However, when non-standard types are used, class names will be serialized with candidate identifiers, and the thread context class loader will be used to load classes from names. To avoid serializing class names, register a election type via `withCandidateType`. Class-based serialization can also be disabled via `withRegistrationRequired()`.

```java
LeaderElection<Foo> election = atomix.<Foo>electionBuilder("my-election")
  .withProtocol(protocol)
  .withCandidateType(Foo.class)
  .build();

Leadership<Foo> leadership = election.run(new Foo("bar"));
```

Leader elections can also be configured in configuration files. To configure a distributed election primitive, use the `election` primitive type:

`atomix.conf`

```hocon
primitives.my-election {
  type: election
  protocol {
    type: multi-raft
    group: raft
    read-consistency: linearizable
  }
}
```

To get an instance of the pre-configured election, use the `getElection` method:

```java
LeaderElection<MemberId> election = atomix.getElection("my-election");
```

The election's protocol and configuration will be loaded from the Atomix configuration files.

## Operation

The [`LeaderElection`][LeaderElection] interface provides methods for joining an election, promoting and demoting candidates, and removing a candidate node from the election.

The first step to electing a leader is joining the election. This is done with the `run` method:

```java
LeaderElection<MemberId> election = atomix.getElection("my-election");

MemberId localMemberId = atomix.getMembershipService().getLocalMember().id();

Leadership<MemberId> leadership = election.run(localMemberId);
```

When a node enters an election, the `LeaderElection` will return a [`Leadership`][Leadership] instance. The `Leadership` object contains the current leader, term and a list of all candidates that exist _after_ the point at which the new node joined. In other words, if the joining node is the first node, then the `Leadership` will always contain the joining node as the leader.

```java
Leader<MemberId> leader = leadership.leader();
MemberId leaderId = leader.id();
long term = leader.term();
```

The [`Leader`][Leader] object contains the current leader's identifier and a `long` term number. The term is a monotonically increasing, globally unique leadership term identifier which can be used as a fencing token.

The current [`Leadership`][Leadership] can also be read via `getLeadership`:

```java
Leadership<MemberId> currentLeadership = election.getLeadership();
```

Once a leader is elected, it can `withdraw` from its position to elect another leader:

```java
Leadership<MemberId> leadership = election.run(memberId);
if (leadership.leader().id().equals(localMemberId)) {
  election.withdraw(localMemberId);
}
```

Candidates can also be `promote`d to the top of the candidates list or `anoint`ed the current leader:

```java
// Promote "foo" to the top of the candidates list
election.promote(atomix.getMembershipService().getMember("foo").id());

// Anoint "bar" the current leader
election.anoint(atomix.getMembershipService().getMember("bar").id());
```

### Event Notifications

[`LeaderElection`][LeaderElection] clients can listen for changes in leadership or candidates by adding a leadership event listener. To add a listener to an election, simply register the listener via `addListener`:

```java
election.addListener(event -> {
  ...
});
```

Atomix guarantees that events will be received in the order in which they occurred inside replicated state machines, and event listeners will be called on an Atomix event thread. Users can optionally provide a custom executor on which to call the event listener:

```java
Executor executor = Executors.newSingleThreadExecutor();
election.addListener(event -> {
  ...
}, executor);
```

{:.callout .callout-warning}
Custom executors can change the ordering of events. It's recommended that single thread executors be used to preserve order. Multi-threaded executors cannot provide the same guarantees as are provided by Atomix event threads or single thread executors.

The event listener will be called with an [`LeadershipEvent`][LeadershipEvent] instance. The event contains both the previous [`Leadership`][Leadership] and the updated [`Leadership`][Leadership]. The previous leadership can be read via `oldLeadership()` and the updated leadership via `newLeadership()`.

```java
Leadership<MemberId> oldLeadership = event.oldLeadership();
Leadership<MemberId> newLeadership = event.newLeadership();
```

The Atomix thread model allows for event listeners to make blocking calls on primitives within event threads. So, in response to a leadership event, an event listener can e.g. evict the elected node:

```java
// Evict the node after it wins an election
election.addListener(event -> {
  Leadership<MemberId> leadership = event.newLeadership();
  if (leadership.leader() != null) {
    election.evict(leadership.leader().id());
  }
});
```

When performing blocking operations (any operation on a synchronous primitive) within an event threads, additional events and futures will be completed on a background thread pool. This means ordering guarantees are inherently relaxed when event threads are blocked.

### Asynchronous Usage

As with all Atomix primitives, an asynchronous analogue of the election API - [`AsyncLeaderElection`][AsyncLeaderElection] - can be retrieved by calling the `async()` method:

```java
MemberId memberId = atomix.getMembershipService().getLocalMember().id();

AsyncLeaderElection<MemberId> asyncElection = election.async();

asyncElection.run(memberId)

asyncElection.incrementAndGet().thenAccept(election -> {
  asyncElection.compareAndSet(election, 1).thenAccept(() -> {
    ...
  });
});
```

The asynchronous API uses [`CompletableFuture`][CompletableFuture]s to notify the client once an operation is complete. The thread model provided by all Atomix protocols guarantees `CompletableFuture` callbacks will always be executed on the same thread unless a thread is blocked by a prior primitive operation. Additionally, `CompletableFuture`s will be completed in program order. In other words, if an operation `A` was performed before operation `B` on the client, the future for operation `A` will always be completed before the future for operation `B`. Similarly, if an event `A` was sent before event `B` in the state machine, all clients will see event `A` arrive before event `B`.

## Cleanup

While an election is in use, Atomix may consume some network, memory, and disk resources to manage the election. To free up those resources, users should call the `close()` method to allow Atomix to garbage collect the instance.

```java
election.close();
```

{% include common-links.html %}
