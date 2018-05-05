---
layout: user-manual
project: atomix
menu: user-manual
title: Custom Primitives
---

Atomix [primitives][primitives] implement a common, pluggable API that can be used by users to provide custom primitives. Primitives are modelled as replicated state machines with several key components:
* [Primitive type][primitive-type]
* [Replicated state machine][primitive-service]
* [Client proxies][primitive-proxy]
* [Configuration][primitive-configuration]
* [REST API][primitive-rest-api]

Custom primitives can be constructed via the Java API using the generic `primitiveBuilder` method on the [`Atomix`][Atomix] class:

```java
MyPrimitive myPrimitive = atomix.primitiveBuilder("my-primitive", MyPrimitive.Type.instance())
  .withProtocol(MultiPrimaryProtocol.builder()
    .withReplication(Replication.ASYNCHRONOUS)
    .withNumBackups(2)
    .build())
  .build();
```

{% include common-links.html %}
