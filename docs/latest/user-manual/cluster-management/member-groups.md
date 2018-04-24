---
layout: user-manual
project: atomix
menu: user-manual
title: Member Groups
---

Primary-backup partition groups distribute partitions among multiple members of the cluster. However, if multiple replicas within a partition are on the same rack or host, a single failure can result in the loss of data. It's imperative that data be distributed across physical locations to avoid catastrophic failures leading to data loss. Atomix provides member groups to solve this problem.

### Rack Awareness

To configure zone/rack/host awareness, members of the cluster must first be configured with information about their physical location. The [`Member`][Member] builder supports the following location information:
* `zone` - a `String` zone
* `rack` - a `String` rack
* `host` - a `String` host name, useful when deploying Atomix nodes in containers

```java
Atomix.Builder builder = Atomix.builder()
  .withLocalMember(Member.builder("member-4")
    .withType(Member.Type.EPHEMERAL)
    .withAddress("localhost:5004")
    .withRack("rack-1")
    .build())
  .withMembers(
      Member.builder("member-1")
        .withType(Member.Type.EPHEMERAL)
        .withAddress("localhost:5001")
        .withRack("rack-1")
        .build(),
      Member.builder("member-2")
        .withType(Member.Type.EPHEMERAL)
        .withAddress("localhost:5002")
        .withRaft("rack-2")
        .build(),
      Member.builder("member-3")
        .withType(Member.Type.EPHEMERAL)
        .withAddress("localhost:5003")
        .withRack("rack-2")
        .build());
```

In addition to configuring the member properties, the [`PrimaryBackupPartitionGroup`][PrimaryBackupPartitionGroup] must also be configured for rack awareness by providing a [`MemberGroupStrategy`][MemberGroupStrategy]:

```java
builder.addPartitionGroup(PrimaryBackupPartitionGroup.builder("data")
  .withPartitions(32)
  .withMemberGroupStrategy(MemberGroupStrategy.RACK_AWARE)
  .build());
```

When the `RACK_AWARE` strategy is used, the primary and backups for a given partition will be spread across configured racks. For example, if `member-2` in `rack-2` is elected primary for partition `1`, the next backup in partition `1` will always be in `rack-1`.

The available strategies provided by [`MemberGroupStrategy`][MemberGroupStrategy] are:
* `ZONE_AWARE` - groups members by the `zone()` attribute
* `RACK_AWARE` - groups members by the `rack()` attribute
* `HOST_AWARE` - groups members by the `host()` attribute
* `NODE_AWARE` - groups members by [`MemberId`][MemberId]

If a grouping attribute is `null` then by default the member will be placed in its own group by its `MemberId`.

Member group strategies can also be configured via configuration files:

```
cluster:
  local-member:
    name: member-4
    type: ephemeral
    address: localhost:5004
    rack: rack-1
  members:
    member-1:
      type: ephemeral
      address: localhost:5001
      rack: rack-1
    member-2:
      type: ephemeral
      address: localhost:5002
      rack: rack-2
    member-3:
      type: ephemeral
      address: localhost:5003
      rack: rack-2
partition-groups:
  data:
    type: primary-backup
    partitions: 32
    member-group-strategy: RACK_AWARE
```

{% include common-links.html %}
