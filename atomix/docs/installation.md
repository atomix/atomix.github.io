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

The [atomix][atomix-mvn] artifact provides APIs for creating core resources such as [variables], [collections], [groups] and more via the [AtomixClient] and [AtomixReplica] classes, along with custom, user-defined resources. It [bundles](https://github.com/atomix/atomix/blob/master/core/pom.xml#L20-L49) the `atomix-resource-manager` with the various core resource implementations.

#### atomix-resource-manager

If you do not need some or all of the core atomix resources, use use the `atomix-resource-manager` artifact along with the [Transport] and resource implementations of your choosing.

The [atomix-resource-manager][resource-manager-mvn] Maven artifact provides APIs for creating custom, user-defined resources via the [ResourceClient] class.

### Resources

Groups of Atomix resources can be individually used in conjunction with the `atomix-resource-manager`. The Atomix resource artifacts along with the resources they include are:

{% include modules.md %}

### Transports

Atomix requires a [Transport] implementation in order for clients and servers to communicate with each other. Available transports include:

* `catalyst-netty` - The [catalyst-netty][catalyst-netty-mvn] artifact provides a high-performance Netty based [Transport] implementation which is ideal for most Atomix installations.
* `catalyst-local` - The [catalyst-local][catalyst-local-mvn] artifact provides a [Transport] implementation that can be used for local, in-process communication for testing purposes.

## Standalone Usage

In addition to being embedded, Atomix can run as a standalone server. Currently the standalone server binaries are not hosted, but can be built very quickly.

To build the standalone server, `git clone` and `mvn package` Atomix:

```
git clone https://github.com/atomix/atomix.git
cd atomix
mvn package -DskipTests=true
```

This will create a single binary with a self-contained Atomix server located at:

```
standalone/standalone-server/target/atomix-standalone-server.jar
```

To run the standalone server, create a [configuration] file to describe your cluster, storage, and serialization settings, and pass it into the jar:

```
java -jar atomix-standalone-server.jar <conf_file>
```

{% include common-links.html %}