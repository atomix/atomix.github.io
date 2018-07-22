---
layout: user-manual
project: atomix
menu: user-manual
title: Member Discovery
---

Member discovery is central to the way Atomix forms new clusters and joins existing clusters. When an Atomix instance is started, the instance uses a configurable `NodeDiscoveryProvider` to locate peers with which to communicate and form a cluster. The provider is configured on the [`AtomixBuilder`][AtomixBuilder] or in the cluster configuration. Atomix provides several built-in discovery providers to help in forming clusters.

### Bootstrap Provider

The simplest way to form a cluster is by simply listing the nodes to which to connect. This can be done by using the `BootstrapDiscoveryProvider`.

```java
Atomix atomix = Atomix.builder()
  .withAddress("localhost:5000")
  .withMembershipProvider(BootstrapDiscoveryProvider.builder()
    .withNodes(
      Node.builder()
        .withId("member1")
        .withAddress("localhost:5001")
        .build(),
      Node.builder()
        .withId("member2")
        .withAddress("localhost:5002")
        .build(),
      Node.builder()
        .withId("member3")
        .withAddress("localhost:5003")
        .build())
    .build())

atomix.start().join();
```

When configuring the cluster in configuration files, the provider can be configured in the `discovery` configuration:

```hocon
cluster {
  address: "localhost:5000"
  disovery {
    type: bootstrap
    nodes.1 {
      id: member1
      address: "localhost:5001"
    }
    nodes.2 {
      id: member2
      address: "localhost:5002"
    }
    nodes.3 {
      id: member3
      address: "localhost:5003"
    }
  }
}
```

### Multicast Discovery

Multicast discovery can be used to dynamically locate members of the cluster. To enable multicast discovery, simple enable multicast on the Atomix instance:

```java
Atomix atomix = Atomix.builder()
  .withAddress("localhost:5000")
  .withMulticastEnabled()
  .build();
```

An optional multicast [`Address`][Address] can also be provided via `withMulticastAddress(Address)`.

```java
Atomix atomix = Atomix.builder()
  .withAddress("localhost:5000")
  .withMulticastEnabled()
  .withMulticastAddress("230.0.0.1:54321")
  .build();
```

Finally, multicast can be enabled via the HOCON/JSON configuration:

```
cluster.multicast-enabled: true
cluster.multicast-address: 230.0.0.1:54321
```

For more complex multicast configurations, a custom `MulticastDiscoveryProvider` can also be provided to Atomix:

```java
Atomix atomix = Atomix.builder()
  .withAddress("localhost:5000")
  .withMulticastEnabled()
  .withMembershipProvider(MulticastDiscoveryProvider.builder()
    .withBroadcastInterval(Duration.ofSeconds(1))
    .build())
  .build();
```

When multicast is enabled, the instance will broadcast the local member's information at startup and periodically thereafter. Multicast is used strictly for initial identification of ephemeral nodes. Once a node has been discovered via multicast, it will be connected over TCP and the normal failure detection mechanisms will take over.

{% include common-links.html %}
