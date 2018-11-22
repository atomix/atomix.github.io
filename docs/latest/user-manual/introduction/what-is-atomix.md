---
layout: user-manual
project: atomix
menu: user-manual
title: What is Atomix?
---

Atomix is a tool for solving common distributed systems problems in a variety of different ways. It is unopinionated about the problems it solves, instead providing primitives with which to solve problems. Some examples of the primitives it provides are:
* Distributed data structures (maps, sets, trees, counters, values, etc)
* Distributed communication (direct, publish-subscribe, etc)
* Distributed coordination (locks, leader elections, semaphores, barriers, etc)
* Group membership

```java
AtomicMap<String, String> map = atomix.<String, String>mapBuilder("my-map")
  .withCacheEnabled()
  .build();
```

Each of these primitives can be replicated using a variety of configurable distributed systems protocols with varying guarantees:
* Multi-Raft - a strongly consistent partitioned consensus algorithm
* Multi-Primary - a consistent partitioned leader-based synchronous/asynchronous replication algorithm
* Anti-entropy - a highly scalable eventually consistent gossip/reconciliation protocol
* CRDT - an eventually strongly consistent gossip-style replication protocol

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build()

Map<String, String> map = atomix.<String, String>mapBuilder("my-map")
  .withProtocol(protocol)
  .withCacheEnabled()
  .build();

map.put("foo", "bar");
```

Primitives are thread-safe, asynchronous, and reactive, relying heavily on event notifications to detect state changes in the system:

```java
LeaderElection<MemberId> election = atomix.getElection("my-election");

election.addListener(event -> {
  Leader leader = event.newLeadership().leader();
  ...
});

election.run(atomix.getMembershipService().getLocalMember().id());
```

And can be accessed in a variety of different ways, including:
* Asynchronous APIs
* Synchronous APIs
* REST API

```java
AsyncAtomicMap<String, String> asyncMap = atomix.getMap("my-map").async();

asyncMap.put("foo", "baz").thenRun(() -> {
  ...
});
```

Similarly, they can be configured either in code or in configuration files:
* Java builders
* HOCON configurations
* JSON configurations

```hocon
primitives.my-map {
  type: map
  protocol {
    type: multi-raft
    group: raft
    readConsistency: linearizable
  }
}
```

This flexibility allows architects to build extremely diverse systems.

### ONOS Use Case

The [ONOS project](http://onosproject.org) for which Atomix is primarily developed is an excellent use case in using the features of Atomix outlined above. At its core, ONOS uses Atomix group membership and messaging for cluster management and communication. Additionally, stores in ONOS rely heavily on Atomix primitives for state replication and coordination. Using Atomix allows ONOS engineers to choose the ideal primitive for the use case of each individual store. For example, some stores may use synchronous primitives for simplicity, while others may use asynchronous (non-blocking) primitives for concurrency. Some stores use Atomix primitives to build higher-level custom replication protocols. The unopinionated nature of Atomix allows engineers to use the best tool for the job, and the ability to encapsulate most of the complexity of distributed systems in Atomix primitives has reduced the barrier to entry for new ONOS contributors.

{% include common-links.html %}
