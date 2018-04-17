<span class="user-guide-menu-header"><a href="/user-manual/introduction"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</a></span>

* [What is Atomix](/user-manual/introduction#what-is-atomix)
* [Features](/user-manual/introduction#features)
* [Setup and Installation](/user-manual/introduction#setup-and-installation)
* [Comparisons](/user-manual/introduction#comparisons)
  * [Something Unique](/user-manual/introduction#something-unique)
  * [ZooKeeper](/user-manual/introduction#zookeeper)
  * [Hazelcast](/user-manual/introduction#hazelcast)

<span class="user-guide-menu-header"><a href="/user-manual/concepts"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</a></span>

* [Cluster Architecture](/user-manual/concepts#cluster-architecture)
  * [Core Nodes](/user-manual/concepts#core-nodes)
  * [Data Nodes](/user-manual/concepts#data-nodes)
  * [Client Nodes](/user-manual/concepts#client-nodes)
  * [Partition Groups](/user-manual/concepts#partition-groups)
* [Distributed Primitives](/user-manual/concepts#distributed-primitives)
  * [Data Primitives](/user-manual/concepts#data-primitives)
  * [Coordination Primitives](/user-manual/concepts#coordination-primitives)
  * [Primitive Protocols](/user-manual/concepts#primitive-protocols)
* [Consistency](/user-manual/concepts#consistency)
  * [CAP Theorem](/user-manual/concepts#cap-theorem)
  * [Consistency Models](/user-manual/concepts#consistency-models)
  * [Event Consistency](/user-manual/concepts#event-consistency)
  * [Cross-primitive Consistency](/user-manual/concepts#cross-primitive-consistency)
* [Fault Tolerance](/user-manual/concepts#fault-tolerance)
  * [Node Failures](/user-manual/concepts#node-failures)
  * [Network Partitions](/user-manual/concepts#network-partitions)
* [Threading Model](/user-manual/concepts#threading-model)

<span class="user-guide-menu-header"><a href="/user-manual/cluster-management"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</a></span>

* [Bootstrapping a Cluster](/user-manual/cluster-management#bootstrapping-a-cluster)
  * [Node Objects](/user-manual/cluster-management#node-objects)
* [Member Discovery](/user-manual/cluster-management#member-discovery)
  * [IP Ranges](/user-manual/cluster-management#ip-ranges)
  * [Multicast Discovery](/user-manual/cluster-management#multicast-discovery)
* [Partition Groups](/user-manual/cluster-management#partition-groups)
  * [Raft Partition Groups](/user-manual/cluster-management#raft-partition-groups)
  * [Primary-Backup Partition Groups](/user-manual/cluster-management#primary-backup-partition-groups)
* [Member Groups](/user-manual/cluster-management#member-groups)
  * [Rack Awareness](/user-manual/cluster-management#rack-awareness)
* [Reading Cluster Membership](/user-manual/cluster-management#reading-cluster-membership)
* [Listening for Membership Changes](/user-manual/cluster-management#listening-for-membership-changes)
* [Failure Detection](/user-manual/cluster-management#failure-detection)

<span class="user-guide-menu-header"><a href="/user-manual/cluster-communication"><img src="/assets/img/icons/communication.svg" class="cluster-communication"> Cluster Communication</a></span>

* [Direct Messaging](/user-manual/cluster-communication#direct-messaging)
* [Publish-subscribe Messaging](/user-manual/cluster-communication#publish-subscribe-messaging)

<span class="user-guide-menu-header"><a href="/user-manual/primitives"><img src="/assets/img/icons/primitives.svg" class="primitives"> Primitives</a></span>

* [Overview](/user-manual/primitives#overview)
* [Primitive Protocols](/user-manual/primitives#primitive-protocols)
  * [RaftProtocol](/user-manual/primitives#raftprotocol)
  * [MultiPrimaryProtocol](/user-manual/primitives#multiprimaryprotocol)
* [ConsistentMap](/user-manual/primitives#consistentmap)
* [ConsistentMultimap](/user-manual/primitives#consistentmultimap)
* [DistributedSet](/user-manual/primitives#distributedset)
* [AtomicValue](/user-manual/primitives#atomicvalue)
* [AtomicCounter](/user-manual/primitives#atomiccounter)
* [DocumentTree](/user-manual/primitives#documenttree)
* [DistributedLock](/user-manual/primitives#distributedlock)
* [LeaderElection](/user-manual/primitives#leaderelection)
* [WorkQueue](/user-manual/primitives#workqueue)

<span class="user-guide-menu-header"><a href="/user-manual/custom-primitives"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</a></span>

* [Defining the Primitive Type](/user-manual/custom-primitives#defining-the-primitive-type)
* [Creating the State Machine](/user-manual/custom-primitives#creating-the-state-machine)
  * [Defining Primitive Operations](/user-manual/custom-primitives#defining-primitive-operations)
    * [Commands](/user-manual/custom-primitives#commands)
    * [Queries](/user-manual/custom-primitives#queries)
  * [Handling Snapshots](/user-manual/custom-primitives#handling-snapshots)
* [Creating a Proxy](/user-manual/custom-primitives#creating-a-proxy)
* [Defining the Primitive Configuration](/user-manual/custom-primitives#defining-the-primitive-configuration)
* [Supplying a Primitive Builder](/user-manual/custom-primitives#supplying-a-primitive-builder)
* [Supporting REST API Access](/user-manual/custom-primitives#supporting-rest-api-access)

<span class="user-guide-menu-header"><a href="/user-manual/configuration"><img src="/assets/img/icons/configuration.svg" class="configuration"> Configuration</a></span>

* [Cluster Configuration](/user-manual/configuration#cluster-configuration)
* [Partition Group Configuration](/user-manual/configuration#partition-group-configuration)
* [Primitive Configurations](/user-manual/configuration#primitive-configuration)

<span class="user-guide-menu-header"><a href="/user-manual/agent"><img src="/assets/img/icons/agent.png" class="agent"> Agent</a></span>

* [Starting the Agent](/user-manual/agent#starting-the-agent)
* [Client Agents](/user-manual/agent#client-agents)

<span class="user-guide-menu-header"><a href="/user-manual/rest"><img src="/assets/img/icons/rest.svg" class="rest"> REST API</a></span>

* [Managing the Cluster](/user-manual/rest#managing-the-cluster)
* [Sending Messages](/user-manual/rest#sending-messages)
* [Publishing Events](/user-manual/rest#publishing-events)
* [Operating on Distributed Primitives](/user-manual/rest#operating-on-distributed-primitives)

<span class="user-guide-menu-header"><a href="/user-manual/cli"><img src="/assets/img/icons/cli.svg" class="cli"> CLI</a></span>

* [Building the CLI](/user-manual/cli#building-the-cli)
* [Running the CLI](/user-manual/cli#running-the-cli)

<span class="user-guide-menu-header"><a href="/user-manual/test"><img src="/assets/img/icons/test.svg" class="test"> Test Framework</a></span>

* [Setting Up the Test Framework](/user-manual/test#setting-up-the-test-framework)
* [Bootstrapping a Test Cluster](/user-manual/test#bootstrapping-a-test-cluster)
* [Adding Nodes](/user-manual/test#adding-nodes)
* [Disrupting Nodes](/user-manual/test#disrupting-nodes)
  * [Killing Nodes](/user-manual/test#killing-nodes)
  * [Stress Testing Nodes](/user-manual/test#stress-testing-nodes)
* [Disrupting the Network](/user-manual/test#disrupting-the-network)
  * [Injecting Latency into the Network](/user-manual/test#injecting-latency-into-the-network)
  * [Creating Network Partitions](/user-manual/test#creating-network-partitions)
* [Running Tests](/user-manual/test#running-tests)
* [Writing New Tests](/user-manual/test#writing-new-tests)

<span class="user-guide-menu-header"><a href="/user-manual/architecture"><img src="/assets/img/icons/architecture.svg" class="architecture"> Architecture</a></span>

* [Cluster Communication](/user-manual/architecture#cluster-communication)
* [Group Membership](/user-manual/architecture#group-membership)
* [Partition Groups](/user-manual/architecture#partition-groups)
* [Primitive Protocols](/user-manual/architecture#primitive-protocols)
  * [Raft](/user-manual/architecture#raft)
  * [Primary-backup](/user-manual/architecture#primary-backup)