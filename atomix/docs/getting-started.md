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
* Distributed [groups] tools such as group membership, leader election, messaging and more
* Distributed [concurrency] tools such as locks

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

## Bootstrapping a new Cluster

The first step with Atomix is to bootstrap a cluster. An atomix cluster consists of stateful distributed resources such as maps, queues, and groups, and a set of [replicas] through which resources are created and operated on. Each replica maintains a copy of the state of each resource created in the cluster. State is stored according to a configurable [`StorageLevel`][StorageLevel] and state changes are replicated according to a given [`ConsistencyLevel`][CommandConsistencyLevel].

Clusters can contain both *active* and *passive* replicas. Active replicas take part in the processing of state changes while passive replicas are kept in sync in order to replace active replicas when a fault occurs. Typically, an Atomix cluster consists of 3 or 5 active replicas. While Atomix embeds inside your clustered application, the number of nodes participating in the Atomix cluster does not need to match that of your application, allowing your application to scale independant of Atomix.

{:.callout .callout-info}
For more information on node types see the [clustering documentation][node-types].

[`AtomixReplica`][AtomixReplica]s are created using a builder pattern. To create a new replica, create a replica [`Builder`][AtomixReplica.Builder] via the `AtomixReplica.builder()` static factory method, passing the replica address to the builder factory:

```java
AtomixReplica.Builder builder = AtomixReplica.builder(new Address("localhost", 8700));
```

The builder can be configured with a number of properties that define how the replica stores state and communicates with other replicas in the cluster. The most critical of these configurations are the [`Storage`][Storage] and [`Transport`][Transport].

```java
AtomixReplica replica = AtomixReplica.builder(new Address("localhost", 8700))
  .withStorage(storage)
  .withTransport(transport)
  .build();
```

Once we've constructed a replica, we can bootstrap a single node cluster by simply calling the `bootstrap()` method:

```java
CompletableFuture<Atomix> future = replica.bootstrap();
```

The [`bootstrap`][AtomixReplica.bootstrap] method returns a [`CompletableFuture`][CompletableFuture] that can be used to block until the replica is bootstrapped or call a completion callback once complete.

```java
future.join();
```

{:.callout .callout-info}
All of the Atomix APIs are [fully asynchronous](/atomix/docs/threading-model/#asynchronous-api-usage), allowing users to perform multiple operations concurrently. The [CompletableFuture] API can still be used in a synchronous manner by using the blocking on the `get` or `join` methods, such as above.

## Joining an existing cluster

Once a single replica has been bootstrapped, additional replicas can be added to the cluster via the [`join`][AtomixReplica.join] method:

```java
AtomixReplica replica2 = AtomixReplica.builder(new Address("localhost", 8701))
  .withStorage(storage)
  .withTransport(transport)
  .build();

replica2.join(new Address("localhost", 8700)).join();

AtomixReplica replica3 = AtomixReplica.builder(new Address("localhost", 8701))
  .withStorage(storage)
  .withTransport(transport)
  .build();

replica2.join(new Address("localhost", 8700), new Address("localhost", 8701)).join();
```

{:.callout .callout-info}
Multiple replicas can [`bootstrap`][AtomixReplica.bootstrap] a full cluster by providing the complete bootstrap cluster configuration to the [`bootstrap`][AtomixReplica.bootstrap] method. See the [clustering][clustering] documentation for more info.

## Creating Distributed Resources

With our [`AtomixReplica`][AtomixReplica] cluster bootstrapped, we can create some distributed resources. To get or create a distributed resource, use one of the [`Atomix`][Atomix] `get*` methods. Let's create and acquire a [`DistributedLock`][DistributedLock]:

{% include sync-tabs.html target1="#async-create" desc1="Async" target2="#sync-create" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-create">
```java
DistributedLock lock = replica.getLock("my-lock").join();
lock.lock().thenRun(() -> System.out.println("Acquired a lock!"));
```
</div>
<div class="tab-pane" id="sync-create">
```java
DistributedLock lock = replica.getLock("my-lock").join();
lock.lock().join();
System.out.println("Acquired a lock!");
```
</div>
</div>

Each resource in the cluster must be assigned a unique `String` name. If multiple [`Atomix`][Atomix] instances `get` the same resource type with the same name, they will all reference the same resource stored in the cluster.

## Creating a Client

In addition to creating and acessing resources directly through an [`AtomixReplica`][AtomixReplica], Atomix also supports [clients] which can be used to remotely access and operate on resources stored in a cluster. The [`AtomixClient`][AtomixClient] API is very similar to [`AtomixReplica`][AtomixReplica], but contains no storage since clients are stateless.

Creating a client is similar to creating a replica:

```java
AtomixClient client = AtomixClient.builder()
  .withTransport(new NettyTransport())
  .build();
```

The provided [`Address`][Address] list does not have to be representative of the full list of active replicas. Users must simply provide enough [`Address`][Address]es to be able to successfully connect to at least one replica.

Once the client is created, call [`connect`][AtomixClient.connect] to establish a connection to the cluster:

{% include sync-tabs.html target1="#async-client" desc1="Async" target2="#sync-client" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-client">
```java
List<Address> cluster = Arrays.asList(
  new Address("123.456.789.0", 8700),
  new Address("123.456.789.1", 8700),
  new Address("123.456.789.2", 8700)
);

client.connect(cluster).thenRun(() -> {
  System.out.println("Client connected!");
});
```
</div>
<div class="tab-pane" id="sync-client">
```java
List<Address> cluster = Arrays.asList(
  new Address("123.456.789.0", 8700),
  new Address("123.456.789.1", 8700),
  new Address("123.456.789.2", 8700)
);

client.connect(cluster).join();

System.out.println("Client connected!");
```
</div>
</div>

Once [`connect`][AtomixClient.connect] is complete, we can get or create distributed resources in the same way as with a replica:

```java
DistributedValue<String> value = client.getValue("value").join();
value.set("Hello world!");
```

{% include common-links.html %}