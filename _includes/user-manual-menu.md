<span class="user-guide-menu-header"><a href="/user-manual/introduction"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</a></span>

* [What is Atomix](#what-is-atomix)
* [Features](#features)
* [Setup and Installation](#setup-and-installation)
* [Comparisons](#comparisons)
  * [Something Unique](#something-unique)
  * [ZooKeeper](#zookeeper)
  * [Hazelcast](#hazelcast)

<span class="user-guide-menu-header"><a href="/user-manual/concepts"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</a></span>

* [Cluster Architecture](#cluster-architecture)
  * [Core Nodes](#core-nodes)
  * [Data Nodes](#data-nodes)
  * [Client Nodes](#client-nodes)
  * [Partition Groups](#partition-groups)
* [Distributed Primitives](#distributed-primitives)
  * [Data Primitives](#data-primitives)
  * [Coordination Primitives](#coordination-primitives)
  * [Primitive Protocols](#primitive-protocols)
* [Consistency](#consistency)
  * [CAP Theorem](#cap-theorem)
  * [Consistency Models](#consistency-models)
  * [Event Consistency](#event-consistency)
  * [Cross-primitive Consistency](#cross-primitive-consistency)
* [Fault Tolerance](#fault-tolerance)
  * [Node Failures](#node-failures)
  * [Network Partitions](#network-partitions)
* [Threading Model](threading-model)

<span class="user-guide-menu-header"><a href="/user-manual/cluster-management"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</a></span>

* [Bootstrapping a Cluster](#bootstrapping-a-cluster)
  * [Node Objects](#node-objects)
* [Member Discovery](#member-discovery)
  * [IP Ranges](#ip-ranges)
  * [Multicast Discovery](#multicast-discovery)
* [Partition Groups](#partition-groups)
  * [Raft Partition Groups](#raft-partition-groups)
  * [Primary-Backup Partition Groups](#primary-backup-partition-groups)
* [Member Groups](#member-groups)
  * [Rack Awareness](#rack-awareness)
* [Reading Cluster Membership](#reading-cluster-membership)
* [Listening for Membership Changes](#listening-for-membership-changes)
* [Failure Detection](#failure-detection)

<span class="user-guide-menu-header"><a href="/user-manual/cluster-communication"><img src="/assets/img/icons/communication.svg" class="cluster-communication"> Cluster Communication</a></span>

* [Direct Messaging](#direct-messaging)
* [Publish-subscribe Messaging](#publish-subscribe-messaging)

<span class="user-guide-menu-header"><a href="/user-manual/primitives"><img src="/assets/img/icons/primitives.svg" class="primitives"> Primitives</a></span>

* [Overview](#overview)
* [Primitive Protocols](#primitive-protocols)
  * [RaftProtocol](#raftprotocol)
  * [MultiPrimaryProtocol](#multiprimaryprotocol)
* [ConsistentMap](#consistentmap)
* [ConsistentMultimap](#consistentmultimap)
* [DistributedSet](#distributedset)
* [AtomicValue](#atomicvalue)
* [AtomicCounter](#atomiccounter)
* [DocumentTree](#documenttree)
* [DistributedLock](#distributedlock)
* [LeaderElection](#leaderelection)
* [WorkQueue](#workqueue)

<span class="user-guide-menu-header"><a href="/user-manual/custom-primitives"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</a></span>

* [Defining the Primitive Type](#defining-the-primitive-type)
* [Creating the State Machine](#creating-the-state-machine)
  * [Defining Primitive Operations](#defining-primitive-operations)
    * [Commands](#commands)
    * [Queries](#queries)
  * [Handling Snapshots](#handling-snapshots)
* [Creating a Proxy](#creating-a-proxy)
* [Defining the Primitive Configuration](#defining-the-primitive-configuration)
* [Supplying a Primitive Builder](#supplying-a-primitive-builder)
* [Supporting REST API Access](#supporting-rest-api-access)

<span class="user-guide-menu-header"><img src="/assets/img/icons/configuration.svg" class="configuration"> Configuration</span>

* [Cluster Configuration](#cluster-configuration)
* [Partition Group Configuration](#partition-group-configuration)
* [Primitive Configurations](#primitive-configuration)

<span class="user-guide-menu-header"><a href="/user-manual/agent"><img src="/assets/img/icons/agent.png" class="agent"> Agent</a></span>

* [Starting the Agent](#starting-the-agent)
* [Client Agents](#client-agents)

<span class="user-guide-menu-header"><a href="/user-manual/rest"><img src="/assets/img/icons/rest.svg" class="rest"> REST API</a></span>

* [Managing the Cluster](#managing-the-cluster)
* [Sending Messages](#sending-messages)
* [Publishing Events](#publishing-events)
* [Operating on Distributed Primitives](#operating-on-distributed-primitives)

<span class="user-guide-menu-header"><a href="/user-manual/cli"><img src="/assets/img/icons/cli.svg" class="cli"> CLI</a></span>

* [Starting the CLI](#starting-the-cli)

<span class="user-guide-menu-header"><a href="/user-manual/test"><img src="/assets/img/icons/test.svg" class="test"> Test Framework</a></span>

* [Setting Up the Test Framework](#setting-up-the-test-framework)
* [Bootstrapping a Test Cluster](#bootstrapping-a-test-cluster)
* [Adding Nodes](#adding-nodes)
* [Disrupting Nodes](#disrupting-nodes)
  * [Killing Nodes](#killing-nodes)
  * [Stress Testing Nodes](#stress-testing-nodes)
* [Disrupting the Network](#disrupting-the-network)
  * [Injecting Latency into the Network](#injecting-latency-into-the-network)
  * [Creating Network Partitions](#creating-network-partitions)
* [Running Tests](#running-tests)
* [Writing New Tests](#writing-new-tests)

<span class="user-guide-menu-header"><a href="/user-manual/architecture"><img src="/assets/img/icons/architecture.svg" class="architecture"> Architecture</a></span>

* [Cluster Communication](#cluster-communication)
* [Group Membership](#group-membership)
* [Partition Groups](#partition-groups)
* [Primitive Protocols](#primitive-protocols)
  * [Raft](#raft)
  * [Primary-backup](#primary-backup)