---
layout: user-manual
project: atomix
menu: user-manual
title: Cluster Configuration
---

The [`Atomix`][Atomix] class extends [`AtomixCluster`][AtomixCluster] which provides a standalone API for group membership and cluster communication. This documentation will describe how to bootstrap an `AtomixCluster`, but these methods are the same for both `AtomixCluster` and `Atomix` instances.

## Members

When configuring an Atomix cluster, a local [`Member`][Member] must be provided. The `Member` object represents the location information for the node joining the cluster. Members support the following attributes:
* `memberId()` - the globally unique `MemberId` of the member
* `address()` - the TCP [`Address`][Address] through which other members can communicate with the node
* `zone()` - an optional `String` zone which can be used when constructing [member groups][member-groups]
* `rack()` - an optional `String` rack which can be used when constructing [member groups][member-groups]
* `host()` - an optional `String` host which can be used when constructing [member groups][member-groups]

Members are constructed using the builder pattern. To configure an `AtomixCluster` or `Atomix` instance with the local member, use the respective builder's `with*` methods:

```java
AtomixBuilder builder = Atomix.builder()
  .withMemberId("member1")
  .withAddress("localhost:5000");
```

## Bootstrapping the cluster

To bootstrap an Atomix cluster, configure the [`Atomix`][Atomix] instance with a [discovery][member-discovery] configuration and call the `start()` the `AtomixCluster` or `Atomix` instance:

```java
Atomix atomix = Atomix.builder()
  .withMemberId("member1")
  .withAddress("localhost:5000")
  .withMulticastEnabled()
  .build();

atomix.start().join();
```

The `start()` method will return a `CompletableFuture` that will be completed once the cluster has been formed.

{:.callout .callout-warning}
Depending on the configuration of an `Atomix` instance, a quorum may be required to complete bootstrapping a new cluster. For example, if the instance is configured with a Raft [partition group][partition-groups], a majority of the group's members must be `start`ed for any single member to complete startup.

## File-based Configuration

As with all other components of Atomix, clusters support file-based configurations via JSON or YAML. The configuration file format mimics that of the builder API:

`atomix.conf`

```hocon
cluster {
  member-id: member4
  address: "localhost:5004"
  discovery {
    type: bootstrap
    nodes.1 {
      id: member1
      address: "localhost:5001"
    }
    nodes.2 {
      id: member2
      address: "localhost:5002"
    }
    nodes.3 {
      id: member3
      address: "localhost:5003"
    }
  }
}
```

The configuration file can be used to configure the Atomix [agent][agent] or can be loaded transparently by a new `AtomixCluster` instance:

```java
Atomix atomix = new Atomix();
```

{:.callout .callout-info}
When constructing an `Atomix` instance from a configuration file, the cluster configuration should be namespaced under the `cluster` field.

Additionally, builders can be initialized using the cluster configuration. This can be convenient for initializing a builder with a shared configuration:

```java
Atomix atomix = Atomix.builder()
  .withAddress("localhost:5004")
  .build();
```

{% include common-links.html %}
