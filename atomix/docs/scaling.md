---
layout: docs
project: atomix
menu: docs
title: Scaling
---

{:.no-margin-top}
Atomix is designed to scale along with the rest of your system by providing different node types for different roles in the cluster.

## Active Nodes

*Active* nodes participate in the processing of operations, perform leader elections, and maintain complete replicas of all resource state within the cluster. The number of active nodes is effected by the [quorum hint][quorum-hint] specified when constructing an [AtomixReplica]. As nodes come and go from the cluster, Atomix will automatically manage the number of active nodes in the cluster according to the quorum hint.

## Passive Nodes

*Passive* nodes maintain complete replicas of all resource state in the cluster but do not participate in the processing of operations or in leader elections. Replication from active to passive nodes is done asynchronously using a gossip protocol, so as to not effect operation latency. The number of passive nodes is effected by the [backup count][backup-count] specified when constructing an [AtomixReplica]. As nodes come and go from the cluster, Atomix will automatically promote and demote nodes from active to passive as needed.

## Reserve Nodes

*Reserve* nodes are simply additional nodes that are available to takeover as passive or active nodes as needed, but do not participate in the Atomix cluster and do not store any resource data. Any nodes that are joined to the cluster in addition to the required active as passive nodes, as determined by Atomix, will be made reserve. As with active and passive, Atomix will automatically promote and demote nodes from passive to reserve as needed.


{% include common-links.html %}

[quorum-hint]: http://atomix.io/atomix/api/latest/io/atomix/AtomixReplica.Builder.html#withQuorumHint-int-
[backup-count]: http://atomix.io/atomix/api/latest/io/atomix/AtomixReplica.Builder.html#withBackupCount-int-
[cluster-seed]: /atomix/docs/configuration/#cluster-seed-config