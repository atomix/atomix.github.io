---
layout: docs
project: atomix
menu: docs
title: Installation
first-section: embedded-usage
---

{:.no-margin-top}
## Embedded Usage

The most common way of using Atomix is as an embedded library via the Atomix Maven artifacts. There are a few different artifacts to choose from depending on your needs:

#### atomix-all

The simplest way to get up and running with Atomix, which we saw in the [Getting Started][atomix-getting-started] guide, is to use the [atomix-all][atomix-all-mvn] artifact. It [bundles](https://github.com/atomix/atomix/blob/master/all/pom.xml#L29-L38) the core `atomix` dependency with a Netty based [Transport] implementation, `catalyst-netty`.

For most users, `atomix-all` is the only dependency you will need.

#### atomix

If you're planning to use a different [Transport] implementation than the Netty transport, use the `atomix` artifact along with your Transport.

The [atomix][atomix-mvn] artifact provides APIs for creating core resources such as [variables], [collections], [groups] and more via the [`AtomixClient`][AtomixClient] and [`AtomixReplica`][AtomixReplica] classes, along with custom, user-defined resources. It [bundles](https://github.com/atomix/atomix/blob/master/core/pom.xml#L20-L49) the `atomix-resource-manager` with the various core resource implementations.

#### atomix-resource-manager

If you do not need some or all of the core atomix resources, use use the `atomix-resource-manager` artifact along with the [`Transport`][Transport] and resource implementations of your choosing.

The [atomix-resource-manager][resource-manager-mvn] Maven artifact provides APIs for creating custom, user-defined resources via the [`ResourceClient`][ResourceClient] class.

### Resources

Groups of Atomix resources can be individually used in conjunction with the `atomix-resource-manager`. The Atomix resource artifacts along with the resources they include are:

{% include modules.md %}

### Transports

Atomix requires a [`Transport`][Transport] implementation in order for clients and servers to communicate with each other. Available transports include:

* `catalyst-netty` - The [catalyst-netty][catalyst-netty-mvn] artifact provides a high-performance Netty based [Transport] implementation which is ideal for most Atomix installations.
* `catalyst-local` - The [catalyst-local][catalyst-local-mvn] artifact provides a [`Transport`][Transport] implementation that can be used for local, in-process communication for testing purposes.

## Standalone Usage

In addition to being embedded, Atomix can run as a standalone server. The standalone server can be [downloaded][standalone-server-jar] from Maven central.

### Bootstrapping a Standalone Cluster

To bootstrap a standalone cluster, pass the `-bootstrap` flag when running the standalone server jar. Bootstrapping the standalone server without any additional arguments will bootstrap a single node cluster to which additional nodes can be added.

```java
java -jar atomix-standalone-server.jar 123.456.789.0:8700 -bootstrap
```

Alternatively, to bootstrap a multi-node cluster, pass a list of server addresses as arguments to the `-bootstrap` option:

```java
java -jar atomix-standalone-server.jar 123.456.789.0:8700 -bootstrap \
    123.456.789.0:8700 \
    123.456.789.1:8700 \
    123.456.789.2:8700
```

### Adding a Node to a Standalone Cluster

To add a node to an existing bootstrapped standalone cluster, use the `-join` flag when running the standalone server jar, passing a list of servers to which to join the node.

```java
java -jar atomix-standalone-server.jar 123.456.789.1:8700 -join 123.456.789.0:8700
```

### Configuring a Standalone Server

Replicas support a number of configuration options that are typically configurable via the [`AtomixReplica.Builder`][AtomixReplica.Builder] API. When running a standalone Atomix server, the same properties can be configured by passing a properties file as the `-config` to the server.

```
java -jar atomix-standalone-server.jar 123.456.789.1:8700 -bootstrap -config atomix.properties
```

{% include common-links.html %}

[standalone-server-jar]: http://search.maven.org/remotecontent?filepath=io/atomix/atomix-standalone-server/{{ site.atomix-version }}/atomix-standalone-server-{{ site.atomix-version }}-shaded.jar