---
layout: docs
project: atomix
menu: docs
title: Configuration
---

{:.no-margin-top}
Atomix supports various configuration that can be specified via the builder APIs when creating a replica, client or server programmatically for [embedded usage][atomix-embedded], or via a properties file which is useful for configuration management and for [standalone usage][atomix-standalone].

## Server Configuration

Aside from `server.address`, server configuration is generally the same across all replicas and servers.

|Name|Default|Description|
|---|---|---|
|server.address||This is the address on which to bind the local server. This address may or may not be present in the `cluster.seed` list below. If the address is present in the seed list, this node will start as a full member of the cluster. If the address is not present in the seed list, this node will join the cluster defined by the seeds.|
|server.transport|io.atomix.catalyst.transport.NettyTransport|This is the transport to use to communicate between replicas. The transport must be the same class on all replicas.|
|server.transport.connectTimeout|5 seconds|The connect timeout.|
|server.transport.sendBufferSize|-1|The TCP send buffer size in bytes.|
|server.transport.receiveBufferSize|-1|The TCP receive buffer size in bytes.|
|server.transport.reuseAddress|true|The SO_REUSEADDR option.|
|server.transport.tcpKeepAlive|true|The SO_KEEPALIVE option.|
|server.transport.tcpNoDelay|false|The TCP_NODELAY option.|
|server.transport.acceptBacklog|1024|The TCP accept backlog.|
|server.transport.ssl.enabled|false|Whether SSL should be enabled.|

## Cluster Configuration

Cluster configuration is generally the same across all members of the cluster.

#### Cluster Seed Config

This is the list of nodes that are used to form an initial cluster. Example:

```properties
cluster.seed.1 = XXX.XXX.XXX.XXX:5749
cluster.seed.2 = XXX.XXX.XXX.XXX:5749
cluster.seed.3 = XXX.XXX.XXX.XXX:5749
```

When adding a node to an existing cluster, the seed nodes will be used as contact points to join the new node to the cluster.

#### Additional Cluster Config

|Name|Default|Description|
|---|---|---|
|cluster.quorumHint|-1|This property indicates the desired size of the quorum. The quorum consists of some set of nodes that participate in the Raft consensus algorithm. Writes to the cluster are synchronously replicated to a majority of the members in the quorum. Atomix guarantees that at least cluster.quorumHint replicas will be in the quorum so long as cluster.quorumHint members have joined the cluster. The default value of -1 indicates that the cluster.seed list represents the desired quorum size. This is typically a good default since clusters are normally started with the desired number of nodes as seed nodes.|
|cluster.backupCount|0|This property indicates the desired number of backup replicas for each active member of the quorum. When a quorum member is partitioned or crashes, Atomix will attempt to replace that member with a backup server. The process of replacing nodes can be shortened by replicating to more backup nodes. Members of the quorum replicate to backup nodes asynchronously, so the number of backups does not significantly impact latency.|
|cluster.electionTimeout|500 ms|The frequency of election communiation between servers.|
|cluster.heartbeatInterval|250 ms|The frequency of heartbeat communiation between servers.|
|cluster.sessionTimeout|5 seconds|The frequency of keep-alive requests from clients. Note that decreasing the sessionTimeout can result in e.g. a lock held by a crashed node being released sooner, but decreasing the sessionTimeout also implies more overhead for frequent keep-aive requests. The leader's configuration at the time a session is registered will be used for this setting, across all members of the cluster.|

## Storage Configuration

|Name|Default|Description|
|---|---|---|
|storage.level|DISK|The type of storage to use. MEMORY, MAPPED or DISK.|
|storage.directory|The system `user.dir`|The directory to store data in.|
|storage.maxSegmentSize|1024 * 1024 * 32|The max log segment size.|
|storage.maxEntriesPerSegment|1024 * 1024|The maximum number of entries per segment.|
|storage.compaction.maxSnapshotSize|1024 * 1024 * 32|The maximum size of snapshot files on disk, in bytes.|
|storage.compaction.retainSnapshots|false|Whether to retain stale snapshots on disk.|
|storage.compaction.threads|# processors / 2|The number of background threads to use for compaction.|
|storage.compaction.minor|1 minute|The minor compaction interval.|
|storage.compaction.major|1 hour|The major compaction interval.|
|storage.compaction.threshold|.5|The percentage of entries in the segment that must be released before a segment can be compacted.|

## Serialization Configuration

This configuration dictates the behavior of the serializer. When building [custom resources][custom-resources], serializable types can be registered along with serializable type IDs for more efficient serialization.

#### Serializer Registration

This is a list of serializer types and serializers to register. Example:

```properties
serializer.types.1 = com.mycompany.FooClass
serializer.types.2 = com.mycompany.AbstractFooClass

serializer.serializers.1 = com.mycompany.FooClassSerializer
serializer.abstractSerializers.2 = com.mycompany.AbstractFooClassSerializer

serializer.types.3=com.mycompany.MyCompanySerializable
serializer.defaultSerializers.3 = com.mycompany.MyCompanySerializableSerializer
```

#### Additional Serialization Config

|Name|Default|Description|
|---|---|---|
|serializer.whitelist|true|Indicates whether serializable types must be whitelisted. If types must be whitelisted for serialization, serializable types must be registered in the `serializer.types.*` properties. If whitelisting is disabled, unregistered types may be serialized with their class name.|
|serializer.allocator|io.atomix.catalyst.buffer.UnpooledHeapAllocator||

{% include common-links.html %}