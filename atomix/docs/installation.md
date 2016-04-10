---
layout: docs
project: atomix
menu: docs
title: Installation
first-section: embedded-usage
---

{:.no-margin-top}
## Embedded Usage

The most common way of using Atomix is as an embedded library via the Atomix Maven artifacts. There are a few different artifacts to choose from depending on your needs:

#### atomix-all

The simplest way to get up and running with Atomix, which we saw in the [Getting Started][atomix-getting-started] guide, is to use the [atomix-all][atomix-all-mvn] artifact. It [bundles](https://github.com/atomix/atomix/blob/master/all/pom.xml#L29-L38) the core `atomix` dependency with a Netty based [Transport] implementation, `catalyst-netty`.

For most users, `atomix-all` is the only dependency you will need.

#### atomix

If you're planning to use a different [Transport] implementation than the Netty transport, use the `atomix` artifact along with your Transport.

The [atomix][atomix-mvn] artifact provides APIs for creating core resources such as [variables], [collections], [groups] and more via the [AtomixClient] and [AtomixReplica] classes, along with custom, user-defined resources. It [bundles](https://github.com/atomix/atomix/blob/master/core/pom.xml#L20-L49) the `atomix-resource-manager` with the various core resource implementations.

#### atomix-resource-manager

If you do not need some or all of the core atomix resources, use use the `atomix-resource-manager` artifact along with the [Transport] and resource implementations of your choosing.

The [atomix-resource-manager][resource-manager-mvn] Maven artifact provides APIs for creating custom, user-defined resources via the [ResourceClient] class.

### Resources

Groups of Atomix resources can be individually used in conjunction with the `atomix-resource-manager`. The Atomix resource artifacts along with the resources they include are:

{% include modules.md %}

### Transports

Atomix requires a [Transport] implementation in order for clients and servers to communicate with each other. Available transports include:

* `catalyst-netty` - The [catalyst-netty][catalyst-netty-mvn] artifact provides a high-performance Netty based [Transport] implementation which is ideal for most Atomix installations.
* `catalyst-local` - The [catalyst-local][catalyst-local-mvn] artifact provides a [Transport] implementation that can be used for local, in-process communication for testing purposes.

## Standalone Usage

In addition to being embedded, Atomix can run as a standalone server. Currently the standalone server binaries are not hosted, but can be built very quickly.

To build the standalone server, `git clone` and `mvn package` Atomix:

```
git clone https://github.com/atomix/atomix.git
cd atomix
mvn package -DskipTests=true
```

This will create a single binary with a self-contained Atomix server located at:

```
standalone/standalone-server/target/atomix-standalone-server.jar
```

### Bootstrapping a Standalone Cluster

To bootstrap a standalone cluster, pass the `-bootstrap` flag when running the standalone server jar. Bootstrapping the standalone server without any additional arguments will bootstrap a single node cluster to which additional nodes can be added.

```java
java -jar atomix-standalone-server.jar 123.456.789.0:8700 -bootstrap
```

Alternatively, to bootstrap a multi-node cluster, pass a list of server addresses as arguments to the `-bootstrap` option:

```java
java -jar atomix-standalone-server.jar 123.456.789.0:8700 -bootstrap 123.456.789.0:8700 123.456.789.1:8700 123.456.789.2:8700
```

### Adding a Node to a Standalone Cluster

To add a node to an existing bootstrapped standalone cluster, use the `-join` flag when running the standalone server jar, passing a list of servers to which to join the node.

```java
java -jar atomix-standalone-server.jar 123.456.789.1:8700 -join 123.456.789.0:8700
```

### Configuring a standalone server

Replicas support a number of configuration options that are typically configurable via the `AtomixReplica.Builder` API. WHen running a standalone Atomix server, the same properties can be configured by passing a properties file as the `-config` to the server.

```
java -jar atomix-standalone-server.jar 123.456.789.1:8700 -bootstrap -config atomix.properties
```

Following is an example replica properties file:

```
# This is the transport to use to communicate between replicas. The transport must
# be the same class on all replicas.
replica.transport=io.atomix.catalyst.transport.NettyTransport

# These are standard TCP configuration options.
replica.transport.connectTimeout=5000
replica.transport.sendBufferSize=-1
replica.transport.receiveBufferSize=-1
replica.transport.reuseAddress=true
replica.transport.tcpKeepAlive=true
replica.transport.tcpNoDelay=false
replica.transport.acceptBacklog=1024

# This property indicates whether SSL should be enabled for the transport.
replica.transport.ssl.enabled=false

# These properties are Raft-specific configurations that define the intervals at which
# Raft servers and clients communicate with one another. The electionTimeout and heartbeatInterval
# control the frequency of communication between servers. The sessionTimeout controls the
# frequency of keep-alive requests from clients. Note that decreasing the sessionTimeout can
# result in e.g. a lock held by a crashed node being released sooner, but decreasing the sessionTimeout
# also implies more overhead for frequent keep-aive requests.
raft.electionTimeout=1000
raft.heartbeatInterval=500
raft.sessionTimeout=10000

# These properties dictate how Raft logs are stored for this replica. By default, Atomix stores
# logs on disk. Alternatively, the MAPPED and MEMORY storage.level can be used for greater efficiency
# at the potential expense of more memory consumption and loss of safety. In order for writes to be
# lost in a cluster of replicas using storage.level=MEMORY, a majority of the cluster would have
# to crash and lose their logs from memory.
storage.level=DISK
storage.directory=logs
storage.maxSegmentSize=33554432
storage.maxEntriesPerSegment=1048576

# These properties dictate the behavior of log compaction in Atomix. Log compaction includes a
# combination of incremental rewrites of the log and storage of snapshots of the system's state.
# Snapshots inherit the storage.level, so snapshots stored with storage.level=MEMORY will not
# be stored on disk but can be replicated to other servers.
storage.compaction.retainSnapshots=false
storage.compaction.threads=2
storage.compaction.minor=60000
storage.compaction.major=600000
storage.compaction.threshold=0.5

# These properties dictate the behavior of the serializer. Serializable types can be registered
# along with serializable type IDs for more efficient serialization.

# This property indicates whether serializable types must be whitelisted. If types must be whitelisted
# for serialization, serializable types must be registered in the serializer.types.* properties.
# If whitelisting is disabled, unregistered types may be serialized with their class name.
serializer.whitelist=false
serializer.allocator=io.atomix.catalyst.buffer.PooledHeapAllocator

# This is an example of a serializable type and custom serializer.
serializer.types.1=com.mycompany.FooClass
serializer.serializers.1=com.mycompany.FooClassSerializer

# This is an example of a serializable abstract type and a custom abstract type serializer.
serializer.types.2=com.mycompany.AbstractFooClass
serializer.abstractSerializers.2=com.mycompany.AbstractFooClassSerializer

# This is an example of a serialization framework interface and the default framework serializer.
serializer.types.3=com.mycompany.MyCompanySerializable
serializer.defaultSerializers.3=com.mycompany.MyCompanySerializableSerializer
```

{% include common-links.html %}