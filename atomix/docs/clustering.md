---
layout: docs
project: atomix
menu: docs
title: Clustering
---

{:.no-margin-top}
As we saw in the [Getting Started][atomix-getting-started] guide, Atomix clusters consist of one or more [replicas] and any number of [clients]. *Replicas* manage the state of distributed resources in the cluster while *clients* allow resources to be created remotely.

## Anatomy of a Cluster

When a cluster is started, the replicas in the cluster coordinate with one another to elect a *leader* while the remaining replicas become *followers*. 

![Atomix cluster](/assets/img/docs/cluster.png)

While the leader is not publicly distinguished, it carries the important responsibility of processing all write operations for the resources in the cluster. Write operations, such as [`DistributedMap.put`][dmap-put], will be proxied to the leader from clients and other replicas while read operations, such as [`DistributedMap.get`][dmap-get], may be processed by a *follower* according to the configured [consistency level][consistency-levels]. Each write operation is replicated by the leader to the rest of the cluster and must be successfully stored on a majority of nodes before it is committed.

As nodes come and go from the cluster, new leaders are automatically elected as needed to carry on the responsibility of processing write operations.

## Cluster Sizing

Since Atomix requires a majority quorum to process write operations, clusters typically consist of 3 or 5 [active nodes](#active-nodes) which allows a quorum to be reached even if a node failure occurs. Smaller clusters can be used but may lose write availability if a node fails. Larger clusters can also be used, but are usually unnecessary in terms of fault tolerance, and they come at the cost of slower write throughput since the quorum size for processing writes is larger.

{:.callout .callout-info}
The ideal number of replicas should be calculated as `2f + 1` where `f` is the number of failures to tolerate.

<h2 id="creating-a-cluster-">Creating a Cluster</h2>

An Atomix cluster is created by starting one replica for each member of the cluster. Each replica must specify the local address to listen on along with the list of cluster member addresses. One replica is typically started in each process or machine that Atomix is deployed on:

```java
List<Address> cluster = Arrays.asList(
  new Address("10.0.0.1", 5000),
  new Address("10.0.0.2", 5000),
  new Address("10.0.0.3", 5000)
);
```

```java
AtomixReplica replica1 = AtomixReplica.builder(cluster.get(0), cluster)
  ...
  .build();
replica1.start();
```

```java
AtomixReplica replica2 = AtomixReplica.builder(cluster.get(1), cluster)
  ...
  .build();
replica2.start();
```

```java
AtomixReplica replica3 = AtomixReplica.builder(cluster.get(2), cluster)
  ...
  .build();
replica3.start();
```

## Joining an Existing Cluster

Additional Atomix replicas can be joined to an existing cluster by simply pointing at any of the existing cluster members:

```java
AtomixReplica replica4 = AtomixReplica.builder(new Address("10.0.0.4", 5000), existingCluster)
  ...
  .build();
replica4.start();
```

## Node Types

In an embedded installation, the size of an Atomix cluster may not necessarily match the size of your application's cluster. Atomix handles this by allowing any number of replicas to be added to a cluster without impacting the performance of the cluster. This is achieved by automatically dividing the replicas into active, passive and reserve nodes, based on the provided [configuration].

### Active Nodes

*Active* nodes participate in the processing of operations, perform leader elections, and maintain complete replicas of all resource state within the cluster. The number of active nodes is effected by the [quorum hint][quorum-hint] specified when constructing an [AtomixReplica]. As nodes come and go from the cluster, Atomix will automatically manage the number of active nodes in the cluster according to the quorum hint.

### Passive Nodes

*Passive* nodes maintain complete replicas of all resource state in the cluster but do not participate in the processing of operations or in leader elections. Replication from active to passive nodes is done asynchronously using a gossip protocol, so as to not effect operation latency. The number of passive nodes is effected by the [backup count][backup-count] specified when constructing an [AtomixReplica]. As nodes come and go from the cluster, Atomix will automatically promote and demote nodes from active to passive as needed.

### Reserve Nodes

*Reserve* nodes are simply additional nodes that are available to takeover as passive or active nodes as needed, but do not participate in the Atomix cluster and do not store any resource data. Any nodes that are joined to the cluster in addition to the required active as passive nodes, as determined by Atomix, will be made reserve. As with active and passive, Atomix will automatically promote and demote nodes from passive to reserve as needed.

{% include common-links.html %}

[quorum-hint]: http://atomix.io/atomix/api/latest/io/atomix/AtomixReplica.Builder.html#withQuorumHint-int-
[backup-count]: http://atomix.io/atomix/api/latest/io/atomix/AtomixReplica.Builder.html#withBackupCount-int-
[cluster-seed]: /atomix/docs/configuration/#cluster-seed-config
[dmap-put]: http://atomix.io/atomix/api/latest/io/atomix/collections/DistributedMap.html#put-K-V-
[dmap-get]: http://atomix.io/atomix/api/latest/io/atomix/collections/DistributedMap.html#get-java.lang.Object-