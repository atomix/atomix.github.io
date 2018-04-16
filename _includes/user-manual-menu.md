<span class="user-guide-menu-header"><a href="/user-manual/introduction"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</a></span>

* [Installation](#installation)
  * [Embedded Usage](#embedded-usage)
    * [Primitives](#primitives)
    * [Transports](#transports)
  * [Standalone Agent](#standalone-usage)
    * [Bootstrapping a Standlone Cluster](#bootstrapping-a-standalone-cluster)
    * [Adding a Node to a Standalone Cluster](#adding-a-node-to-a-standalone-cluster)
    * [Configuring a Standlone Server](#configuring-a-standalone-server)
* [Clustering](clustering)
  * [Anatomy of a Cluster](#anatomy-of-a-cluster)
  * [Determining the Size of a Cluster](#determining-the-size-of-a-cluster)
  * [Bootstrapping a Cluster](#bootstrapping-a-cluster)
  * [Joining a Cluster](#joining-a-cluster)
  * [Node Types](#node-types)
    * [Core nodes](#core-nodes)
    * [Data nodes](#data-nodes)
    * [Client nodes](#client-nodes)
* [Comparisons](comparisons)
  * [Something Unique](#something-unique)
  * [ZooKeeper](#zookeeper)
  * [Hazelcast](#hazelcast)

<span class="user-guide-menu-header"><a href="/user-manual/concepts"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</a></span>

* [Consistency](consistency)
  * [CAP Theorem](#cap-theorem)
  * [Consistency Model](#consistency-model)
  * [Consistency Levels](#consistency-levels)
    * [Write Consistency Levels](#write-consistency-levels)
    * [Read Consistency Levels](#read-consistency-levels)
  * [Event Consistency](#event-consistency)
  * [Cross-primitive Consistency](#cross-primitive-consistency)
* [Fault Tolerance](fault-tolerance)
  * [Node Failures](#node-failures)
  * [Leader Failures](#leader-failures)
  * [Network Partitions](#network-partitions)
* [Threading Model](threading-model)

<span class="user-guide-menu-header"><a href="/user-manual/cluster-management"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</a></span>

* [Cluster formation](#cluster-formation)
  * [Consensus configuration](#consensus-configuration)
  * [IP ranges](#ip-ranges)
  * [Multicast discovery](#multicast-discovery)
* [Cluster membership](#cluster-membership)
* [Cluster events](#cluster-events)
* [Partition groups](#partition-groups)
  * [Raft partition groups](#raft-partition-groups)
  * [Primary-backup partition groups](#primary-backup-partition-groups)
* [Member groups](#member-groups)

<span class="user-guide-menu-header"><a href="/user-manual/cluster-communication"><img src="/assets/img/icons/communication.svg" class="cluster-communication"> Cluster Communication</a></span>

* [Direct Messaging](#direct-messaging)
* [Publish-subscribe Messaging](#publish-subscribe-messaging)

<span class="user-guide-menu-header"><a href="/user-manual/primitives"><img src="/assets/img/icons/primitives.svg" class="primitives"> Primitives</a></span>

* [Overview](primitives)
* [ConsistentMap](#consistentmap)
* [ConsistentMultimap](#consistentmultimap)
* [DistributedSet](#distributedset)
* [AtomicValue](#atomicvalue)
* [AtomicCounter](#atomiccounter)
* [DocumentTree](#documenttree)
* [DistributedLock](#distributedlock)
* [LeaderElection](#leaderelection)
* [WorkQueue](#workqueue)

<span class="user-guide-menu-header"><a href="/user-manual/agent"><img src="/assets/img/icons/agent.png" class="agent"> Agent</a></span>

* [Overview](#overview)

<span class="user-guide-menu-header"><a href="/user-manual/rest"><img src="/assets/img/icons/rest.svg" class="rest"> REST API</a></span>

* [Overview](#overview)

<span class="user-guide-menu-header"><a href="/user-manual/cli"><img src="/assets/img/icons/cli.svg" class="cli"> CLI</a></span>

* [Overview](#overview)

<span class="user-guide-menu-header"><img src="/assets/img/icons/operations.svg" class="operations"> Operation</span>

* [Configuration](configuration)

<span class="user-guide-menu-header"><a href="/user-manual/architecture"><img src="/assets/img/icons/architecture.svg" class="architecture"> Architecture</a></span>

* [Cluster Architecture](#cluster-architecture)
* [Cluster Communication](#cluster-communication)
* [Partition Groups](#partition-groups)
* [Primitive Protocols](#primitive-protocols)
  * [Consensus](#consensus)
  * [Primary-backup](#primary-backup)
* [Distributed Primitives](#distributed-primitives)