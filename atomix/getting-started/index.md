---
layout: content
project: atomix
menu: getting-started
title: Getting Started
pitch: Atomix in two minutes
first-section: getting-started
---

### Installation

Atomix can be found in standard Maven repositories. To add Atomix core - which includes `AtomixClient`, `AtomixServer`, and `AtomixReplica` - add the `atomix` artifact:

```
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix</artifactId>
  <version>{{ site.version  }}</version>
</dependency>
```

Groups of Atomix core distributed resources - i.e. [collections], [atomic variables][atomics], and [coordination tools][coordination] - are each packaged in separate artifacts based on the type of resource. The available resource artifacts are as follows:

* `atomix-collections` provides distributed collections like maps, multimaps, sets, and queues
* `atomix-atomic` provides distributed atomic variables
* `atomix-coordination` provides distributed coordination tools like locks, leader elections, group membership, and messaging

To add Atomix core and all resources, use the `atomix-all` artifact:

```
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix-all</artifactId>
  <version>{{ site.version  }}</version>
</dependency>
```

### Setting up the cluster

Atomix clusters consist of at least one (but usually 3 or 5) [servers][AtomixServer] or [replicas][AtomixReplica] and any number of [clients][AtomixClient]. *Servers* are stateful nodes that actively participate in the [Raft consensus protocol][Raft], and *clients* are stateless nodes that modify system state remotely. When a cluster is started, the servers in the cluster coordinate with one another to elect a leader.

![Atomix cluster](http://s24.postimg.org/3jrc7yuad/IMG_0007.png)

To create an [AtomixServer], first you must define the server's [Address] and a list of addresses through which to communicate with other members of the cluster:

```java
Address address = new Address("123.456.789.0", 5000);

List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);
```

With the membership list, create an `AtomixServer.Builder` to build the server:

```java
AtomixServer.Builder builder = AtomixServer.builder(address, members);
```

Each server can optionally be configured with a [Storage] module and [Transport]. The `Storage` object can be configured with differen `StorageLevel`s, such as `StorageLevel.MEMORY` or `StorageLevel.DISK`, indicating how the server should store state changes. The [NettyTransport] provides a fast, reliable communication layer for the cluster.

```java
builder.withStorage(new Storage(StorageLevel.MEMORY)).withTransport(new NettyTransport());
```

Once the server has been configured, construct the server with the `build` method:

```java
AtomixServer server = builder.build();
```

To open the server, simple call the `open` method:

```java
server.open();
```

All Atomix APIs are fully asynchronous, so users must explicitly block if so desired:

```java
CompletableFuture<AtomixServer> future = server.open();
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

### Embedding servers and clients

Atomix is designed to be used as an embedded framework is the user so chooses. In order to facilitate embedded use, Atomix provides a combined client/server called a *replica*. The replica acts both as a stateful server which communicates and coordinates with other servers and replicas in the cluster and exposes the [Atomix] client API.

[AtomixReplica]s are constructed in exactly the same manner as servers:

{% include sync-tabs.html target1="#async-replica" desc1="Async" target2="#sync-replica" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-replica">
```java
Address address = new Address("123.456.789.0", 5000);

List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);

AtomixReplica replica = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(StorageLevel.DISK))
  .build();

replica.open().thenRun(() -> {
  System.out.println("Replica started!");
});
```
</div>

<div class="tab-pane" id="sync-replica">
```java
Address address = new Address("123.456.789.0", 5000);

List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.1", 5000),
  new Address("123.456.789.2", 5000)
);

AtomixReplica replica = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(StorageLevel.DISK))
  .build();

replica.open().get();

System.out.println("Replica started!");
```
</div>
</div>

### Creating distributed resources

Clients and replicas operate on fault-tolerant, distributed [resources] like maps, sets, locks, leader elections, and more through the [Atomix] API. Atomix exposes an extensible interface that allows users to create and manage arbitrary resources.

To create a resource, use the `create` method:

{% include sync-tabs.html target1="#async-create" desc1="Async" target2="#sync-create" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-create">
```java
client.create("lock", DistributedLock::new).thenAccept(lock -> {
  lock.lock().thenRun(() -> System.out.println("Acquired a lock!"));
});
```
</div>

<div class="tab-pane" id="sync-create">
```java
DistributedLock lock = client.create("lock", DistributedLock::new).get();
```
</div>
</div>

Each resource in the cluster must be assigned a unique `String` name. If multiple clients `create` or `get` the same resource type with the same name, they both reference the same state in the server-side replicated state machine.

Users can also access a singleton instance of any resource using the `get` method:

{% include sync-tabs.html target1="#async-get" desc1="Async" target2="#sync-get" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-get">
```java
client.get("lock", DistributedLock::new).thenAccept(lock -> {
  lock.lock().thenRun(() -> System.out.println("Acquired a lock!"));
});
```
</div>

<div class="tab-pane" id="sync-get">
```java
DistributedLock lock = client.get("lock", DistributedLock::new).get();
```
</div>
</div>

{% include common-links.html %}