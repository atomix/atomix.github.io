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
    <version>3.0.0-rc5</version>
  </dependency>
</dependencies>
```

Additionally, most clusters are configured with a set of partition groups. The partition groups that are used depend on the consistency, fault-tolerance, and persistence requirements of the system. Different use cases may require different dependencies. But packaged with Atomix are several protocol implementations:
* `atomix-raft` - `RaftPartitionGroup` and `MultiRaftProtocol`
* `atomix-primary-backup` - `PrimaryBackupPartitionGroup` and `MultiPrimaryProtocol`
* `atomix-gossip` - `AntiEntropyProtocol` and `CrdtProtocol`

```xml
<dependencies>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix</artifactId>
    <version>3.0.0-rc5</version>
  </dependency>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix-raft</artifactId>
    <version>3.0.0-rc5</version>
  </dependency>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix-primary-backup</artifactId>
    <version>3.0.0-rc5</version>
  </dependency>
  <dependency>
    <groupId>io.atomix</groupId>
    <artifactId>atomix-gossip</artifactId>
    <version>3.0.0-rc5</version>
  </dependency>
</dependencies>
```

### Using the Atomix Agent

A convenient alternative to the Java API is the [Atomix agent][agent]. An agent is a standalone Atomix node that behaves just like a Java node would but instead exposes a REST API for client interaction. Agents can be useful in configuring Atomix clusters in a client-server architecture or providing polyglot access to Atomix primitives.

To use the Atomix agent, first download and build Atomix with Maven:

```
mvn clean package
```

Once the project has been built, to run the agent, the `$ATOMIX_ROOT` environment variable must be set:

```
export ATOMIX_ROOT=./
```

The agent is run with the `bin/atomix-agent` script:

```
bin/atomix-agent -h
```

Use the `-h` option to see a list of options for the agent script.

When working with the agent, it's most convenient to provide a JSON or YAML configuration file. All builder configurations supported via the Java API are supported in configuration files as well. To configure the agent, create an `atomix.conf` file and define the cluster:

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

profiles.1 {
  type: consensus
  partitions: 3
  members: [member1, member2, member3]
  data-path: .data/consensus
}

profiles.2 {
  type: data-grid
  partitions: 32
}
```

{:.callout .callout-info}
The Java API supports configuration files as well. To configure an `Atomix` instance with a configuration file, simply pass the file to the `Atomix` constructor.

Once the configuration file has been created, start the cluster by bootstrapping the configured nodes:

```
bin/atomix-agent -m member1 -a 10.192.19.181:5679
```

```
bin/atomix-agent -m member2 -a 10.192.19.182:5679
```

```
bin/atomix-agent -m member3 -a 10.192.19.183:5679
```

{% include common-links.html %}
