---
layout: getting-started
project: atomix
title: Getting Started
---

{:.no-margin-top}

## Introduction

## Dependency Management

## Bootstrapping a Cluster

### Using the Java API

Atomix relies heavily upon builder APIs to build high-level objects used to communicate and coordinate distributed systems.

To create a new Atomix instance, create an Atomix builder:

```java
Atomix.Builder builder = Atomix.builder();
```

The builder should be configured with the local node configuration:

```java
builder.withLocalNode(Node.builder("server1")
  .withType(Node.Type.DATA)
  .withAddress("localhost:5000")
  .build());
```

In addition to configuring the local node information, each instance must be configured with a set of _bootstrap nodes_ from which to form a cluster. When first starting a cluster, all instances should provide the same set of bootstrap nodes.

```java
builder.withBootstrapNodes(
  Node.builder("server1")
    .withType(Node.Type.DATA)
    .withAddress("localhost:5000")
    .build(),
  Node.builder("server2")
    .withType(Node.Type.DATA)
    .withAddress("localhost:5001")
    .build(),
  Node.builder("server3")
    .withType(Node.Type.DATA)
    .withAddress("localhost:5002")
    .build());
```

Bootstrap nodes can be either `CORE` or `DATA` nodes. To read more about the difference between the various types of nodes, see the [user manual][node-types]

Finally, the instance must be configured with one or more partition groups. The partition groups define how data is distribtued in the cluster.

```java
builder.addPartitionGroup(PrimaryBackupPartitionGroup.builder("data")
  .withNumPartitions(32)
  .build());
```

Typically, clusters that require strong consistency guarantees are configured with `CORE` nodes and at least one `RaftPartitionGroup`, and clusters designed for performance and scalability with `DATA` nodes use `PrimaryBackupPartitionGroup`s.

```java
Atomix atomix = builder.build();
```

Finally, call `start()` on the instance to start the node:

```java
atomix.start().join();
```

{:.callout .callout-warning}
In order to form a cluster consisting of `CORE` nodes and a Raft partition group, a majority of instances must be started concurrently to allow Raft partitions to form a quorum. The future returned by the `start()` method will not be completed until all partitions are able to form. If your `Atomix` instance is blocking indefinitely at startup, ensure you enable `DEBUG` logging to debug the issue.

### Using the Atomix Agent

## Creating a Java Client

## Creating Distributed Primitives

## Configuring the Cluster

{% include common-links.html %}