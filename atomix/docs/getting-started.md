---
layout: content
project: atomix
menu: docs
title: Getting Started
pitch: Atomix in two minutes
first-section: getting-started
---

### Installation

Atomix can be found in standard Maven repositories. To add Atomix core - which includes `AtomixClient` and `AtomixReplica` - add the `atomix` artifact:

```xml
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix</artifactId>
  <version>{{ site.atomix-version }}</version>
</dependency>
```

Groups of Atomix core distributed resources - i.e. [collections], [variables], [messaging] and [coordination tools][coordination] - are each packaged in separate artifacts based on the type of resource. The available resource artifacts are as follows:

* `atomix-collections` provides distributed collections like maps, multimaps, sets, and queues
* `atomix-variables` provides distributed atomic variables
* `atomix-coordination` provides distributed coordination tools like locks, leader elections, and group membership
* `atomix-messaging` provides reliable and unreliable distributed messaging tools

To add Atomix core and all resources, use the `atomix-all` artifact:

```xml
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix-all</artifactId>
  <version>{{ site.atomix-version }}</version>
</dependency>
```

### Setting up the cluster

Atomix can run on a cluster of any size. Atomix clusters consist of a set of core *active* replicas and any number of *passive* replicas. The user defines the desired number of *active* nodes in the cluster, and Atomix dynamically scales the cluster based on the number of nodes. Typically, an Atomix cluster consists of 3 or 5 active nodes and 1 backup per active node. For more information on node types see the [cluster documentation][cluster].

Clusters are formed by creating an [AtomixReplica] instance on each node. When creating a new replica, the replica must be initialized with an `Address` for the local server and list of active members of the cluster.

```java
Address address = new Address("123.456.789.0", 5000);

List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);

AtomixReplica replica = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(StorageLevel.MEMORY))
  .build();
```

Each replica can optionally be configured with a [Storage][storage-jd] module and [Transport]. The `Storage` object can be configured with differen `StorageLevel`s, such as `StorageLevel.MEMORY` or `StorageLevel.DISK`, indicating how the server should store state changes. The [NettyTransport] provides a fast, reliable communication layer for the cluster.

```java
builder.withStorage(new Storage(StorageLevel.MEMORY)).withTransport(new NettyTransport());
```

Once the replica has been configured, construct the replica with the `build` method:

```java
AtomixReplica replica = builder.build();
```

To open the replica, simple call the `open` method:

```java
replica.open();
```

All Atomix APIs are fully asynchronous, so users must explicitly block if so desired:

```java
CompletableFuture<AtomixServer> future = replica.open();
future.join();
```

### Connecting the client

The cluster of servers is responsible for managing state in the distributed system, but not operating on it. To operate on state, users must construct an [AtomixClient]. Clients are constructed using a builder pattern that may now seem familiar:

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

client.open().get();

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

client.open().get();

System.out.println("Client started!");
```
</div>
</div>

### Creating distributed resources

Clients and replicas operate on fault-tolerant, distributed [resources] like maps, sets, locks, leader elections, and more through the [Atomix] API. Atomix exposes an extensible interface that allows users to create and manage arbitrary resources.

To get a distributed resource, use one of the `get*` resource methods:

{% include sync-tabs.html target1="#async-create" desc1="Async" target2="#sync-create" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-create">
```java
replica.getLock("my-lock").thenAccept(lock -> {
  lock.lock().thenRun(() -> System.out.println("Acquired a lock!"));
});
```
</div>

<div class="tab-pane" id="sync-create">
```java
DistributedLock lock = client.getLock("my-lock").get();
lock.lock().join();
System.out.println("Acquired a lock!");
```
</div>
</div>

Each resource in the cluster must be assigned a unique `String` name. If multiple clients `get` the same resource type with the same name, they both reference the same state in the server-side replicated state machine.

{% include common-links.html %}