---
layout: user-manual
project: atomix
menu: user-manual
title: Installation and Setup
---

Atomix is packaged in a hierarchy of modules that allow users to depend only on those features they intend to use. Almost all users will want to use the Atomix core module, which is identified by the `atomix` artifact ID:

```xml
<dependencies>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix</artifactId>
    <version>{{ site.version }}</version>
  </dependency>
</dependencies>
```

Additionally, most clusters are configured with a set of partition groups. The partition groups that are used depend on the consistency, fault-tolerance, and persistence requirements of the system. Different use cases may require different dependencies. But packaged with Atomix are several protocol implementations:
* `atomix-raft` - `RaftPartitionGroup` and `MultiRaftProtocol`
* `atomix-primary-backup` - `PrimaryBackupPartitionGroup` and `MultiPrimaryProtocol`
* `atomix-log` - `LogPartitionGroup` and `DistributedLogProtocol`
* `atomix-gossip` - `AntiEntropyProtocol` and `CrdtProtocol`

```xml
<dependencies>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix</artifactId>
    <version>{{ site.version }}</version>
  </dependency>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix-raft</artifactId>
    <version>{{ site.version }}</version>
  </dependency>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix-log</artifactId>
    <version>{{ site.version }}</version>
  </dependency>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix-primary-backup</artifactId>
    <version>{{ site.version }}</version>
  </dependency>
</dependencies>
```

### Using the Java API

Atomix can be used either as a library or as a standalone service referred to as an agent. When using the Java API, simply configure an [`Atomix`][Atomix] instance using the builder pattern.

```java
Atomix atomix = Atomix.builder()
  .withMemberId("member1")
  .withNodeDiscovery(BootstrapDiscoveryProvider.builder()
    .withNodes(
      Node.builder()
        .withId("member1")
        .withAddress("10.192.19.181:5679")
        .build(),
      Node.builder()
        .withId("member2")
        .withAddress("10.192.19.182:5679")
        .build(),
      Node.builder()
        .withId("member3")
        .withAddress("10.192.19.183:5679")
        .build())
    .build())
  .withManagementGroup(RaftPartitionGroup.builder("system")
    .withNumPartitions(1)
    .withMembers("member1", "member2", "member3")
    .build())
  .withPartitionGroups(RaftPartitionGroup.builder("raft")
    .withPartitionSize(3)
    .withNumPartitions(3)
    .withMembers("member1", "member2", "member3")
    .build())
  .build();
```

{:.callout .callout-info}
[`Atomix`][Atomix] instances can also be configured with [configuration files][reference] by supplying a file name to the `builder` factory method.

Once the `Atomix` instance has been constructed, start the instance to join the Atomix cluster.

```java
atomix.start().join();
```

### Using the Atomix Agent

A convenient alternative to the Java API is the [Atomix agent][agent]. An agent is a standalone Atomix node that behaves just like a Java node would but instead exposes a REST API for client interaction. Agents can be useful in configuring Atomix clusters in a client-server architecture or providing polyglot access to Atomix primitives.

To use the Atomix agent, download the agent from the [downloads] page or from Maven Central:

```
curl -o atomix-dist-{{ site.version }}.tar.gz -XGET https://oss.sonatype.org/content/repositories/releases/io/atomix/atomix-dist/{{ site.version }}/atomix-dist-{{ site.version }}.tar.gz
```

Once the distribution has been downloaded, unpack the archive:

```
tar -xvf atomix-dist-{{ site.version }}.tar.gz
```

The agent is run with the `bin/atomix-agent` script:

```
./bin/atomix-agent -h
```

Use the `-h` option to see a list of options for the agent script.

When working with the agent, it's most convenient to provide a JSON or YAML configuration file. All builder configurations supported via the Java API are supported in configuration files as well. To configure the agent, modify the `/conf/atomix.conf` file to setup the cluster:

`atomix.conf`

```
cluster.discovery {
  type: bootstrap
  nodes.1 {
    id: member1
    address: "10.192.19.181:5679"
  }
  nodes.2 {
    id: member2
    address: "10.192.19.182:5679"
  }
  nodes.3 {
    id: member3
    address: "10.192.19.183:5679"
  }
}

managementGroup {
  type: raft
  partitions: 1
  members: [member1, member2, member3]
}

partitionGroups.raft {
  type: raft
  partitionSize: 3
  partitions: 3
  members: [member1, member2, member3]
}
```

{:.callout .callout-info}
See the [configuration reference][reference] for a full list of configuration options.

Once the configuration file has been created, start the cluster by bootstrapping the configured nodes:

```
./bin/atomix-agent -m member1 -a 10.192.19.181:5679
```

```
./bin/atomix-agent -m member2 -a 10.192.19.182:5679
```

```
./bin/atomix-agent -m member3 -a 10.192.19.183:5679
```

{% include common-links.html %}
