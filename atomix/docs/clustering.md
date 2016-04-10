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

## Sizing Your Cluster

Since Atomix requires a majority quorum to process write operations, clusters typically consist of 3 or 5 [active nodes](#active-nodes) which allows a quorum to be reached even if a node failure occurs. Smaller clusters can be used but may lose write availability if a node fails. Larger clusters can also be used, but are usually unnecessary in terms of fault tolerance, and they come at the cost of slower write throughput since the quorum size for processing writes is larger.

{:.callout .callout-info}
The ideal number of replicas should be calculated as `2f + 1` where `f` is the number of failures to tolerate.

The typical size of an Atomix cluster is dependent on your use case. For write-heavy workloads, smaller `3` node clusters can be more efficient since writes only need to be replicated to one additional node. For read-heavy workloads, `5` node clusters can allow sequential reads to be scaled significantly.

<h2 id="bootstrapping-a-cluster-">Bootstrapping a Cluster</h2>

When a new Atomix cluster is created, the first nodes in the cluster must be *bootstrapped* to define the initial members of the cluster. Atomix provides two methods for bootstrapping a cluster. First, a cluster can be formed by bootstrapping a single replica and joining additional replicas to the bootstrapped node.

```java
AtomixReplica replica = AtomixReplica.builder(new Address("123.456.788.0", 8700)).build();
replica.bootstrap().join();
```

Additional replicas are added to the bootstrapped node by `join`ing the initial replica:

```java
AtomixReplica replica2 = AtomixReplica.builder(new Address("123.456.788.1", 8700)).build();
replica2.join(new Address("123.456.789.0", 8700)).join();

AtomixReplica replica3 = AtomixReplica.builder(new Address("123.456.788.2", 8700)).build();
replica3.join(new Address("123.456.789.0", 8700)).join();
```

Alternatively, multiple replicas can be simultaneously bootstrapped to form a complete cluster by specifying the full cluster configuration in the `bootstrap` method:

```java
List<Address> cluster = Arrays.asList(
  new Address("10.0.0.1", 5000),
  new Address("10.0.0.2", 5000),
  new Address("10.0.0.3", 5000)
);
```

```java
AtomixReplica replica1 = AtomixReplica.builder(cluster.get(0)).build();
replica1.bootstrap(cluster).join();
```

```java
AtomixReplica replica2 = AtomixReplica.builder(cluster.get(1)).build();
replica2.bootstrap(cluster).join();
```

```java
AtomixReplica replica3 = AtomixReplica.builder(cluster.get(2)).build();
replica3.bootstrap(cluster).join();
```

## Joining an Existing Cluster

Additional replicas can be added to any existing Atomix cluster via the same method described above. To join a replica to an existing cluster, pass a list of addresses to which to join the replica to the `join` method:

```java
List<Address> cluster = Arrays.asList(
  new Address("10.0.0.1", 5000),
  new Address("10.0.0.2", 5000),
  new Address("10.0.0.3", 5000)
);

AtomixReplica replica4 = AtomixReplica.builder(new Address("123.456.789.3", 8700)).build();
replica4.join(cluster);
```

## Replica Types

Atomix cluster can scale to sizes much larger than the typical Raft cluster. To do so, Atomix provides three types of nodes that serve three unique roles within the cluster. Replica types can be configured either by specifying the [`AtomixReplica.Type`][AtomixReplica.Type] when configurig a replica or via a pluggable [`ClusterManager`][ClusterManager].

### Active Replicas

*Active* replicas participate in the processing of operations, perform leader elections, and maintain complete replicas of all resource state within the cluster. The number of active nodes is effected by the [quorum hint][quorum-hint] specified when constructing an [AtomixReplica]. As nodes come and go from the cluster, Atomix will automatically manage the number of active nodes in the cluster according to the quorum hint.

By default, all replicas are active replicas unless otherwise specified. Active replicas may be used to bootstrap a new cluster or join an existing cluster. To explicitly configure an active replica, use the `AtomixReplica.Type.ACTIVE` constant:

```java
AtomixReplica replica = AtomixReplica.builder(new Address("123.456.789.0", 8700))
  .withType(AtomixReplica.Type.ACTIVE)
  .build();

replica.bootstrap().join();
```

### Passive Replicas

*Passive* nodes maintain complete replicas of all resource state in the cluster but do not participate in the processing of operations or in leader elections. Replication from active to passive nodes is done asynchronously using a gossip protocol, so as to not effect operation latency. The number of passive nodes is effected by the [backup count][backup-count] specified when constructing an [AtomixReplica]. As nodes come and go from the cluster, Atomix will automatically promote and demote nodes from active to passive as needed.

Passive replicas may only be `join`ed to an existing cluster and cannot be used to `bootstrap` a new cluster. To configure a passive replica, use the `AtomixReplica.Type.PASSIVE` constant:

```java
AtomixReplica replica = AtomixReplica.builder(new Address("123.456.789.0", 8700))
  .withType(AtomixReplica.Type.PASSIVE)
  .build();

replica.join(new Address("123.456.789.1", 8700), new Address("123.456.789.1", 8700)).join();
```

### Reserve Replicas

*Reserve* nodes are simply additional nodes that are available to takeover as passive or active nodes as needed, but do not participate in the Atomix cluster and do not store any resource data. Any nodes that are joined to the cluster in addition to the required active as passive nodes, as determined by Atomix, will be made reserve. As with active and passive, Atomix will automatically promote and demote nodes from passive to reserve as needed.

Reserve replicas may only be `join`ed to an existing cluster and cannot be used to `bootstrap` a new cluster. To configure a reserve replica, use the `AtomixReplica.Type.RESERVE` constant:

```java
AtomixReplica replica = AtomixReplica.builder(new Address("123.456.789.0", 8700))
  .withType(AtomixReplica.Type.RESERVE)
  .build();

replica.join(new Address("123.456.789.1", 8700), new Address("123.456.789.1", 8700)).join();
```

## Automatic Cluster Balancing

As has been described above, Atomix clusters support scaling to large sizes through the use of various types of replicas. However, the types defines by the replica builder API are static. In practice, clusters can evolve over time. In order to facilitate evolving clusters, Atomix provides mechanisms to automatically balance the active, passive, and reserve replicas in a cluster via a configurable [`ClusterManager`][ClusterManager].

To implement automatic balancing of the replicas in a cluster, use the `BalancingClusterManager`:

```java
AtomixReplica replica = AtomixReplica.builder(new Address("123.456.789.0", 8700))
  .withClusterManager(BalancingClusterManager.builder()
    .withQuorumHint(3)
    .withBackupCount(1)
    .build())
  .build();
```

The `quorumHint` defines the desired number of `ACTIVE` replicas in the cluster. WHen an `ACTIVE` node crahes or is partitioned, the cluster manager will attempt to replace the `ACTIVE` replica with a `PASSIVE` or `RESERVE` replica. The `backupCount` defines the number of `PASSIVE` replicas per non-leader `ACTIVE` replica. In other words, if the `quorumHint` is `3` and the `backupCount` is `1`, the cluster manager will attempt to maintain `3` `ACTIVE` replicas and `2` `PASSIVE` replicas at all times.

## Persistent Cluster Configurations

It's important to note that while Atomix provides methods for bootstrapping and joining clusters or promoting and demoting replicas, once a cluster has been initialized, cluster configurations are typically persisted on disk via the replica's configured [`Storage`][Storage] object. This means after the first time a replica `join`s a cluster, in the event the replica crashes and is restarted, calling the `join` method again will have no effect since the replica is already a member of the cluster. This means users don't have to concern themselves with whether a replica has already joined a cluster. If a replica is being added to an existing cluster, simply always start the replica with the `join` method.

{% include common-links.html %}

[quorum-hint]: http://atomix.io/atomix/api/latest/io/atomix/AtomixReplica.Builder.html#withQuorumHint-int-
[backup-count]: http://atomix.io/atomix/api/latest/io/atomix/AtomixReplica.Builder.html#withBackupCount-int-
[cluster-seed]: /atomix/docs/configuration/#cluster-seed-config
[dmap-put]: http://atomix.io/atomix/api/latest/io/atomix/collections/DistributedMap.html#put-K-V-
[dmap-get]: http://atomix.io/atomix/api/latest/io/atomix/collections/DistributedMap.html#get-java.lang.Object-