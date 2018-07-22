---
layout: user-manual
project: atomix
menu: user-manual
title: Partition Groups
---

Distributed primitives in Atomix are replicated using the [replication protocols][replication-protocols] outlined in the previous section. To facilitate replication, clusters must configured a set of partition groups within which primitives will be replicated. Partition groups are sets of instances of either the Raft or primary-backup protocol used to replicate specific named primitive instances.

When a cluster is formed, the members of the cluster must define the set of partition groups in which they participate. For example, a node that participates in a primary-backup partition group might be configured as follows:

```hocon
management-group {
  type: primary-backup
  name: system
  partitions: 1
}

partition-groups.data {
  type: primary-backup
  name: data
  partitions: 32
}
```

This configuration specifies a primitive `management-group` in which the member participates as well as an additional primary-backup group used for storing primitives. The `management-group` is used to store primitive metadata and elect primaries in the primary-backup protocol. The `partition-groups` are used to store primitive state.

Remember, nodes only need to be configured with the partition groups in which they participate. Multiple partition groups may exist on different nodes in a cluster, and when a primitive instance is created it can be assigned to be replicated within a specific partition group. This allows different primitives to be replicated on different nodes depending simply on the configuration of the cluster.

The most important property of a partition group configuration is the number of partitions. Each partition is a single instance of the protocol implemented by the partition group, and the more instances of the protocol the more parallelism can be acheived in replication. For example, a Raft partition group with 3 partitions represents three distinct instances of the Raft protocol. A distributed map which is stored in that partition group will be spread across all three partitions. This allows multiple Raft leaders to concurrently replicate changes for the primitive, and it's how Atomix achieves greater scalability than similar systems.

{% include common-links.html %}
