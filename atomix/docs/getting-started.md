---
layout: docs
project: atomix
menu: docs
title: Getting Started
first-section: Introduction
---

{:.no-margin-top}
## Introduction

Atomix is an easy to use, zero-dependency, embeddable library that provides strong, fault-tolerant consistency for stateful resources in your distributed application. Some of the resources provided by Atomix include:

* Distributed [variables]
* Distributed [collections] such as maps, multi-maps, sets, and queues
* Distributed [group][groups] tools such as group membership, leader election, consistent hashing and more
* Distributed [concurrency] tools such as locks
* Distributed [messaging] tools such as a message bus, topics, and task queues

Atomix also provides a high-level API for creating and managing [custom user-defined resources][custom-resources] where fault-tolerance and consistency is provided automatically with the help of [Copycat](/copycat), a sophisticated implementation of the [Raft consensus algorithm][Raft] which Atomix is built upon.

## Setup

To get started, add the [atomix-all][atomix-all-mvn] Maven artifact to your project:

```xml
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix-all</artifactId>
  <version>{{ site.atomix-version }}</version>
</dependency>
```

This dependency provides you with all of the Atomix resources along with a [Netty] based transport that Atomix nodes can use to communicate with each other.

## Creating a Cluster

The first step with Atomix is to create a cluster. An atomix cluster consists of stateful distributed resources such as maps, queues, and groups, and a set of [replicas] through which resources are created and operated on. Each replica maintains a copy of the state of each resource created in the cluster. State is stored according to a configurable [StorageLevel] and state changes are replicated according to a given [ConsistencyLevel][CommandConsistencyLevel]. 

Clusters can contain both *active* and *passive* replicas. Active replicas take part in the processing of state changes while passive replicas are kept in sync in order to replace active replicas when a fault occurs. Typically, an Atomix cluster consists of 3 or 5 active replicas. While Atomix embeds inside your clustered application, the number of nodes participating in the Atomix cluster does not need to match that of your application, allowing your application to scale independant of Atomix.

{:.callout .callout-info}
For more information on node types see the [cluster documentation][clustering].

To create a cluster, first define the `Address` of the local server along with a list of addressess for all the active members of the cluster:

```
Address address = new Address("123.456.789.0", 5000);

List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);
```

Next, define [Storage] for your resource data. Supported [StorageLevel]s include in memory, disk, and memory mapped:

```java
Storage storage = new Storage(StorageLevel.MEMORY);
```

Finally, define the [Transport] that your replicas will use to communicate with each other. The [NettyTransport] is a fast, reliable Transport implementation:

```java
Transport transport = new NettyTransport();
```

Now we can build a replica:

```java
AtomixReplica replica = AtomixReplica.builder(address, members)
  .withStorage(storage)
  .withTransport(transport)
  .build();
```

We'll start the replica by calling the `open` method which attempts to establish communication with the other members of the cluster.

```java
CompletableFuture<Atomix> future = replica.open();
```

`open()` returns a [CompletableFuture] which we can use to wait for the replica to successfully start:

```java
future.join();
```

{:.callout .callout-info}
All of the Atomix APIs are [fully asynchronous](/atomix/docs/threading-model/#asynchronous-api-usage), allowing users to perform multiple operations concurrently. The [CompletableFuture] API can still be used in a synchronous manner by using the blocking on the `get` or `join` methods, such as above.

To establish a cluster, a replica will need to be opened on each of the member addresses defined above.

## Creating Distributed Resources

With our [AtomixReplica] ready and open, we can create some distributed resources. To get or create a distributed resource, use one of the [Atomix] `get` methods. Let's create and acquire a [DistributedLock]:

{% include sync-tabs.html target1="#async-create" desc1="Async" target2="#sync-create" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-create">
```java
DistributedLock lock = replica.getLock("my-lock").get();
lock.lock().thenRun(() -> System.out.println("Acquired a lock!"));
```
</div>
<div class="tab-pane" id="sync-create">
```java
DistributedLock lock = replica.getLock("my-lock").get();
lock.lock().join();
System.out.println("Acquired a lock!");
```
</div>
</div>

Each resource in the cluster must be assigned a unique `String` name. If multiple [Atomix] instances `get` the same resource type with the same name, they will all reference the same resource stored in the cluster.

## Creating a Client

In addition to creating and acessing resources directly through an [AtomixReplica], Atomix also supports [clients] which can be used to remotely access resources stored in a cluster.

Creating a client is similar to creating a replica:

{% include sync-tabs.html target1="#async-client" desc1="Async" target2="#sync-client" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-client">
```java
List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);

AtomixClient client = AtomixClient.builder(members)
  .withTransport(new NettyTransport())
  .build();

client.open().thenRun(() -> {
  System.out.println("Client started!");
});
```
</div>
<div class="tab-pane" id="sync-client">
```java
List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);

AtomixClient client = AtomixClient.builder(members)
  .withTransport(new NettyTransport())
  .build();

client.open().join();

System.out.println("Client started!");
```
</div>
</div>

With our [AtomixClient] open, we can get or create distributed resources in the same way as with a replica:

```java
DistributedValue<String> value = client.getValue("value").get();
value.set("Hello world!");
```

## Freeing Resources

To discontinue the usage of a resource, call `close()`. The resource's state will still remain in tact and the resource can be re-opened by calling `open()`.

To delete a resource's state permanently, call `delete()`.

{% include common-links.html %}