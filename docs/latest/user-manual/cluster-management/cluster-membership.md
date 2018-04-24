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

Collection<Member> members = atomix.membershipService().getMembers();
```

{:.callout .callout-info}
In order to access cluster membership information the `Atomix` instance must first be `start`ed.

Specific members can be accessed via getters on the `ClusterMembershipService`:

```java
Member fooMember = atomix.membershipService().getMember("foo");
```

## Member States

The membership service will store the set of all `PERSISTENT` members in the cluster and all available `EPHEMERAL` members. For persistent members, the state of the member can be read via the [`Member`][Member] object:

```java
Member.State fooState = atomix.membershipService().getMember("foo").getState();
```

Each member can be in one of only two states:
* `ACTIVE` indicates that the node is currently available or was available in the recent past
* `INACTIVE` indicates that a failure was detected

## Listening for Membership Changes

Users can react to changes in the cluster membership or to the state of members in the cluster. To listen for membership changes, add a listener to the `ClusterMembershipService`:

```java
atomix.membershipService().addListener(event -> {
  switch (event.type()) {
    ...
  }
});
```

When a member joins or leaves the cluster or a failure is detected, an event will be triggered and all registered listeners will be called with a [`ClusterMembershipEvent`][ClusterMembershipEvent]. The event `type()` indicates the type of state change that occurred and the [`Member`][Member] on which it occurred:
* `MEMBER_ADDED` indicates that a new member joined the cluster
* `MEMBER_REMOVED` indicates that a member left the cluster, either explicitly or via failure detection
* `MEMBER_ACTIVATED` indicates that a previously `INACTIVE` member's state was changed to `ACTIVE`
* `MEMBER_DEACTIVATED` indicates that a previously `ACTIVE` member's state was changed to `INACTIVE` due to failure detection

{% include common-links.html %}
