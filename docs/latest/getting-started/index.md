---
layout: getting-started
project: atomix
title: Getting Started
---

{:.no-margin-top}
## Overview

Atomix 2.1 is a fully featured framework for building fault-tolerant distributed systems. Combining ZooKeeper's consistency with Hazelcast's usability and performance, Atomix uses a set of custom communication APIs, a sharded Raft cluster, and a multi-primary protocol to provide a series of high-level primitives for building distributed systems. These primitives include:
* [Cluster management][cluster-management] and failure detection
* [Cluster communication][cluster-communication] (direct and pub-sub) via Netty
* Strongly consistent reactive [distributed coordination primitives][primitives] (locks, leader elections, etc)
* Efficient partitioned distributed [data structures][primitives] (maps, sets, trees, etc)
* [Standalone Agent][agent]
* [REST API][rest]
* [Interactive CLI][cli]

## Background

Atomix was originally conceived in 2014 along with its sister project [Copycat](http://github.com/atomix/copycat) (deprecated) as a hobby project. Over time, Copycat grew into a mature implementation of the Raft consensus protocol, and both Copycat and Atomix were put into use in various projects. In 2017, development of a new version was begun, and Copycat and Atomix were combined in Atomix 2.x. Additionally, significant extensions to the projects originally developed for use in [ONOS](http://onosproject.org) were migrated into Atomix 2.x. Atomix is now maintained as a core component of ONOS at the [Open Networking Foundation](http://opennetworking.org).

## Dependency Management

Atomix is packaged in a hierarchy of modules that allow users to depend only on those features they intend to use. Almost all users will want to use the Atomix core module, which is identified by the `atomix` artifact ID:

```
<dependencies>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix</artifactId>
    <version>2.1.0-SNAPSHOT</version>
  </dependency>
</dependencies>
```

Additionally, most clusters are configured with a set of partition groups. The partition groups that are used depend on the consistency, fault-tolerance, and persistence requirements of the system. Different use cases may require different dependencies. But packaged with Atomix are two primary protocols:
* `atomix-raft`
* `atomix-primary-backup`

```
<dependencies>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix</artifactId>
    <version>2.1.0-SNAPSHOT</version>
  </dependency>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix-raft</artifactId>
    <version>2.1.0-SNAPSHOT</version>
  </dependency>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix-primary-backup</artifactId>
    <version>2.1.0-SNAPSHOT</version>
  </dependency>
</dependencies>
```

## Bootstrapping a Cluster

The first step to working with Atomix is forming a cluster. Atomix clusters consist of two types of members:
* `PERSISTENT` members exist in the cluster configuration whether available or not
* `EPHEMERAL` members join and leave the cluster based on their availability

To form a cluster, typically a set of nodes need to be bootstrapped. Additionally, if using distributed primitives, one or more [partition groups][partition-groups] must be configured.

### Using the Java API

Users can operate on Atomix clusters using a variety of methods. The most fundamental of these methods is using the Java API, which affords the greatest performance, consistency, and flexibility.

The core Java API in Atomix is the [`Atomix`][Atomix] object. Atomix relies heavily upon the builder pattern to construct high-level objects used to communicate and coordinate distributed systems.

To create a new Atomix instance, create an Atomix builder:

```java
Atomix.Builder builder = Atomix.builder();
```

The builder should be configured with the local node configuration:

```java
builder.withLocalMember(Member.builder("node1")
  .withType(Member.Type.EPHEMERAL)
  .withAddress("localhost:5000")
  .build());
```

In addition to configuring the local node information, each instance must be configured with a set of _bootstrap nodes_ from which to form a cluster. When first starting a cluster, all instances should provide the same set of bootstrap nodes.

```java
builder.withMembers(
  Member.builder("member1")
    .withType(Member.Type.EPHEMERAL)
    .withAddress("localhost:5000")
    .build(),
  Member.builder("member2")
    .withType(Member.Type.EPHEMERAL)
    .withAddress("localhost:5001")
    .build(),
  Member.builder("member3")
    .withType(Member.Type.EPHEMERAL)
    .withAddress("localhost:5002")
    .build());
```

Bootstrap nodes can be either `PERSISTENT` or `EPHEMERAL` nodes. Clusters that require strong consistency must be bootstrapped with a set of `PERSISTENT` nodes capable of participating in consensus. Clusters that have more relaxed persistence/consistency requirements can use `EPHEMERAL` nodes which can scale dynamically.

{:.callout .callout-info}
To read more about the difference between the various types of nodes, see the [user manual][node-types]

Finally, the instance must be configured with one or more partition groups. Common partition groups can be configured using [profiles][profiles].

```java
builder.addProfiles(Profiles.DATA_GRID);
```

Typically, clusters that require strong consistency guarantees are configured with `CORE` nodes and at least one `RaftPartitionGroup`, and clusters designed for performance and scalability with `DATA` nodes use `PrimaryBackupPartitionGroup`s.

```java
Atomix atomix = builder.build();
```

Call `start()` on the instance to start the node:

```java
atomix.start().join();
```

The `start()` method returns a future that will be completed once the node has joined the cluster.

{:.callout .callout-warning}
In order to form a cluster consisting of `CORE` nodes and a Raft partition group, a majority of instances must be started concurrently to allow Raft partitions to form a quorum. The future returned by the `start()` method will not be completed until all partitions are able to form. If your `Atomix` instance is blocking indefinitely at startup, ensure you enable `DEBUG` logging to debug the issue.

### Using the Atomix Agent

As mentioned, there are multiple ways to manage and interact with Atomix clusters. A convenient alternative to the Java API is the [Atomix agent][agent]. An agent is a standalone Atomix node that behaves just like a Java node would but instead exposes a REST API for client interaction. Agents can be useful in configuring Atomix clusters in a client-server architecture or providing polyglot access to Atomix primitives.

To use the Atomix agent, first download and build Atomix with Maven:

```
mvn clean package
```

Once the project has been built, to run the agent, the `$ATOMIX_ROOT` environment variable must be set:

```
export ATOMIX_ROOT=./
```

The agent is run with the `bin/atomix-agent` script:

```
bin/atomix-agent -h
```

Use the `-h` option to see a list of options for the agent script.

When working with the agent, it's most convenient to provide a JSON or YAML configuration file. All builder configurations supported via the Java API are supported in configuration files as well. To configure the agent, create an `atomix.yaml` file and define the cluster:

`atomix.yaml`

```
cluster:
  nodes:
    node1:
      type: ephemeral
      address: localhost:5001
    node2:
      type: ephemeral
      address: localhost:5002
    node3:
      type: ephemeral
      address: localhost:5003
profiles:
  - consensus
  - data-grid
```

{:.callout .callout-info}
The Java API supports configuration files as well. To configure an `Atomix` instance with a configuration file, simply pass the file to the `Atomix` constructor.

Once the configuration file has been created, start the cluster by bootstrapping the configured nodes:

```
bin/atomix-agent node1 -c atomix.yaml
```

```
bin/atomix-agent node2 -c atomix.yaml
```

```
bin/atomix-agent node3 -c atomix.yaml
```

{:.callout .callout-info}
The local node could be specified in the configuration file, but specifying the local instance name in the `atomix-agent` arguments allows the configuration file to be shared across all the instances.

## Creating a Java Client

All Atomix node types expose the same API and are capable of performing all the same functions as their peers. Both stateful and stateless nodes, strongly consistent and eventually consistent nodes can operate on primitives, send and receive messages, and manage the cluster. Thus, Atomix does not necessarily require any client nodes. But Atomix can be configured in a variety of different architectures, and in the client-server architecture where stateful nodes are standalone agents, clients become a necessity.

Client nodes are constructed in the same way as all other nodes except that they don't participate in replication and thus are not members of the cluster membership list. To configure a client node, simply create a `CLIENT` node and point it towards one or more peers:

```java
Atomix atomix = Atomix.builder()
  .withLocalMember(Member.builder("client1")
    .withAddress("localhost:6000")
    .build())
  .withMembers(
    Member.builder("member1")
      .withType(Member.Type.PERSISTENT)
      .withAddress("localhost:5000")
      .build(),
    Member.builder("member2")
      .withType(Member.Type.PERSISTENT)
      .withAddress("localhost:5001")
      .build(),
    Member.builder("member3")
      .withType(Member.Type.PERSISTENT)
      .withAddress("localhost:5002")
      .build());
```

Finally, starting the instance using the `start()` method will cause it to join the cluster:

```java
atomix.start().join();
```

## Creating Distributed Primitives

Bootstrapping the Atomix cluster does not in itself give us a great deal of functionality. The true power of Atomix comes in the form of its primitives. [Primitives][primitives] are high-level distributed objects designed for replicating state and coordinating state changes in a distributed system.

Atomix generally provides two different methods for creating distributed primitives:
* Creating distinct instances using a builder pattern
* Creating multiton instances using a getter

As with other builders, primitive configurations provide the same options as do primitive builders. Builders simply provide a fluent API for configuring primitives programmatically.

To create a distributed primitive via the builder pattern, use one of the `*Builder` methods on the [`Atomix`][Atomix] interface:

```java
ConsistentMap<String, String> map = atomix.consistentMapBuilder("my-map")
  .withCacheEnabled()
  .build();

map.put("foo", "Hello world!");

Versioned<String> value = map.get("foo");

if (map.put("foo", "Hello world again!", value.version())) {
  ...
}
```

All distributed primitives provide both a synchronous and an asynchronous version of the API. By default, getters and builders return a synchronous primitive instance. To retrieve the underlying asynchronous instance of the primitive, use the `async()` method:

```java
AsyncConsistentMap<String, String> asyncMap = map.async();

asyncMap.put("foo", "Hello world!").thenRun(() -> {
  ...
});
```

{% include common-links.html %}