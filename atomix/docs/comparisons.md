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

That said, it's helpful to understand what Atomix offers by comparing to other well-known technologies.

## ZooKeeper

Atomix and [ZooKeeper] are both backed by a similar consensus-based persistence/replication layer. But Atomix is a framework that can be embedded instead of depending on an external cluster. Additionally, ZooKeeper's low-level primitives require complex recipes or other tools like [Apache Curator][Curator], whereas Atomix provides [high-level interfaces][resources] for common data structures and coordination tools like [locks](/atomix/docs/coordination/#distributedlock), [maps](/atomix/docs/collections/#distributedmap), and [server groups](/atomix/docs/coordination/#distributedgroup), along with the ability to create [custom resources][custom-resources].

## Hazelcast

[Hazelcast] is a fast, in-memory data grid that, like Atomix, exposes rich APIs for operating on distributed object. But whereas Hazelcast chooses [availability over consistency][CAP] in the face of a partition, Atomix is designed to ensure that data is never lost in the event of a network partition or other failure and that data is always consistent across nodes. Like ZooKeeper, this requires that Atomix synchronously replicate all writes to a majority of the cluster and persist writes to disk.

{:.callout .callout-info}
For a further look at how Atomix differs from other technologies, read the overview of [consistency] in Atomix.

{% include common-links.html %}