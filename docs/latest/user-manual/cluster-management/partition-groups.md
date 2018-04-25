---
layout: user-manual
project: atomix
menu: user-manual
title: Partition Groups
---

Atomix distributes [primitives][primitives] in portions of the cluster called _partition groups_. Partition groups are collections of partitions (or shards) distributed on a set of nodes in the cluster using a configurable replication protocol. Atomix clusters can be configured with any number of partition groups, and each group may replicate a distinct set of primitives.

## Configuring Partition Groups

Partition groups are configured by either providing them to the [`Atomix`][Atomix] builder or in the Atomix configuration file. Each partition group configuration has three standard attributes:
* `name` - every partition group must have a name that is unique across all partition groups in the cluster
* `type` - the partition group type defines the replication protocol implemented by the partitions. In Java builders, the type is the partition group class (e.g. `RaftPartitionGroup` implements the Raft protocol), but in configuration files the `type` must be provided
* `partitions` - the number of partitions in the group

Specific partition group types may implement additional options. As with other areas of the Atomix cluster configuration, Atomix uses builders to configure partition groups:

```java
PartitionGroup primaryBackupGroup = PrimaryBackupPartitionGroup.builder("data")
  .withNumPartitions(32)
  .build();
```

Partition group `builder` methods accept the partition group name as a required argument.

### Group Discovery

When configuring partition groups, only the nodes intended to participate in the replication of a given group should add the group to their instance configuration. If a Raft group is configured on an `Atomix` instance, that instance will participate in the Raft protocol. Similarly, if a primary-backup group is configured on an instance, that instance will participate in the primary-backup protocol.

Instances not configured with groups that exist on other nodes will discover those groups at startup. Note, however, that group discovery can block or fail the startup process during network partitions.

### The Management Group

Before configuring any partition groups in a cluster, the cluster must first be configured with a _system management group_. The management group is used internally by Atomix to store primitive information and by user partition groups to coordinate replication protocols. For example, the primary-backup partition group implementation uses the management group for primary election.

To configure the system management group on an [`Atomix`][Atomix] builder, use the `withManagementGroup` method:

```java
Atomix atomix = Atomix.builder()
  .withLocalMember(...)
  .withMembers(...)
  .withManagementGroup(RaftPartitionGroup.builder("system")
    .withNumPartitions(1)
    .withMembers("member-1", "member-2", "member-3")
    .build())
  .build();
```

Note that the cluster _must_ be configured with a system management group if [primitive groups](#primitive-groups) are defined. However, the instance does not have to be configured with a management group if one exists on other members in the cluster.

When using a file-based configuration, configure the `management-group`:

```
cluster:
  local-member:
    ...
  members:
    ...
management-group:
  type: raft
  name: system
  partitions: 1
  members:
    - member-1
    - member-2
    - member-3
```

### Primitive Groups

The [system management group](#system-management-group) helps Atomix manage distributed primitives and partition groups, but in order to store and replicate primitives, additional partition groups must be defined. Any number of primitive partition groups may be configured, and primitive instances may be replicated within any desired partition group.

To configure the primitive partition groups, use the `withPartitionGroups` method on the [`Atomix`][Atomix] builder:

```java
Atomix atomix = Atomix.builder()
  .withLocalMember(...)
  .withMembers(...)
  .withManagementGroup(RaftPartitionGroup.builder("system")
    .withNumPartitions(1)
    .withMembers("member-1", "member-2", "member-3")
    .build())
  .withPartitionGroups(
    PrimaryBackupPartitionGroup.builder("data")
      .withNumPartitions(32)
      .build())
  .build();
```

## Raft Partition Groups

The [Raft protocol][Raft] is a consensus protocol developed in 2013. Consensus protocols are partition tolerant and provide strong consistency guarantees (linearizability, sequential consistency) that can be useful for coordination. However, strong consistency comes with a cost in terms of configuration and performance.

The [`RaftPartitionGroup`][RaftPartitionGroup] provides a set of partitions based on a complete, mature implementation of the Raft consensus protocol. To configure a Raft partition group, use the builder:

```java
RaftPartitionGroup.Builder raftBuilder = RaftPartitionGroup.builder("data");
```

Critically, Raft partition groups require explicitly defined membership. Each Raft group must identify the cluster members on which the group's partitions will be replicated at startup. Without explicitly defined membership, Raft partitions may experience split brain when a network partition occurs while bootstrapping the cluster.

To configure the group's members, use the `withMembers` method, passing a list of [`Member`][Member] IDs:

```java
raftBuilder.withMembers("member-1", "member-2", "member-3");
```

The Raft partition group's members must be `PERSISTENT`. This constraint exists because the semantics of persistent members accurately reflect the semantics of Raft cluster members: even after a Raft node crashes, the quorum size remains the same and the node still counts towards vote tallies.

Once the group has been configured, call the `build()` method to build the group:

```java
RaftPartitionGroup raftGroup = builder.build();
```

Raft partition groups are strongly recommended for use in the management of the Atomix cluster. When configured as the management group, Raft can provide reliable primary elections for primary-backup partition groups:

```java
Atomix atomix = Atomix.builder()
  .withLocalMember("member-1")
  .withMembers(
      Member.builder("member-1")
        .withType(Member.Type.PERSISTENT)
        .withAddress("localhost:5001")
        .build(),
      Member.builder("member-2")
        .withType(Member.Type.PERSISTENT)
        .withAddress("localhost:5002")
        .build(),
      Member.builder("member-3")
        .withType(Member.Type.PERSISTENT)
        .withAddress("localhost:5003")
        .build())
  .withManagementGroup(RaftPartitionGroup.builder("system")
    .withNumPartitions(1)
    .withMembers("member-1", "member-2", "member-3")
    .build())
  .withPartitionGroups(
    PrimaryBackupPartitionGroup.builder("data")
      .withNumPartitions(32)
      .build())
  .build();
```

As with other partition groups, Raft groups can be configured via configuration files. The above configuration when translated to YAML looks like this:

```
cluster:
  local-member:
    name: member-1
  members:
    member-1:
      type: persistent
      address: localhost:5001
    member-2:
      type: persistent
      address: localhost:5002
    member-3:
      type: persistent
      address: localhost:5003
management-group:
  type: raft
  name: system
  partitions: 1
  members:
    - member-1
    - member-2
    - member-3
partition-groups:
  data:
    type: primary-backup
    partitions: 32
```

## Primary-Backup Partition Groups

Even with sharding, Raft partition groups can be limited in their scalability. Writes to Raft partitions must be synchronously replicated to a majority of the cluster and must be flushed to disk prior to completion of a write operation. Primary-backup partition groups are a more efficient alternative to Raft partitions. Primary-backup replication works by electing a leader through which writes are replicated. The leader replicates to _n_ backups based on the primitive configuration. Primary-backup partitions are managed entirely in-memory and have options for synchronous or asynchronous replication.

{:.callout .callout-warning}
Primary-backup partitions are only as reliable as the protocol used in the [system management group](#the-management-group). For the strongest consistency and reliability guarantees, use a Raft management group.

Primary-backup groups are configured via the [`PrimaryBackupPartitionGroup`] builder:

```java
PartitionGroup primaryBackupGroup = PrimaryBackupPartitionGroup.builder("data")
  .withNumPartitions(32)
  .build();
```

The configuration for primary-backup groups is simple. Most features of the replication protocol are provided on a per-primitive basis in the [primitive protocol][primitive-protocols]. One feature that is, however, important for primary-backup partitions is [member groups][member-groups], which provide zone/rack/host awareness for primary-backup partitions.

Primary-backup partition groups can, of course, be configured in configuration files:

```
partition-groups:
  data:
    type: primary-backup
    partitions: 32
```

## Profiles

Configuring management and primitive partition groups can be tedious for newcomers. As has been suggested in the preceding documentation, most cluster configurations can fit into only a few categories:
* Consensus
* Consensus-based data grid
* Eventually consistent data grid
* Client

Atomix provides an abstraction for common partition configurations known as _profiles_. Profiles are named objects that configure [`Atomix`][Atomix] instances for specific use cases:

```java
Atomix atomix = Atomix.builder()
  .withLocalMember("member-1")
  .withMembers(members)
  .withProfiles(Profile.CONSENSUS, Profile.DATA_GRID)
  .build();
```

The built-in profiles provided by Atomix are:
* `CONSENSUS` - creates a [Raft](#raft-partition-groups) system management group and a Raft primitive group named `raft` both replicated on all initially configured `PERSISTENT` members
* `DATA_GRID` - creates a [primary-backup](#primary-backup-partition-groups) system management group if no group already exists, and a primary-backup primitive group named `data`
* `CLIENT` - sets the local member to `EPHEMERAL` and does not configure any management or primitive groups

Profiles will configure the Atomix instance in the order in which they're specified. This allows, e.g., the `DATA_GRID` profile to configure primary-backup partitions that may or may not be backed by Raft depending on prior configurations. Thus, when chaining `Profile.CONSENSUS` and `Profile.DATA_GRID` we get a Raft-backed primary-backup `data` group for primitives.

The [`Atomix`][Atomix] configuration, of course, supports profiles via the `profiles    ` field:

```
cluster:
  local-member:
    name: member-1
  members:
    member-1:
      type: persistent
      address: localhost:5001
    member-2:
      type: persistent
      address: localhost:5002
    member-3:
      type: persistent
      address: localhost:5003
profiles:
  - consensus
  - data-grid
```

Additional partition groups may be added to profiles as well:

```
cluster:
  local-member:
    name: member-1
  members:
    member-1:
      type: persistent
      address: localhost:5001
    member-2:
      type: persistent
      address: localhost:5002
    member-3:
      type: persistent
      address: localhost:5003
profiles:
  - consensus
  - data-grid
partition-groups:
  more-data:
    type: primary-backup
    partitions: 7
```

{% include common-links.html %}
