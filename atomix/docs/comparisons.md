---
layout: docs
project: atomix
menu: docs
title: Comparisons
first-section: something-unique
---

{:.no-margin-top}
## Something Unique

While Atomix provides a rich set of resources for solving common distributed computing problems, it also enables users to easily build their own distributed resources that are fault tolerant and strongly consistent. This flexibility not only makes Atomix unique, but empowers it to be uniquely matched to various problems and systems.

> But how does it compare to those other projects?

That said, it's helpful to understand what Atomix offers by comparing to other well-known technologies.

## ZooKeeper

Atomix and [ZooKeeper] are both backed by a similar consensus-based persistence/replication layer. But Atomix is a framework that can be embedded instead of depending on an external cluster. Additionally, ZooKeeper's low-level primitives require complex recipes or other tools like [Apache Curator](http://curator.apache.org/), whereas Atomix provides [high-level interfaces](/docs/distributed-resources#resources) for common data structures and coordination tools like [locks](/docs/distributed-resources#distributedlock), [maps](/docs/distributed-resources#distributedmap), and [leader elections](/docs/distributed-resources#distributedleaderelection), along with the ability to create [custom replicated state machines](/docs/distributed-resources#custom-resources).

## Hazelcast

[Hazelcast] is a fast, in-memory data grid that, like Atomix, exposes rich APIs for operating on distributed object. But whereas Hazelcast chooses [availability over consistency in the face of a partition](https://en.wikipedia.org/wiki/CAP_theorem), Atomix is designed to ensure that data is never lost in the event of a network partition or other failure. Like ZooKeeper, this requires that Atomix synchronously replicate all writes to a majority of the cluster and persist writes to disk.

{% include common-links.html %}