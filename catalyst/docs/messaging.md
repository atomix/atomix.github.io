---
layout: docs
project: catalyst
menu: docs
title: I/O & Serialization
pitch: Custom binary serialization, built for the JVM
first-section: messaging
---

## Transports

The [Transport][Transport] API provides an interface that generalizes the concept of asynchronous client-server messaging. `Transport` objects control the communication between all clients and servers throughout a Copycat cluster. Therefore, it is essential that all nodes in a cluster use the same transport.

The [NettyTransport][NettyTransport] is a TCP-based transport built on [Netty] 4.

```java
Transport transport = new NettyTransport();
```

{:.callout .callout-info}
For test cases, Copycat provides the [LocalTransport][LocalTransport] which mimics the behavior of a network based transport via threads and executors.

{% include common-links.html %}