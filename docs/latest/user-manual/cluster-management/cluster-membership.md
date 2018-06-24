---
layout: user-manual
project: atomix
menu: user-manual
title: Cluster Membership
---

Atomix provides a group membership API that allows users to access information about the members in the cluster and their availability. Cluster membership can be accessed via services exposed by both the [`Atomix`][Atomix] and [`AtomixCluster`][AtomixCluster] class.

## Getting the Set of Members in the Cluster

The cluster membership can be accessed via the [`ClusterMembershipService`][ClusterMembershipService]:

```java
Atomix atomix = Atomix.builder()
  ...
  .build();

atomix.start().join();

Collection<Member> members = atomix.getMembershipService().getMembers();
```

{:.callout .callout-info}
In order to access cluster membership information the `Atomix` instance must first be `start`ed.

Specific members can be accessed via getters on the `ClusterMembershipService`:

```java
Member fooMember = atomix.getMembershipService().getMember("foo");
```

## Member States

The state of the member can be read via the [`Member`][Member] object:

```java
Member.State fooState = atomix.getMembershipService().getMember("foo").getState();
```

Each member can be in one of only two states:
* `ACTIVE` indicates that the node is currently available or was available in the recent past
* `INACTIVE` indicates that a failure was detected

## Member Metadata

Each member in the cluster can also be replicated with metadata. This can be useful for sharing additional properties of a node. Metadata is a simple `Map<String, String>` that's monitored for changes:

```java
atomix.getMembershipService().getLocalMember().metadata().put("foo", "bar");
```

Note that only changes made on the local member will be replicated to other nodes.

## Listening for Membership Changes

Users can react to changes in the cluster membership or to the state of members in the cluster. To listen for membership changes, add a listener to the `ClusterMembershipService`:

```java
atomix.getMembershipService().addListener(event -> {
  switch (event.type()) {
    ...
  }
});
```

When a member joins or leaves the cluster or a failure is detected, an event will be triggered and all registered listeners will be called with a [`ClusterMembershipEvent`][ClusterMembershipEvent]. The event `type()` indicates the type of state change that occurred and the [`Member`][Member] on which it occurred:
* `MEMBER_ADDED` indicates that a new member joined the cluster
* `MEMBER_UPDATED` indicates that the member's metadata was updated
* `MEMBER_REMOVED` indicates that a member left the cluster, either explicitly or via failure detection

{% include common-links.html %}
