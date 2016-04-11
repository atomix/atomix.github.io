---
layout: docs
project: atomix
menu: docs
title: Configuration
---

{:.no-margin-top}
Atomix supports various configuration that can be specified via the builder APIs when creating a replica, client or server programmatically for [embedded usage][atomix-embedded], or via a properties file which is useful for configuration management and for [standalone usage][atomix-standalone].

## Raft Configuration

The Raft configuration provides options for configuring timeouts within the Raft consensus algorithm.

|Name|Default|Description|
|---|---|---|
|raft.electionTimeout|500ms|The period after which a follower that has not received a heartbeat from a leader will timeout and start a new election, potentially forcing an existing leader to step down. This should always be greater than the heartbeat interval.|
|raft.heartbeatInterval|250ms|The interval at which Raft leaders send heartbeats to followers. This must be less than the election timeout.|
|raft.sessionTimeout|5s|The period after which the cluster should expire a client's session after not receiving a keep-alive from the client. Lengthening the session timeout will reduce the risk of sessions being improperly expired, resulting in lost consistency guarantees.|

## Transport Configuration

|Name|Default|Description|
|---|---|---|
|server.transport|io.atomix.catalyst.transport.NettyTransport|This is the transport to use to communicate between replicas. The transport must be the same class on all replicas.|
|server.transport.connectTimeout|5s|The connect timeout.|
|server.transport.sendBufferSize|-1|The TCP send buffer size in bytes.|
|server.transport.receiveBufferSize|-1|The TCP receive buffer size in bytes.|
|server.transport.reuseAddress|true|The SO_REUSEADDR option.|
|server.transport.tcpKeepAlive|true|The SO_KEEPALIVE option.|
|server.transport.tcpNoDelay|false|The TCP_NODELAY option.|
|server.transport.acceptBacklog|1024|The TCP accept backlog.|
|server.transport.ssl.enabled|false|Whether SSL should be enabled.|

## Storage Configuration

|Name|Default|Description|
|---|---|---|
|storage.level|DISK|The type of storage to use. MEMORY, MAPPED or DISK. MEMORY storage stores log entries in binary form on the Java heap. MAPPED storage stores log entries in on disk with the most recent (uncompacted) segments mapped into memory. DISK storage stores all log entries in `RandomAccessFile`s on disk. All storage levels require some memory usage for in-memory indexes.|
|storage.directory|The system `user.dir`|The directory to which to write commit logs, snapshots, and server configurations. This directory must be unique to the server.|
|storage.maxSegmentSize|1024 * 1024 * 32|The maximum allowed size for a log segment in bytes. Logs are broken into segments where each segment is a file on disk. When a segment file reaches the configured capacity, the log will roll over a new segment file and compact existing segments. Reducing the segment size can allow for more granular and more frequent compaction but requires more file descriptors to be open.|
|storage.maxEntriesPerSegment|1024 * 1024|The maximum number of entries per segment file. When a segment reaches the maximum configured number of entries, the log will roll over to a new segment and compact existing segments. Reducing the number of entries per segment can result in more frequent log compaction.|
|storage.compaction.retainSnapshots|false|Whether to retain stale snapshots on disk. If this property is true, snapshot files that no longer contribute to the state of the system will not be deleted from disk.|
|storage.compaction.threads|# processors / 2|The number of background threads to use for compaction. Increasing the number of compaction threads will allow more segments to be compacted concurrently. However, in practice it's rare for multiple segments to be compacted concurrently because of intelligent selection of segments for compaction.|
|storage.compaction.minor|1m|The interval at which the log compactor will evaluate segments of the log for minor compaction. Note that this does not necessarily indicate that the log will be compacted at the given interval.|
|storage.compaction.major|1h|The interval at which the log compactor will evaluate segments of the log for major compaction. Note that this does not necessarily indicate that the log will be compacted at the given interval. However, major compaction is an expensive process that involves rewriting the majority of the Raft log. Servers should limit the frequency of major compaction as much as possible to ensure consistent performance.|
|storage.compaction.threshold|.5|The percentage of entries in the segment that must be released before a segment can be compacted.|

## Serialization Configuration

This configuration dictates the behavior of the serializer. When building [custom resources][custom-resources], serializable types can be registered along with serializable type IDs for more efficient serialization.

|Name|Default|Description|
|---|---|---|
|serializer.whitelist|false|Indicates whether serializable types must be whitelisted. If types must be whitelisted for serialization, serializable types must be registered in the `serializer.types.*` properties. If whitelisting is disabled, unregistered types may be serialized with their class name.|
|serializer.allocator|io.atomix.catalyst.buffer.UnpooledHeapAllocator|The `BufferAllocator` to use for buffer allocation during serialization when no buffer is provided. Note that typically this property will not have a significant impact on performance since Copycat and Atomix usually provide buffers for serialization.|

#### Serializer Registration

|Name|Default|Description|
|---|---|---|
|serializer.types.{id}||The name of a class to register with the given numeric serializable type ID.|
|serializer.serializers.{id}||The name of a class to register as a serializer for the type defined by the given numeric serializable type ID.|
|serializer.abstractSerializers.{id}||The name of a class to register as an abstract serializer for the type defines by the given numeric serializable type ID.|
|serializer.defaultSerializers.{id}||The name of a class to register as a default serializer.|

Example:

```
serializer.types.1 = com.mycompany.FooClass
serializer.types.2 = com.mycompany.AbstractFooClass

serializer.serializers.1 = com.mycompany.FooClassSerializer
serializer.abstractSerializers.2 = com.mycompany.AbstractFooClassSerializer

serializer.types.3=com.mycompany.MyCompanySerializable
serializer.defaultSerializers.3 = com.mycompany.MyCompanySerializableSerializer
```

## Custom Resources

Custom resources can be added to a replica configuration via the `resource.*` property.

|Name|Default|Description|
|resource.{id}||The fully qualified class name for a custom resource.|

Example:

```
resource.lock = io.atomix.concurrent.DistributedLock
resource.map = io.atomix.collections.DistributedMap
resource.group = io.atomix.group.DistributedGroup
```

{% include common-links.html %}