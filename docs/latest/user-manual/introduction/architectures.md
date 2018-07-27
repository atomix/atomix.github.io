---
layout: user-manual
project: atomix
menu: user-manual
title: Architectures
---

Atomix is designed to be un-opinionated, and that features extends even to the structure of the cluster itself. Atomix clusters can be architected in many different ways, so it can sometimes be confusing for new users trying to figure out how to architect their Atomix cluster.

In Atomix, every node is treated as a normal member of the cluster. Nodes differ only in their configuration, i.e. how they replicate data. This allows for many different configurations.

## Data-Grid

The most common architecture for projects like Atomix is a simple data grid:
![Data-Grid](https://image.ibb.co/np2D3o/Data_Grid.png)

The data grid uses a partitioned primary-backup (or multi-primary) protocol to distributed primitive state across all the nodes in the cluster. This architecture is both scalable and efficient, replicating state only on a configurable number of nodes and balancing reads and writes across all the nodes in the cluster. Add to this the ability to dynamically discover nodes, and the data grid architecture makes for a highly flexible, highly scalable one.

The data-grid architecture can be achieved in Atomix using primary-backup partition groups and multicast discovery:

```hocon
# The cluster configuration defines how nodes discover and communicate with one another
cluster {
  multicast-enabled: true   # Enable multicast discovery
  discovery.type: multicast # Configure the cluster membership to use multicast
}

# The management group coordinates higher level partition groups and is required
management-group {
  type: primary-backup # Use the primary-backup protocol
  partitions: 1        # Use only a single partition for system management
}

# Partition groups are collections of partitions in which primitives are replicated
# This sets up a partition group named `data` on this node
partition-groups.data {
  type: primary-backup # Use the primary-backup protocol
  partitions: 71       # Use 71 partitions for scalability
  member-group-strategy: RACK_AWARE # Replicate partitions across physical racks
}
```

The data grid architecture supports rack awareness wherein backups will be replicated across physical racks.

With this architecture, we can create primitives replicated in the data grid simply by configuring them with a `MultiPrimaryProtocol`:

```java
Map<String, String> map = atomix.mapBuilder("my-map")
  .withProtocol(MultiPrimaryProtocol.builder()
    .withNumBackups(2)
    .build())
  .build();

map.put("foo", "bar");
```

Simple data grid architectures have one draw back for certain types of applications, though. The data grid architecture as described here is an AP system. In a network partition, this data grid may experience split brain and lose data.

## Consistent Data-Grid

To avoid data loss and other inconsistencies during network partitions, we introduce the use of consensus:

![Consistent Data-Grid](https://image.ibb.co/jhEt3o/Consistent_Data_Grid.png)

Atomix includes one of the most advanced implementations of the [Raft consensus algorithm][Raft] in existence, and that implementation is used in part to coordinate the primary-backup protocol. This is done by configuring a subset of the nodes with a Raft management group:

`raft.conf`

```hocon
# The cluster configuration defines how nodes discover and communicate with one another
cluster {
  multicast-enabled: true   # Enable multicast discovery
  discovery.type: multicast # Configure the cluster membership to use multicast
}

# The management group coordinates higher level partition groups and is required
# This node configures only a management group and no partition groups since it's
# used only for partition/primitive management
management-group {
  type: raft # Use the Raft consensus protocol for system management
  partitions: 1 # Use only a single partition
  members: [raft-1, raft-2, raft-3] # Raft requires a static membership list
}
```

The management group is used by Atomix to coordinate the cluster: elect primaries, manage primitives and transactions, and replicate configurations. Once the set of Raft management nodes has been bootstrapped, additional nodes configured without the `management-group` will connect to the Raft management nodes and use Raft for partition management:

`data-grid.conf`

```hocon
# The cluster configuration defines how nodes discover and communicate with one another
cluster {
  multicast-enabled: true   # Enable multicast discovery
  discovery.type: multicast # Configure the cluster membership to use multicast
}

# This node does not configure a management group since that group is on another
# node. Since the management group is consensus-based, participating in system
# management on this node would constrain its fault tolerance.

# Partition groups are collections of partitions in which primitives are replicated
# This sets up a partition group named `data` on this node
partition-groups.data {
  type: primary-backup # Use the primary-backup protocol
  partitions: 71       # Use 71 partitions for scalability
  member-group-strategy: RACK_AWARE # Replicate partitions across physical racks
}
```

With this architecture, data grid primitives are still created in the same manner as before, but they transparently use the Raft protocol for more reliable primary election and replication.

```java
Map<String, String> map = atomix.mapBuilder("my-map")
  .withProtocol(MultiPrimaryProtocol.builder()
    .withNumBackups(2)
    .build())
  .build();

map.put("foo", "bar");
```

Note that this architecture separates the management and data groups on separate nodes, but the management group could just as well be configured to be replicated on a subset of the data nodes.

## Raft Client-Server

Of course, the cluster can also be configured for a traditional client-server architecture with a scalable multi-Raft partition group.

![Raft Client](https://image.ibb.co/cKO9b8/Multi_Raft_Client.png)

To scale Raft based primitives in the same manner as we've done for primary-backup primitives, we simply increase the number of partitions again.

`raft.conf`

```hocon
# The cluster configuration defines how nodes discover and communicate with one another
cluster {
  multicast-enabled: true   # Enable multicast discovery
  discovery.type: multicast # Configure the cluster membership to use multicast
}

# The management group coordinates higher level partition groups and is required
# This node configures only a management group and no partition groups since it's
# used only for partition/primitive management
management-group {
  type: raft # Use the Raft consensus protocol for system management
  partitions: 1 # Use only a single partition
  members: [raft-1, raft-2, raft-3] # Raft requires a static membership list
}

# Configure a Raft partition group named "raft"
partition-groups.raft {
  type: raft # Use the Raft consensus protocol for this group
  partitions: 7 # Configure the group with 7 partitions
  members: [raft-1, raft-2, raft-3] # Raft requires a static membership list
}
```

Once we've configured the set of Raft nodes with a `raft` partition group, clients can connect to the Raft nodes to operate on primitives using a multi-Raft protocol. As mentioned, Atomix treats all nodes the same, so setting up a client node is simply a matter of configuring a stateless Atomix node:

`client.conf`

```hocon
# The cluster configuration defines how nodes discover and communicate with one another
cluster {
  multicast-enabled: true   # Enable multicast discovery
  discovery.type: multicast # Configure the cluster membership to use multicast
}

# Partition groups will be discovered from other nodes
```

The client will discover the Raft nodes and through them the Raft partition groups. Once a client node has been bootstrapped, it can create a multi-Raft based primitive using the `MultiRaftProtocol`:

```java
Map<String, String> map = atomix.mapBuilder("my-map")
  .withProtocol(MultiRaftProtocol.builder()
    .withReadConsistency(ReadConsistency.SEQUENTIAL)
    .withCommunicationStrategy(CommunicationStrategy.FOLLOWER)
    .build())
  .build();

map.put("foo", "bar");
```

The multi-Raft primitive will be partitioned among each of the configured Raft partitions.

## Consistent Data-Grid Client-Server

Of course, there's no limitation to the number of partition groups that can be configured in a cluster or even on a single node. This allows for architectures that support multiple configurable replication protocols.

![Consistent Data-Grid Client](https://image.ibb.co/fqzhw8/Consistent_Primary_Backup_Client_Server.png)

Similarly, these protocols can be configured on a single node:

`atomix.conf`

```hocon
# The cluster configuration defines how nodes discover and communicate with one another
cluster {
  multicast-enabled: true   # Enable multicast discovery
  discovery.type: multicast # Configure the cluster membership to use multicast
}

# The management group coordinates higher level partition groups and is required
management-group {
  type: raft # Use the Raft consensus protocol for system management
  partitions: 1 # Use only a single partition
  members: [raft-1, raft-2, raft-3] # Raft requires a static membership list
}

# Configure a primary-backup group named "data"
partition-groups.data {
  type: primary-backup # Use the primary-backup protocol
  partitions: 71       # Use 71 partitions for scalability
  member-group-strategy: RACK_AWARE # Replicate partitions across physical racks
}

# Configure a Raft partition group named "raft"
partition-groups.raft {
  type: raft # Use the Raft consensus protocol for this group
  partitions: 7 # Configure the group with 7 partitions
  members: [raft-1, raft-2, raft-3] # Raft requires a static membership list
}
```

## REST Client-Server

The stateless client configuration allows for one more interesting architecture. To support clients in any language, the Atomix agent can be used as a REST proxy to Atomix primitives.

![Multi-Raft Client-Server](https://image.ibb.co/bXWUb8/Multi_Raft_Client_Server.png)

By running an agent locally on each client node, clients can have language-agnostic access to Atomix cluster information and distributed primitives. Additionally, maintaining a one-to-one relationship between agents and REST clients affords consistency guarantees consistent with those of Java clients.

{% include common-links.html %}
