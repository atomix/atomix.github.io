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
* `type()` - the [`Member.Type`][MemberType] of the member, either `EPHEMERAL` or `PERSISTENT`
* `address()` - the TCP [`Address`][Address] through which other members can communicate with the node
* `zone()` - an optional `String` zone which can be used when constructing [member groups][member-groups]
* `rack()` - an optional `String` rack which can be used when constructing [member groups][member-groups]
* `host()` - an optional `String` host which can be used when constructing [member groups][member-groups]

Members are constructed using the builder pattern:

```java
Member localMember = Member.builder("member1")
  .withType(Member.Type.EPHEMERAL)
  .withAddress("localhost:5000")
  .build();
```

For simple members that use the default `0.0.0.0` address, members can also be constructed via static helper methods:

```java
Member localMember = Member.persistent("member1");
```

To configure an `AtomixCluster` or `Atomix` instance with the local member, use the respective builder's `withLocalMember` method:

```java
Atomix.Builder builder = Atomix.builder();
builder.withLocalMember(Member.builder("member1")
  .withType(Member.Type.PERSISTENT)
  .withAddress("localhost:5001")
  .build());
```

In addition to configuring the local member, additional existing cluster members may be provided depending on whether a cluster is being [bootstrapped](#bootstrapping-a-new-cluster) or [joined](#joining-an-existing-cluster):

```java
builder.withMembers(
    Member.builder("member1")
      .withType(Member.Type.PERSISTENT)
      .withAddress("localhost:5001")
      .build(),
    Member.builder("member2")
      .withType(Member.Type.PERSISTENT)
      .withAddress("localhost:5002")
      .build(),
    Member.builder("member3")
      .withType(Member.Type.PERSISTENT)
      .withAddress("localhost:5003")
      .build());
```

### Member types

The sections above introduce a [`Member.Type`][MemberType] enum. Member types define how the Atomix cluster interprets member state changes. The two types of members are:
* `PERSISTENT` - always exist in the cluster configuration even when unreachable
* `EPHEMERAL` - exist in the cluster configuration as long as reachable

Different types of Atomix clusters may require different configurations with respect to member types. For example, Raft-based clusters require a set of `PERSISTENT` members on which to store Raft partitions, while primary-backup partition groups can be efficiently rebalanced as `EPHEMERAL` members come and go. See [partition groups][partition-groups] for more information.

## Bootstrapping a new cluster

To bootstrap an Atomix cluster, simply build and `start()` the `AtomixCluster` or `Atomix` instance:

```java
Atomix atomix = builder.build();

atomix.start().join();
```

The `start()` method will return a `CompletableFuture` that will be completed once the cluster has been formed.

{:.callout .callout-warning}
Depending on the configuration of an `Atomix` instance, a quorum may be required to complete bootstrapping a new cluster. For example, if the instance is configured with a Raft [partition group][partition-groups], a majority of the group's members must be `start`ed for any single member to complete startup.

## Joining an existing cluster

Bootstrapping an Atomix cluster is simple, but joining an existing cluster can be a more complex and risky process. It's critical that instances joining an existing cluster be able to identify and communicate with nodes in that cluster. To join a cluster, simply list a set of `Member`s from the running cluster.

```java
Atomix atomix = Atomix.builder()
  .withLocalMember(Member.builder("member4")
    .withType(Member.Type.EPHEMERAL)
    .withAddress("localhost:5004")
    .build())
  .withMembers(
      Member.builder("member1")
        .withType(Member.Type.PERSISTENT)
        .withAddress("localhost:5001")
        .build(),
      Member.builder("member2")
        .withType(Member.Type.PERSISTENT)
        .withAddress("localhost:5002")
        .build(),
      Member.builder("member3")
        .withType(Member.Type.PERSISTENT)
        .withAddress("localhost:5003")
        .build())
  .build();

atomix.start().join();
```

To join the cluster, the instance will broadcast its configuration to each of the members in listed in its membership list. Once successful, those nodes will gossip the joining node's information to any remaining nodes and will send the information about unknown members back to the joining node.

{:.callout .callout-info}
It may be convenient to choose a set of `PERSISTENT` members through which all new nodes join.

## File-based Configuration

As with all other components of Atomix, clusters support file-based configurations via JSON or YAML. The configuration file format mimics that of the builder API:

`cluster.yaml`

```java
local-member:
  name: member4
  type: ephemeral
  address: localhost:5004
members:
  member1:
    type: persistent
    address: localhost:5001
  member2:
    type: persistent
    address: localhost:5002
  member3:
    type: persistent
    address: localhost:5003
```

The configuration file can be used to configure the Atomix [agent][agent] or can be passed directly to the `AtomixCluster` API:

```java
AtomixCluster cluster = new AtomixCluster("cluster.yaml");
```

{:.callout .callout-info}
When constructing an `Atomix` instance from a configuration file, the cluster configuration should be namespaced under the `cluster` field.

Additionally, builders can be initialized using the cluster configuration. This can be convenient for initializing a builder with a shared configuration:

```java
AtomixCluster cluster = AtomixCluster.builder("cluster.yaml")
  .withLocalMember(Member.builder("member4")
    .withType(Member.Type.EPHEMERAL)
    .withAddress("localhost:5004")
    .build())
  .build();
```

{% include common-links.html %}
