---
layout: docs
project: atomix
menu: docs
title: Distributed Groups
pitch: Primitives for distributed group operations
---

The [DistributedGroup] resource provides an API for managing process or node groups in an Atomix cluster. The API can be used for group membership, service discovery, leader election, and remote scheduling and execution.

To create a distributed group, use the `DistributedGroup` class or constructor:

```java
DistributedGroup group = atomix.getGroup("my-group").get();
```

Each instance of `DistributedGroup` resource represents a single [GroupMember]. 

## Joining the Group

After creating a `DistributedGroup`, you can join the group by calling [join()][join]:

```java
group.join().thenAccept(member -> {
  System.out.println("Joined with member ID: " + member.id());
});
```

After joining a group, all existing members of the group may be notified via the [onJoin(Consumer)][on-join] event handlers:

```java 
group.onJoin(member -> {
  System.out.println(member.id() + " joined the group!");
});
```






When new members [join](#joining-the-group) a membership group, all existing members of the group may be [notified](#listening-for-membership-changes). Typically, in fault tolerant systems members remain in the group until they fail. When a member's session is disconnected from the cluster, remaining members of the group will again be notified that the member has left the cluster.

## Leaving the Group

[Leaving][leave] a group is similarly straightforward to joining:

```java
group.leave();
```

The [onLeave(Consumer)][on-leave] event handler can be used to learn when members leave the group:

```java 
group.onLeave(member -> {
  System.out.println(member.id() + " left the group!");
});
```

If a group member loses its session connection or otherwise fails, it will automatically be removed from the group and members will be notified.

## Listing Group Members

The [members()][members] list provides an up-to-date view of the group which will be automatically updated as members [join] and [leave] the group:

```java 
DistributedGroup group = atomix.getGroup("my-group").get();
for (GroupMember member : group.members()) {
  System.out.println("Member: " + member);
}
```

Users of the distributed group do not have to join the group to interact with it. For instance, while a server may participate in the group by joining it, a client may interact with the group just to get a list of available members. 

Once the group instance has been created, the group membership will be automatically updated each time the structure of the group changes. However, in the event that the client becomes disconnected from the cluster, it may not receive notifications of changes in the group structure.

## Leader election

The [DistributedGroup] resource facilitates leader election which can be used to coordinate a group by ensuring only a single member of the group performs some set of operations at any given time. Leader election is a core concept of membership groups, and because leader election is a low-overhead process, leaders are elected for each group automatically.

Leaders are elected using a fair policy. The first member to [join] a group will always become the initial group [leader]. Each unique leader in a group is associated with a [term]. The term is a globally unique, monotonically increasing token that can be used for fencing. Users can listen for changes in group terms and leaders with event listeners:

```java 
DistributedGroup group = atomix.getGroup("my-group").get();
group.election().onTerm(term -> {
  System.out.println("New term: " + term);
});

group.election().onElection(leader -> {
  System.out.println("Elected leader: " + leader);
});
```

The [term] is guaranteed to be incremented prior to the election of a new [leader], and only a single leader for any given term will ever be elected. Each instance of a group is guaranteed to see terms and leaders progress monotonically, and no two leaders can exist in the same term. In that sense, the terminology and constrains of leader election in Atomix borrow heavily from the Raft algorithm that underlies it.

While terms and leaders are guaranteed to progress in the same order from the perspective of all clients of the resource, Atomix cannot guarantee that two leaders cannot exist at any given time. The group state machine will make a best effort attempt to ensure that all clients are notified of a term or leader change prior to the change being completed, but arbitrary process pauses due to garbage collection and other effects can cause a client's session to expire and thus prevent the client from being updated in real time. Only clients that can maintain their session are guaranteed to have a consistent view of the membership, term, and leader in the group at any given time.

To guard against inconsistencies resulting from arbitrary process pauses, clients can use the monotonically increasing term for coordination and managing optimistic access to external resources.

## Consistent hashing

Membership groups also provide features to aid in supporting replication via consistent hashing and partitioning. When a group is created, users can configure the group to support a particular number of partitions and replication factor. Partitioning can aid in hashing resources to specific members of the group, and the replication factor builds on partitions to aid in identifying multiple members per partition.

By default, groups are created with a single partition and replication factor of 1. To configure the group for more partitions, provide a [DistributedGroup.Config][dgroup-config] when creating the resource.

```java
DistributedGroup.Config config = DistributedGroup.config()
  .withPartitions(32)
  .withVirtualNodes(200)
  .withReplicationFactor(3);
DistributedGroup group = atomix.getGroup("foo", config);
```

Partitions are managed within a consistent hash ring. For each member of the cluster, `100` virtual nodes are created on the ring by default. This helps spread reduce hotspotting within the ring. For each partition, the partition is mapped to a set of members of the group by hashing the partition to a point on the ring. Once hashed to a point on the ring, the `n` members following that point are the replicas for that partition.

Partition features are accessed via the group's [GroupPartitions] instance, which can be fetched via partitions().

```java
group.partitions().partition(1).members().forEach(m -> ...);
```

Partitions change over time while members are added to or removed from the group. Each time a member is added or removed, the group state machine will reassign the minimal number of partitions necessary to balance the cluster, and DistributedGroup instances will be notified and updated automatically. Atomix guarantees that when a new member [joins][join] a group, all partition information on all connected group instances will be updated before the join completes. Similarly, when a member [leaves][leave] the group, all partition information on all connected group instances are guaranteed to be updated before the operation completes.

Groups also aid in hashing objects to specific partitions and thus replicas within the group. Users can provide a [GroupPartitioner] class in the [DistributedGroup.Options][dgroup-options] when a group instance is first created on a node. The partitioner will be used to determine the partition to which an object maps within the current set of partitions when [GroupPartitions.partition(Object)][partition] is called.

```java
group.partitions().partition("foo").members().forEach(m -> m.send("foo"));
```

## Remote execution

Once members of the group, any member can [execute] immediate callbacks or [schedule] delayed callbacks to be run on any other member of the group. Submitting a [Runnable] callback to a member will cause it to be serialized and sent to that node to be executed.
   
```java
group.onJoin(member -> {
  String memberId = member.id();
  member.execute((Serializable & Runnable) () -> System.out.println("Executing on " + memberId));
});
```

{% include common-links.html %}

[leader]: http://atomix.io/atomix/api/latest/io/atomix/group/GroupElection.html#leader--
[join]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#join--
[leave]: http://atomix.io/atomix/api/latest/io/atomix/group/LocalGroupMember.html#leave--
[members]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#members--
[on-join]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#onJoin-java.util.function.Consumer-
[on-leave]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#onLeave-java.util.function.Consumer-
[term]: http://atomix.io/atomix/api/latest/io/atomix/group/GroupElection.html#term--
[partition]: http://atomix.io/atomix/api/latest/io/atomix/group/GroupPartitions.html#partition-java.lang.Object-
[dgroup-config]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.Config.html
[dgroup-options]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.Options.html
[execute]: http://atomix.io/atomix/api/latest/io/atomix/group/GroupScheduler.html#execute-java.lang.Runnable-
[schedule]: http://atomix.io/atomix/api/latest/io/atomix/group/GroupScheduler.html#schedule-java.time.Duration-java.lang.Runnable-