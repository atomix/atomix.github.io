---
layout: user-manual
project: atomix
menu: user-manual
title: Member Discovery
---

Configuring Atomix clusters can be tedious. It would be much more convenient if cluster membership could be automatically discovered. Atomix provides mechanisms for automatic discovery of cluster membership.

### Multicast Discovery

Atomix supports dynamic discovery of `EPHEMERAL` group members via multicast. Multicast member discovery can be enabled via the `AtomixCluster` builder:

```java
AtomixCluster cluster = AtomixCluster.builder()
  .withLocalMember(Member.ephemeral("member1"))
  .withMulticastEnabled()
  .build();
```

An optional multicast [`Address`][Address] can also be provided via `withMulticastAddress(Address)`.

```java
AtomixCluster cluster = AtomixCluster.builder()
  .withLocalMember(Member.ephemeral("member1"))
  .withMulticastEnabled()
  .withMulticastAddress("230.0.0.1:54321")
  .build();
```

Finally, multicast can be enabled via the JSON/YAML configuration:

```
multicast-enabled: true
multicast-address: 230.0.0.1:54321
```

When multicast is enabled, the instance will broadcast the local member's information at startup and periodically thereafter. Multicast is used strictly for initial identification of ephemeral nodes. Once a node has been discovered via multicast, it will be connected over TCP and the normal failure detection mechanisms will take over.

{% include common-links.html %}
