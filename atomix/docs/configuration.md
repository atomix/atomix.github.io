---
layout: docs
project: atomix
menu: docs
title: Configuration
---

{:.no-margin-top}
## Server Configuration

|Name|Default|Description|
|---|---|---|
|server.address||This is the address to which to bind the local server. This address may or may not be present in the cluster.seed list below. If the address is present in the seed list, this node will start as a full member of the cluster. If the address is not present in the seed list, this node will join the cluster defined by the seeds.|
|server.transport|io.atomix.catalyst.transport.NettyTransport|This is the transport to use to communicate between replicas. The transport must be the same class on all replicas.|
|server.transport.connectTimeout|500|(in milliseconds)|
|server.transport.sendBufferSize|||
|server.transport.receiveBufferSize|||
|server.transport.reuseAddress|||
|server.transport.tcpKeepAlive|||
|server.transport.tcpNoDelay|||
|server.transport.acceptBacklog|||
|server.transport.ssl.enabled||This property indicates whether SSL should be enabled for the transport.|

## Cluster Configuration

#### Cluster Seed

This is a list of members of the cluster to which to connect. If the local member is joining a cluster, its address will not be present in the seed list. If the local member is forming a new cluster, its address will be present in the seed list. The first time the cluster is started, n seed nodes should be started where n is the size of the Raft quorum. Example:

```ini
cluster.seed.1=XXX.XXX.XXX.XXX:5749
cluster.seed.2=XXX.XXX.XXX.XXX:5749
cluster.seed.3=XXX.XXX.XXX.XXX:5749
```

#### Additional Cluster Config

|Name|Default|Description|
|---|---|---|
|cluster.quorumHint|-1|This property indicates the desired size of the quorum. The quorum consists of some set of nodes that participate in the Raft consensus algorithm. Writes to the cluster are synchronously replicated to a majority of the members in the quorum. Atomix guarantees that at least cluster.quorumHint replicas will be in the quorum so long as cluster.quorumHint members have joined the cluster. The default value of -1 indicates that the cluster.seed list represents the desired quorum size. This is typically a good default since clusters are normally started with the desired number of nodes as seed nodes.|
|cluster.backupCount|0|This property indicates the desired number of backup replicas for each active member of the quorum. When a quorum member is partitioned or crashes, Atomix will attempt to replace that member with a backup server. The process of replacing nodes can be shortened by replicating to more backup nodes. Members of the quorum replicate to backup nodes asynchronously, so the number of backups does not significantly impact latency.|
|cluster.electionTimeout|500|The frequency of election communiation between servers (in milliseconds).|
|cluster.heartbeatInterval|250|The frequency of heartbeat communiation between servers (in milliseconds).|
|cluster.sessionTimeout|5|The frequency of keep-alive requests from clients. Note that decreasing the sessionTimeout can result in e.g. a lock held by a crashed node being released sooner, but decreasing the sessionTimeout also implies more overhead for frequent keep-aive requests (in seconds).|

## Storage Configuration

|Name|Default|Description|
|---|---|---|
|storage.level|||
|storage.directory|||
|storage.maxSegmentSize|||
|storage.maxEntriesPerSegment|||
|storage.compaction.maxSnapshotSize|||
|storage.compaction.retainSnapshots|||
|storage.compaction.threads|||
|storage.compaction.minor|||
|storage.compaction.major|||
|storage.compaction.threshold|||

## Serialization Configuration

This configuration dictates the behavior of the serializer. Serializable types can be registered along with serializable type IDs for more efficient serialization.

#### Serializer Registration

This is a list of serializer types and serializers to register. Example:

```ini
serializer.types.1=com.mycompany.FooClass
serializer.types.2=com.mycompany.AbstractFooClass

serializer.serializers.1=com.mycompany.FooClassSerializer
serializer.abstractSerializers.2=com.mycompany.AbstractFooClassSerializer

serializer.types.3=com.mycompany.MyCompanySerializable
serializer.defaultSerializers.3=com.mycompany.MyCompanySerializableSerializer
```

#### Additional Serialization Config

|Name|Default|Description|
|---|---|---|
|serializer.whitelist||Indicates whether serializable types must be whitelisted. If types must be whitelisted for serialization, serializable types must be registered in the `serializer.types.*` properties. If whitelisting is disabled, unregistered types may be serialized with their class name.|
|serializer.allocator|||

{% include common-links.html %}