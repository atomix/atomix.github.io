---
layout: user-manual
project: atomix
menu: user-manual
title: Primitive Protocols
---

Atomix primitives are stored and replicated simply based on the protocol implemented by the partition group to which they're assigned. Each primitive can be stored in either a Raft partition group or a primary-backup partition group, and the behavior of each specific protocol can be defined in the primitive protocol configuration:

```java
DistributedSet<String> set = atomix.setBuilder("my-set")
  .withProtocol(MultiPrimaryProtocol.builder("data")
    .withNumBackups(2)
    .withReplication(Replication.ASYNCHRONOUS)
    .build())
  .build();
```

The partition group and protocol with which a primitive is replicated is defined simply by providing a `PrimitiveProtocol` instance to the primitive builder. The protocol defines the partition group within which the primitive is replicated as well as the behavior of the specific protocol in replication.

The protocol configuration can also be provided in the primitive configuration:

```hocon
primitives.my-set {
  type: set
  protocol {
    type: multi-primary
    backups: 2
    replication: asynchronous
  }
}
```

```java
DistributedSet<String> set = atomix.getSet("my-set");
```

{% include common-links.html %}
