---
layout: user-manual
project: atomix
menu: user-manual
title: Replication Protocols
---

Replication protocols are specific distributed systems protocols implemented by Atomix to share state across nodes. Atomix core depends on several different types of protocols for state replication.

## Raft

The [Raft][Raft] protocol is a consensus protocol used in Atomix for strongly consistent, partition tolerant primitives. Atomix provides a mature custom implementation of the Raft protocol for consensus-based primitives. At its core, the Raft protocol manages a persistent replicated log of changes to primitives. This is done by electing a leader and synchronously replicating changes to followers. Consistency is maintained by electing only leaders that have all the most recent changes. However, an important property of the Raft protocol is that it can only make progress when a majority of the cluster is available. In the event of a network partition, only the majority side of the partition will continue to make progress.

## Primary-backup

The primary-backup protocol is a simpler in-memory replication protocol with weaker consistency properties. Unlike with Raft, the Atomix primary-backup protocol can tolerate the loss of all but one node, and changes may be replicated either synchronously or asynchronously to any number of nodes. This makes the primary-backup protocol far better suited to high-performance use cases.

The primary-backup protocol works by electing a primary through which writes are replicated to backups. If the Atomix cluster is configured with a Raft management partition, primary election for all instances of the primary-backup protocol will be done through a Raft replicated state machine for strong consistency. Otherwise, an eventually consistent primary election algorithm will be used.

{% include common-links.html %}
