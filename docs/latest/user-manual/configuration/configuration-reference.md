---
layout: user-manual
project: atomix
menu: user-manual
title: Reference
---

## Atomix
* `cluster`*
  * `clusterId` - The unique cluster identifier. This is used to validate
    communication between Atomix nodes.
  * `node`* - The local node description.
    * `id` - The local node identifier. This must be unique among all nodes
    in the cluster. If no identifier is provided, a universally unique
    identifier (UUID) will be used.
    * `address`* - The local node address. This may be a `host:port` tuple,
    a `host`, or a `port`. Defaults to the first interface, port: `5679`.
    * `zone` - The zone in which the node resides. This can be used for
    zone-aware replication in certain protocols. Defaults to `null`.
    * `rack` - The rack in which the node resides. This can be used for
    rack-aware replication in certain protocols. Defaults to `null`.
    * `host` - The host on which the node resides. This can be used for
    host-aware replication in certain protocols. Defaults to `null`.
    * `properties` - An mapping of arbitrary node properties replicated
    by the cluster membership protocol.
      * `{key}`: `{value}`
      * ...
  * `discovery`* - The node [discovery protocol](#cluster-discovery-protocols)
  configuration, used to determine initial cluster membership.
    * `type`* - The [discovery protocol](#cluster-discovery-protocols) type
    name. This may be one of `bootstrap`, `multicast`, `dns`, or a custom
    protocol.
    * ... - Additional discovery protocol specific options.
  * `protocol` - The [cluster membership protocol](#cluster-membership-protocols)
  configuration, used for managing cluster membership, failure detection,
  and membership replication.
    * `type` - The [cluster membership protocol](#cluster-membership-protocols)
    type name. This may be one of `heartbeat`, `swim`, or a custom protocol
    implementation.
    * ... - Additional protocol-specific options.
  * `multicast` - The multicast service configuration.
    * `enabled` - Whether to enable multicast support. Defaults to `false`.
    Before enabling multicast, ensure multicast is supported by your network.
    * `group` - The multicast group. Defaults to `230.0.0.1`.
    * `port` - The multicast port. Defaults to `54321`.
  * `messaging` - The messaging service configuration.
    * `interfaces` - The interfaces to which to bind to listen for messages
    from peers. This may differ from the `cluster.node.address` hostname e.g.
    in containerized environments. Defaults to `0.0.0.0`.
    * `port` - The local port to which to bind to listen for messages from peers.
    This may differ from the `cluster.node.address` port e.g. in containerized
    environments.
    * `connectTimeout` - The messaging connect timeout. This may be specified
    in human readable format with a time unit, e.g. `1m` or `15s`. Defaults to `10s`.
    * `tls` - The messaging TLS configuration.
      * `enabled` - Whether to enable TLS for the messaging service. Defaults
      to `false`.
      * `keyStore` - The key store path. Defaults to the `javax.net.ssl.keyStore`
      system property or `conf/atomix.jks`.
      * `keyStorePassword` - The key store password. Defaults to the
      `javax.net.ssl.keyStorePassword` system property or `changeit`.
      * `trustStore` - The trust store path. Defaults to the
      `javax.net.ssl.trustStore` system property or `conf/atomix.jks`.
      * `trustStorePassword` - The trust store password. Defaults to the
      `javax.net.ssl.trustStorePassword` system property or `changeit`.
* `managementGroup`* - The partition group to use for managing primitives,
  transactions, sessions, etc.
  * `type` - The management partition group type. This may be one of
  [`raft`](#raft), [`primary-backup`](#primary-backup), [`log`](#log),
  or a custom partition group type.
  * ... - Additional partition group specific options.
* `partitionGroups`* - A mapping of named primitive partition groups in
which the configured node participates.
  * `{name}` - The unique partition group name.
    * `type` - The partition group type. This may be one of
    [`raft`](#raft), [`primary-backup`](#primary-backup), [`log`](#log),
    or a custom partition group type.
    * ... - Additional partition group specific options. See partition
    group reference below.
* `primitiveDefaults` - A mapping of default primitive configurations,
keyed by primitive type.
  * `{type}` - The primitive type name key, e.g. `map`, `atomic-map`, `lock`,
    `set`, `queue`, `leader-election`, etc.
    * `protocol` - The default protocol to use for primitives of the type.
    * ... - Additional primitive default options. See primitive reference below.
* `primitives`
  * `{name}`
    * `type` - The primitive type name, e.g. `map`, `atomic-map`, `lock`,
    `set`, `queue`, `leader-election`, etc.
    * `protocol` - The protocol to use for the primitive.
      * `type` - The primitive protocol type name. This may be one of
      `multi-raft`, `multi-primary`, `log`, or a custom protocol.
      * ... - Additional protocol-specific options. See protocol reference below.
    * ... - Additional primitive options. See primitive reference below.
* `enableShutdownHook` - Enables a hook that shuts down the Atomix node
when the JVM is shut down.

\* required

## Cluster Discovery Protocols

Cluster discovery protocols are pluggable objects configured in the
`cluster.discovery` field. Each discovery protocol is defined by a
`type` name:

```
cluster {
  discovery {
    type: bootstrap
    ...
  }
}
```

### Bootstrap Discovery Protocol

* `type`: `bootstrap`
* `nodes`* - A list of node objects indicating the nodes through which to
join the cluster.

\* required

#### Example

```
cluster {
  discovery {
    type: bootstrap
    nodes.1 {
      id: member-1
      address: localhost:5000
    }
    nodes.2 {
      id: member-2
      address: localhost:5001
    }
    nodes.3 {
      id: member-3
      address: localhost:5002
    }
  }
}
```

### Multicast Discovery Protocol

* `type`: `multicast`
* `broadcastInterval` - The interval at which to broadcast the local member
information to the multicast group. This may be specified in human readable
format with a time unit, e.g. `100ms` or `5s`. Defaults to `1s`.

#### Example

```
cluster {
  discovery {
    type: multicast
    broadcastInterval: 5s
  }
}
```

### DNS Discovery Protocol

* `type`: `dns`
* `service`* - The DNS SRV service name to look up.
* `resolutionInterval` - The interval at which to resolve DNS SRV entries.
This may be specified in human readable format with a time unit, e.g. `100ms`
or `5s`. Defaults to `15s`.

\* required

#### Example

```
cluster {
  discovery {
    type: dns
    service: atomix
  }
}
```

## Cluster Membership Protocols

Cluster membership protocols are pluggable objects configured in the
`cluster.protocol` field. Membership protocols define how cluster membership
is managed, member information is replicated, and failures are detected.
Protocol implementations are identified by the `type` field:

```
cluster {
  protocol {
    type: heartbeat
    ...
  }
}
```

### Heartbeat Protocol

* `type`: `heartbeat`
* `heartbeatInterval` - The interval at which to send heartbeats to peers.
This may be specified in human readable format with a time unit, e.g.
`100ms` or `5s`. Defaults to `1s`.
* `failureThreshold` - The phi accrual failure detector threshold. Defaults
to `10`.
* `failureTimeout` - The maximum failure timeout, used when not enough
heartbeats have been recorded in the phi failure detector. This may be
specified in human readable format with a time unit, e.g. `100ms` or `5s`.
Defaults to `10s`.

#### Example

```
cluster {
  protocol {
    type: heartbeat
    heartbeatInterval: 1s
  }
}
```

### SWIM Protocol

* `type`: `swim`
* `broadcastUpdates` - A boolean indicating whether to broadcast membership
updates to all peers. Enabling this option may increase network traffic but
 reduce the time it takes to propagate membership changes. Defaults to `false`.
* `broadcastDisputes` - A boolean indicating whether to broadcast disputes
to all peers. Enabling this option may increase network traffic but reduce
 the time it takes to propagate membership changes. Defaults to `true`.
* `notifySuspect` - A boolean indicating whether to notify a suspect member
when a suspicion is propagated. Enabling this option will increase network
traffic but may avoid false positives in failure detectors. Defaults to
`false`.
* `gossipInterval` - The interval at which the SWIM protocol gossips with
a random peer. This may be specified in human readable format with a time
unit, e.g. `100ms` or `5s`. Defaults to `250ms`.
* `gossipFanout` - The maximum number of nodes to which to broadcast
updates on each round of gossip. Defaults to `2`.
* `probeInterval` - The interval at which to attempt to probe a random
peer. This may be specified in human readable format with a time unit,
e.g. `100ms` or `5s`. Defaults to `1s`.
* `suspectProbes` - The number of probes to attempt before declaring a
member suspect. Defaults to `3`.
* `failureTimeout` - The time to allow a suspect member to refute its
state before declaring it dead. This may be specified in human readable
format with a time unit, e.g. `100ms` or `5s`. Defaults to `10s`.

#### Example

```
cluster {
  protocol {
    type: swim
    broadcastUpdates: true
    gossipInterval: 500ms
    probeInterval: 2s
    suspectProbes: 2
    failureTimeout: 15s
  }
}
```

## Raft

The Raft protocol provides both a [partition group](#raft-partition-group)
and a [primitive protocol](#multi-raft-protocol). The partition group and
protocol are used in a pair to configure partitions/replication and
primitive/session level options respectively:

```
partitionGroups.raft {
  type: raft
  ...
}

primitives.my-map {
  type: map
  protocol {
    type: multi-raft
    group: raft
    ...
  }
}
```

### Raft Partition Group

* `type`: `raft`
* `partitions` - The number of Raft partitions in the group. More partitions
implies greater parallelism. However, the overhead of Raft partitions makes
large numbers of partitions impractical unless distributed among a large set
of nodes. We recommend 1-2 partitions per group member. Defaults to `7`.
* `members`* - The fixed set of members in the partition group. The full
group membership is required for vote counting to safely form Raft partitions.
The value is a list of member IDs as defined by the `cluster.node.id` field.
* `partitionSize` - The size of each partition in the group. This is used to
compute the distribution of partitions among the group `members` and form
Raft partition clusters. Defaults to `0`, a magic value indicating the
partition size is equal to the number of `members` in the group.
* `storage` - The Raft storage configuration. This defines how Raft logs
and snapshots are stored on the local node.
  * `directory` - The directory in which to store Raft logs and snapshots
  for the partition group. Defaults to a named directory in the directory
  specified by the `--data-dir` agent argument if provided, otherwise the
  `atomix.data` system property.
  * `level` - The Raft log storage level. This may be one of `DISK` or
  `MAPPED`. Defaults to `DISK`.
  * `maxEntrySize` - The maximum size of each entry in the Raft log. Increasing
  the size increases the memory footprint of each Raft partition but allows
  larger individual writes to Raft-based primitives. This value may be specified
  in memory size format, e.g. `100KB`, `10MB`, etc. Defaults to `1MB`.
  * `maxSegmentSize` - The maximum size of each segment in the Raft log.
  Increasing the size may reduce the frequency of service snapshots but
  reduces the ability of the Raft partitions to conserve disk space.
  This value may be specified in memory size format, e.g. `100KB`, `10MB`,
  etc. Defaults to `32MB`.
  * `flushOnCommit` - A boolean indicating whether to flush the Raft logs
  to disk on every write. Enabling this option ensures durability for every
  write to Raft-based primitives but will increase the latency of Raft
  partitions. Disabling this option risks losing some recent writes after
  a majority of a Raft partition is lost. Defaults to `false`.
* `compaction` - The Raft log compaction configuration.
  * `dynamic` - Whether to enable dynamic compaction, allowing Raft partitions
  to optionally skip compaction during periods of high load. Defaults to
  `true`.
  * `freeDiskBuffer` - A percentage value of free disk space to require
  before Raft partitions will force compact logs. Defaults to `.2`.
  * `freeMemoryBuffer` - A percentage value of free memory to require before
  Raft partitions will force compact logs. This option applies only to storage
  configured with the `MAPPED` storage level. Defaults to `.2`.

\* required

#### Example

```
partitionGroups.raft {
  type: raft
  partitions: 3
  members: [member-1, member-2, member-3]
  storage {
    level: mapped
    flushOnCommit: true
  }
  compaction.dynamic: true
}
```

### Multi-Raft Protocol

* `type`: `multi-raft`
* `group` - The name of the [Raft partition group](#raft-partition-group)
on which to operate. If no group name is specified and only a single Raft
group is configured, the single group will be used.
* `minTimeout` - The minimum Raft session timeout. This may be specified
in human readable format with a time unit, e.g. `100ms` or `5s`. Defaults
to `250ms`.
* `maxTimeout` - The maximum Raft session timeout. This may be specified
in human readable format with a time unit, e.g. `100ms` or `5s`. Defaults
to `30s`.
* `readConsistency` - The consistency level with which to execute primitive
reads against Raft partitions. This option dictates whether the primitive
reads are executed against Raft followers or leaders and how read operations
are sequenced among concurrent operations. The value may be one of
`SEQUENTIAL`, `LINEARIZABLE`, or `LINEARIZABLE_LEASE`. Defaults to
`SEQUENTIAL`.
* `communicationStrategy` - The strategy with which to communicate with
nodes in each Raft partition. The value may be one of `LEADER`, `FOLLOWERS`,
or `ANY`. Communication with followers can spread the network load more
evenly among the partitions but may introduce additional latency when
switching between reads and writes. Defaults to `LEADER`.
* `recoveryStrategy` - The strategy with which to recover expired Raft
sessions. This may be one of `RECOVER` or `CLOSE`. Defaults to `RECOVER`.
* `maxRetries` - The maximum number of retries to perform per operation.
Note that retries break program order guarantees. Defaults to `0`.
* `retryDelay` - The delay between each operation retry. This may be
specified in human readable format with a time unit, e.g. `100ms` or `5s`.
Defaults to `100ms`.

#### Example

```
primitives.my-lock {
  type: lock
  protocol {
    type: multi-raft
    group: raft
    readConsistency: linearizable
    communicationStrategy: leader
  }
}
```

## Primary-Backup

The primary-backup protocol provides both a [partition group](#primary-backup-partition-group)
and a [primitive protocol](#multi-primary-protocol). The partition group and
protocol are used in a pair to configure partitions/replication and
primitive/session level options respectively:

```
partitionGroups.data {
  type: primary-backup
  ...
}

primitives.my-map {
  type: map
  protocol {
    type: multi-primary
    group: primary-backup
    ...
  }
}
```

### Primary-Backup Partition Group

* `type`: `primary-backup`
* `partitions` - The number of primary-backup partitions in the group.
A larger number of partitions improves parallelism and state distribution.
Defaults to `71`.
* `memberGroupStrategy` - The member group strategy defines how partitions
are distributed among the cluster members. The value may be one of
`NODE_AWARE`, `HOST_AWARE`, `RACK_AWARE`, or `ZONE_AWARE`. Defaults to
`NODE_AWARE`.

#### Example

```
cluster.node {
  id: member-1
  address: localhost:5000
  rack: rack-1
}

partitionGroups.data {
  type: primary-backup
  partitions: 32
  memberGroupStrategy: rack-aware
}
```

### Multi-Primary Protocol

* `type`: `multi-primary`
* `group` - The name of the [primary-backup partition group](#primary-backup-partition-group)
on which to operate. If no group name is specified and only a single
primary-backup group is configured, the single group will be used.
* `replication` - The partition group replication strategy. This may be
one of `SYNCHRONOUS` or `ASYNCHRONOUS`. Defaults to `ASYNCHRONOUS`.
* `recovery` - The strategy with which to recover expired primary-backup
sessions. This may be one of `RECOVER` or `CLOSE`. Defaults to `RECOVER`.
* `backups` - The number of backups for the primitive. Defaults to `1`.
* `maxRetries` - The maximum number of retries to perform per operation.
Note that retries break program order guarantees. Defaults to `0`.
* `retryDelay` - The delay between each operation retry. This may be
specified in human readable format with a time unit, e.g. `100ms` or `5s`.
Defaults to `100ms`.

#### Example

```
primitives.my-map {
  type: map
  protocol {
    type: multi-primary
    group: data
    replication: asynchronous
    backups: 2
  }
}
```

## Distributed Log

The log protocol provides both a [partition group](#log-partition-group)
and a [primitive protocol](#log-protocol). The partition group and
protocol are used in a pair to configure partitions/replication and
primitive/session level options respectively:

```
partitionGroups.logs {
  type: log
  ...
}

primitives.my-log {
  type: log
  protocol {
    type: log
    group: logs
    ...
  }
}
```

### Log Partition Group

* `type`: `log`
* `partitions` - The number of Raft partitions in the group. More partitions
implies greater parallelism. However, the overhead of log partitions makes
large numbers of partitions impractical unless distributed among a large set
of nodes. We recommend 1-2 partitions per group member. Defaults to `7`.
* `memberGroupStrategy` - The member group strategy defines how partitions
are distributed among the group members. The value may be one of
`NODE_AWARE`, `HOST_AWARE`, `RACK_AWARE`, or `ZONE_AWARE`. Defaults to
`NODE_AWARE`.
* `storage` - The log storage configuration. This defines how logs are
stored on the local node.
  * `directory` - The directory in which to store logs for the partition
  group. Defaults to a named directory in the directory specified by the
  `--data-dir` agent argument if provided, otherwise the `atomix.data`
  system property.
  * `level` - The log storage level. This may be one of `DISK` or
  `MAPPED`. Defaults to `DISK`.
  * `maxEntrySize` - The maximum size of each entry in the Raft log. Increasing
  the size increases the memory footprint of each log partition but allows
  larger individual writes to the log. This value may be specified
  in memory size format, e.g. `100KB`, `10MB`, etc. Defaults to `1MB`.
  * `maxSegmentSize` - The maximum size of each segment in the log.
  Increasing the size of the segments may improve performance but reduces
  the granularity of log compaction. This value may be specified in memory
  size format, e.g. `100KB`, `10MB`, etc. Defaults to `32MB`.
  * `flushOnCommit` - A boolean indicating whether to flush the logs
  to disk on every write. Enabling this option ensures durability for every
  write to the log but will increase the latency of log partitions.
  Defaults to `false`.
* `compaction` - The log compaction configuration.
  * `size` - Specifies the size after which to remove log entries from each
  partition. This value may be specified in memory size format, e.g. `100KB`,
  `10MB`, etc. Defaults to `1GB`.
  * `age` - Specifies the age after which to remove log entries from each
  partition. This value may be specified in time format, e.g. `1h`, `1d`,
  etc. Defaults to `null` which disables time-based compaction.

#### Example

```
partitionGroups.logs {
  type: log
  partitions: 7
  storage.level: mapped
  compaction.age: 1d
}
```

### Log Protocol

* `type`: `log`
* `group` - The name of the [log partition group](#log-partition-group)
on which to operate. If no group name is specified and only a single log
group is configured, the single group will be used.
* `replication` - The partition group replication strategy. This may be
one of `SYNCHRONOUS` or `ASYNCHRONOUS`. Defaults to `ASYNCHRONOUS`.
* `recovery` - The strategy with which to recover expired primary-backup
sessions. This may be one of `RECOVER` or `CLOSE`. Defaults to `RECOVER`.
* `maxRetries` - The maximum number of retries to perform per operation.
Note that retries break program order guarantees. Defaults to `0`.
* `retryDelay` - The delay between each operation retry. This may be
specified in human readable format with a time unit, e.g. `100ms` or `5s`.
Defaults to `100ms`.

#### Example

```
primitives.my-log {
  type: log
  protocol {
    type: log
    group: logs
    replication: synchronous
  }
}
```

{% include common-links.html %}
