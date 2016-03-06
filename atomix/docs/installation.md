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

The simplest way to get up and running with Atomix, which we saw in the [Getting started][getting-started] guide, is to use the [atomix-all][atomix-all-mvn] artifact:

```xml
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix-all</artifactId>
  <version>{{ site.atomix-version }}</version>
</dependency>
```

`atomix-all` [bundles](https://github.com/atomix/atomix/blob/master/all/pom.xml#L29-L38) the core `atomix` dependency with a Netty based [Transport] implementation, `catalyst-netty`.

#### atomix

The [atomix][atomix-mvn] artifact provides APIs for creating core resources such as [variables], [collections], [groups] and more via the [AtomixClient] and [AtomixReplica] classes, along with custom, user-defined resources. It [bundles](https://github.com/atomix/atomix/blob/master/core/pom.xml#L20-L49) the `atomix-resource-manager` with the various core resource implementations.

If you're planning to use a different [Transport] implementation than the Netty transport, you can use the `atomix` artifact directly instead of `atomix-all`.

#### atomix-resource-manager

The [atomix-resource-manager][resource-manager-mvn] Maven artifact provides APIs for creating custom, user-defined resources via the [ResourceClient] class.

If you're planning to write a custom resource and do not need to use any of the core atomix resources, or if you only want to use a select few resources, you can use the `atomix-resource-manager` artifact directly along with the [Transport] and resource implementations of your choosing.

### Resources

Groups of Atomix resources are available for use individually. The Maven artifacts for individual resources include:

{% include modules.md %}

### Transports

Atomix requires a [Transport] implementation in order for clients and servers to communicate with each other:

#### catalyst-netty

The [catalyst-netty][catalyst-netty-mvn] artifact provides a high-performance Netty based [Transport] implementation which is ideal for most Atomix installations.

#### catalyst-local

The [catalyst-local][catalyst-local-mvn] artifact provides a [Transport] implementation that can be used for local, in-process communication for testing purposes.

## Standalone Usage

In addition to being embedded, Atomix can run as a standalone server. To run as a standalone server, create a [configuration file](https://github.com/atomix/atomix/blob/standalone/standalone/standalone-server/conf/example.properties) to describe your cluster, storage, and serialization settings. To run the server:

```
java -jar atomix-standalone-server.jar <conf_file>
```


[atomix-all-mvn]: http://search.maven.org/#artifactdetails%7Cio.atomix%7Catomix-all%7C{{ site.atomix-version }}%7Cjar
[atomix-mvn]: http://search.maven.org/#artifactdetails%7Cio.atomix%7Catomix%7C{{ site.atomix-version }}%7Cjar
[resource-manager-mvn]: http://search.maven.org/#artifactdetails%7Cio.atomix%7Catomix-resource-manager%7C{{ site.atomix-version }}%7Cjar
[catalyst-netty-mvn]: http://search.maven.org/#artifactdetails%7Cio.atomix.catalyst%7Ccatalyst-netty%7C{{ site.catalyst-version }}%7Cjar
[catalyst-local-mvn]: http://search.maven.org/#artifactdetails%7Cio.atomix.catalyst%7Ccatalyst-local%7C{{ site.catalyst-version }}%7Cjar

{% include common-links.html %}