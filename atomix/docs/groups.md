---
layout: docs
project: atomix
menu: docs
title: Distributed Groups
pitch: Primitives for distributed group operations
---

The [DistributedGroup] resources provides an asynchronous API for coordinating group membership across the cluster. Group membership can be used to track, for example, nodes in a cluster.

When new members [join](#joining-the-group) a membership group, all existing members of the group may be [notified](#listening-for-membership-changes). Typically, in fault tolerant systems members remain in the group until they fail. When a member's session is disconnected from the cluster, remaining members of the group will again be notified that the member has left the cluster.

To create a `DistributedGroup`, use the `Atomix.getGroup` method:

```java
DistributedGroup group = atomix.getGroup("my-group").get();
```

#### Joining the Group

Once a new `DistributedGroup` instance has been created, `join` the group:

```java
group.join().join();
```

When the member joins the group, a new [GroupMember] will be added and all existing group members will be notified. Atomix guarantees that existing members will be notified prior to the `join` operation's completion.

#### Leaving the Group

Typically, members remain part of the group until their session becomes disconnected from the cluster, at which time they will be automatically removed from the group and remaining members will be [notified](#listening-for-membership-changes). Alternatively, members can explicitly `leave` the group:

```java
group.leave().join();
```

#### Membership Events

To listen for group members joining the group, use the `onJoin` event listener:

```java
group.onJoin(member -> {
  System.out.println(member.id() + " joined the group");
});
```

When a new member joins the group, all existing members of the group are guaranteed to be notified of the new member prior to that member's join completing.

To listen for group members leaving the group, use the `onLeave` event listener:

```java
group.onLeave(member -> {
  System.out.println(member.id() + " left the group");
});
```

#### Leader Election

[Leader election](https://en.wikipedia.org/wiki/Leader_election) is a pattern commonly used in distributed systems to elect some leader from a set of processes as the primary point of access to some resource. Atomix's `DistributedGroup` handles the coordination of a leader and notifies processes when they become the leader.

Any member in a group can be elected leader, and indeed a leader is always elected for any group. To await the current leader being elected, use the `onElection` method of the `LocalGroupMember`:

```java
atomix.getGroup("group").thenAccept(group -> {
  group.join().thenAccept(member -> {
    member.onElection(term -> {
      System.out.println("Elected leader!");
    });
  });
});
```

Leaders can step down once they've been elected using the `resign` method:

```java
member.onElection(term -> {
  member.resign();
});
```

Additionally, any node can listen for a leader election:

```java
group.onElection(member -> {
  System.out.println(member.id() + " was elected leader!");
});
```

#### Remote Execution

Members in a [DistributedGroup] are represented as [GroupMember] objects. The `GroupMember` class provides an interface for remote execution on specific members of the group.

```java
group.onJoin(member -> {
  member.execute(() -> System.out.println("Printed on member " + member.id());
});
```

The `GroupMember` API supports two types of remote executions, *instant* and *scheduled*. To execute a remote callback immediately, use the `execute` method:

```java
member.execute(() -> System.out.println("Printed on member " + member.id());
```

To schedule a remote execution, use the `schedule` method, passing a `Duration` after which to execute the callback:

```java
member.schedule(Duration.ofSeconds(10), () -> System.out.println("Printed after 10 seconds on member " + member.id()));
```

#### Handling Failures

Atomix membership groups are fault-tolerant and will automatically remove a member and elect a new leader as necessary when a member node crashes or is partitioned. However, in some cases a member of the group can become partitioned from the cluster without crashing, and in that case it may not receive updates on membership changes or be notified when it is itself evicted from the group. Atomix provides a mechanism for detecting these types of communication issues through the `Resource.State` API. Each instance of a `DistributedGroup` on any node will track its ability to maintain communication with the rest of the cluster. In the event that the client cannot communicate with the rest of the cluter, the membership group's state will change to `SUSPENDED`.

```java
group.onStateChange(state -> {
  if (state == Resource.State.SUSPENDED) {
    ...
  }
});
```

When a resource's state is changed to `SUSPENDED`, clients should assume that any local group members have been evicted from the group. This means in the case of leader elections, if a local member has been elected leader, it should immediately `resign` when the resource becomes disconnected from the cluster.

```java
member.onElection(term -> {
  group.onStateChange(state -> {
    if (state == Resource.State.SUSPENDED) {
      member.resign();
    }
  });
});
```

If a client does not properly monitor the state of the resource and detect a `SUSPENDED` resource state - particularly for leaders - multiple leaders can potentially be elected at the same time. Users should assume that *any* change to the membership can occur while in the `SUSPENDED` state.

{% include common-links.html %}