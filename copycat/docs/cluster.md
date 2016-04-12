---
layout: docs
project: copycat
menu: docs
title: Getting Started
pitch: Managing the Copycat cluster
first-section: cluster
---

Copycat servers interact with one another within the context of a Copycat [`Cluster`][Cluster]. Once started, each server is represented by a [`Member`][Member] within the cluster, and users of each server can access the [`Cluster`][Cluster] through the server API.

## Cluster lifecycle

Underlying each [`Cluster`][Cluster] instance is a persistent cluster configuration. The cluster configuration is managed through the underlying implementation of the [Raft consensus algorithm][Raft]. When a `CopycatServer` joins the cluster, a configuration change is submitted to the cluster leader which logs and replicates the configuration change. Similarly, when any other change to a member of the cluster is requested - a server is removed from the cluster or promoted or demoted - a configuration change is submitted to the cluster leader where it's logged and replicated. This ensures that the cluster API receives the same consistency guarantees as replicated state machines.

Cluster configurations are persisted via the configured [`Storage`][Storage] object on each Copycat server. When a configuration change is committed, servers will store the most recent configuration in a `meta` file on disk. When a server is started, if it detects an existing configuration on disk, the on-disk configuration will override any user-provided configuration. This allows clusters to evolve independently of initial configurations.

### Accessing the cluster

The [`Cluster`][Cluster] can be accessed through any [`CopycatServer`][CopycatServer] instance via the `cluster` getter:

```java
server.start().join();

Cluster cluster = server.cluster();
```

### Cluster term and leader

Clusters expose the current `leader()` and `term()` through the [`Cluster`][Cluster] API.

```java
long term = server.cluster().term();
Member leader = server.cluster().leader();
```

The leader and term are representative of the local Copycat server's known leader and term. This is important to note as Copycat cannot guarantee that the leader or term is consistent. Copycat clusters are asynchronous, and two leaders may exist at any given time. Users should not rely upon the `leader` and `term` for consistency.

## Members

Copycat clusters consist of a set of [`Member`][Member]s. Each member in a [`Cluster`][Cluster] represents a single instance of a [`CopycatServer`][CopycatServer]. Members can be accessed through various getters provided by the cluster API.

To access the [`Member`][Member] representing the local [`CopycatServer`][CopycatServer], use the `member()` getter:

```java
Member localMember = server.cluster().member();
```

To access all remote members, use the `members()` getter, or to access a specific remote member, pass an [`Address`][Address] or member ID to the `member` getter:

```java
server.cluster().members().forEach(member -> {
  member.onStatusChange(status -> {
    System.out.println(member.id() + " status changed to " + status);
  });
});
```

### Listening for membership changes

Users can listen for changes to the structure of the Copycat [`Cluster`][Cluster] by registering join and leave listeners. When new servers `join` the cluster, configuration changes will be propagated to all servers and `onJoin` callbacks will be triggered. Similarly, when servers `leave` or are `remove`d from the cluster, configuration changes will be propagated to all servers and `onLeave` callbacks will be triggered.

```java
server.cluster().onJoin(member -> {
  System.out.println(member.address() + " joined the cluster");
});

server.cluster().onLeave(member -> {
  System.out.println(member.address() + " left the cluster");
});
```

## Member types

Each [`Member`][Member] of a Copycat cluster has an associated [`Type`][Member.Type]. Member types define how a server interacts with the rest of the cluster. Some nodes in a Copycat cluster may participate in the Raft consensus algorithm, which other nodes may simply receive state changes controlled by the Raft nodes. Each member can only be assigned to a single type at any given time, and types can be changed via the [`Cluster`][Cluster] API. As with other cluster state changes, type changes are controlled by the cluster leader where they're logged and replicated.

### Active members

Active members are servers that participate fully in the Raft consensus algorithm. Active members are represented by [`Member.Type.ACTIVE`][Member.Type]. Each cluster must necessarily consist of at least one active member. Active members participate in elections, can be elected leader, and can service reads and writes.

```java
if (server.cluster().member().type() == Member.Type.ACTIVE) {
  ...
}
```

### Passive members

Passive members are stateful servers that do not participate in the Raft consensus algorithm but instead receive state changes via a gossip protocol *after* they're committed through the consensus cluster. Passive members are represented by [`Member.Type.PASSIVE`][Member.Type] and can be used to scale reads across a larger number of nodes than the restricted number of `ACTIVE` members.

```java
if (server.cluster().member().type() == Member.Type.PASSIVE) {
  ...
}
```

### Reserve members

Reserve members are stateless servers that neither participate in the Raft consensus algorithm nor replication of any kind. Reserve servers are represented by [`Member.Type.RESERVE`][Member.Type] and typically serve as backups to the stateful members of the cluster.

```java
if (server.cluster().member().type() == Member.Type.RESERVE) {
  ...
}
```

### Promoting members

Members can be transitioned between types by any member of the cluster through the [`Cluster`][Cluster] API. Member types are hierarchical. The lowest member type is [`Member.Type.RESERVE`][Member.Type], and the highest member type is [`Member.Type.ACTIVE`][Member.Type]. To promote a member from a lower type to a higher type, use the [`Member`][Member]'s `promote()` method:

```java
server.cluster().member(address).promote(Member.Type.ACTIVE).whenComplete((result, error) -> {
  if (error == null) {
    // Member promoted successfully
  }
});
```

Keep in mind that promoting a member to `ACTIVE` will result in a change in the consensus cluster. This means increased fault tolerance since the consensus cluster can tolerate the failure of a minority of servers in the cluster, but it also may mean reduced write throughput.

### Demoting members

As with promoting members from lower types to higher types, members can also be demoted from higher types to lower types. The lowest member type is [`Member.Type.RESERVE`][Member.Type], and the highest member type is [`Member.Type.ACTIVE`][Member.Type]. To demote a member from a higher type to a lower type, use the [`Member`][Member]'s `demote()` method:

```java
server.cluster().member(address).demote(Member.Type.PASSIVE).whenComplete((result, error) -> {
  if (error == null) {
    // Member demoted successfully
  }
});
```

Once a member is demoted, the demotion will be propagated to all other nodes in the cluster and `onTypeChange` callbacks will be triggered. Remember that demoting an `ACTIVE` member will result in the consensus cluster size shrinking. This can mean greater write performance but reduced fault tolerance.

### Removing members

The need to remove a failed server from a cluster is a common task in distributed systems. If servers can only remove themselves from a cluster then the permanent failure of a server could mean it must permanently reside in the cluster's configuration. Copycat provides a mechanism for any server to remove any other server from the cluster via the [`Cluster`][Cluster] API with the [`Member`][Member]'s `remove()` method:

```java
server.cluster().member(address).remove().whenComplete((result, error) -> {
  if (error == null) {
    // Member removed from the cluster
  }
});
```

Once a member is removed from the cluster, the configuration change will be propagated to all other nodes in the cluster and `onLeave` event callbacks will be triggered.

### Listening for member type changes

Users can listen for changes to the type of a server via the [`Member`][Member] object for a given server. To listen for type changes, register a listener via the `onTypeChange` method:

```java
Member member = server.cluster().member(address);
member.onTypeChange(type -> {
  System.out.println(member.address() + " type changed to " + type);
});
```

The callback will be called with the [`Member.Type`][Member.Type] to which the member transitioned.

## Member statuses

Copycat's replication algorithm is optimized based on the availability of servers. In the event that a server cannot be reached by the leader, the leader will cease attempts to replicate state to the server and instead only send empty heartbeats until it can re-establish communication. To do so, leaders track the availability of individual servers in the cluster configuration, and this information is exposed to users as the [`Member.Status`][Member.Status].

Each member of the cluster can be associated with one of two statuses at any given time:
* `AVAILABLE` - indicates that the leader is able to heartbeat the member
* `UNAVAILABLE` - indicates that the leader is unable to heartbeat the member

Once a leader fails to send several heartbeats to a server it will commit a configuration change marking the member [`UNAVAILABLE`][Member.Status]. The status change will be propagated to all the servers in the cluster and can be accessed via the [`Member`][Member] API:

```java
Member.Status status = server.cluster().member(address).status();
```

Users can listen for changes in the availability of a member by registering a status change listener via `onStatusChange`. The [`Member.Status`][Member.Status] will be passed to the status change listener callback:

```java
member.onStatusChange(status -> {
  System.out.println(member.address() + " is now " + status);
});
```

## Cluster consistency guarantees
It's important to note the consistency guarantees when interacting with the [`Cluster`][Cluster] object. The state of the `Cluster` represents the state from the perspective of the local server, but not necessarily of the cluster as a whole. Different servers may perceive the state of the cluster to be different at any given time. But because of this, Copycat takes steps to ensure that changes to the structure of the cluster - adding, removing, promoting, or demoting members - can only be done on a consistent view of the cluster.

To ensure consistency when operating on the cluster, Copycat does a version check when submitting configuration changes to the leader. Effectively, this amounts to an atomic check-and-set operation. When the leader receives a configuration change request from any node, if the request was made on an old version of the configuration, the configuration change will be rejected and the [`CompletableFuture`][CompletableFuture] will be completed with a `ConfigurationException`.

```java
Address address = new Address("123.456.789.0", 5000);
server.cluster().member(address).promote(Member.Type.ACTIVE).whenComplete((result, error) -> {
  if (error != null && error instanceof ConfigurationException) {
    // Attempted to promote the member on an old version of the cluster configuration.
    // The member may have already been promoted.
  }
}
});
```

Any attempt to reconfigure the cluster may fail with a `ConfigurationException`. The cluster state will be updated prior to the failure of the reconfiguration attempt. In the event of such a failure, users should perform any retries first by evaluating the updated state of the cluster to ensure the reconfiguration is still valid. For instance, if promoting a member to `ACTIVE`, check to determine that the member is not already `ACTIVE` and the condition that led to the decision to promote the member is still valid.

{% include common-links.html %}