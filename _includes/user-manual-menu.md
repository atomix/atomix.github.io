<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/introduction"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</a></span>

* [What is Atomix](/docs/latest/user-manual/introduction#what-is-atomix)
* [Features](/docs/latest/user-manual/introduction#features)
* [Setup and Installation](/docs/latest/user-manual/introduction#setup-and-installation)
* [Comparisons](/docs/latest/user-manual/introduction#comparisons)
  * [Something Unique](/docs/latest/user-manual/introduction#something-unique)
  * [ZooKeeper](/docs/latest/user-manual/introduction#zookeeper)
  * [Hazelcast](/docs/latest/user-manual/introduction#hazelcast)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/concepts"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</a></span>

* [Cluster Architecture](/docs/latest/user-manual/concepts#cluster-architecture)
  * [Core Nodes](/docs/latest/user-manual/concepts#core-nodes)
  * [Data Nodes](/docs/latest/user-manual/concepts#data-nodes)
  * [Client Nodes](/docs/latest/user-manual/concepts#client-nodes)
  * [Partition Groups](/docs/latest/user-manual/concepts#partition-groups)
* [Distributed Primitives](/docs/latest/user-manual/concepts#distributed-primitives)
  * [Data Primitives](/docs/latest/user-manual/concepts#data-primitives)
  * [Coordination Primitives](/docs/latest/user-manual/concepts#coordination-primitives)
  * [Primitive Protocols](/docs/latest/user-manual/concepts#primitive-protocols)
* [Consistency](/docs/latest/user-manual/concepts#consistency)
  * [CAP Theorem](/docs/latest/user-manual/concepts#cap-theorem)
  * [Consistency Models](/docs/latest/user-manual/concepts#consistency-models)
  * [Event Consistency](/docs/latest/user-manual/concepts#event-consistency)
  * [Cross-primitive Consistency](/docs/latest/user-manual/concepts#cross-primitive-consistency)
* [Fault Tolerance](/docs/latest/user-manual/concepts#fault-tolerance)
  * [Node Failures](/docs/latest/user-manual/concepts#node-failures)
  * [Network Partitions](/docs/latest/user-manual/concepts#network-partitions)
* [Threading Model](/docs/latest/user-manual/concepts#threading-model)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/cluster-management"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</a></span>

* [Bootstrapping a Cluster](/docs/latest/user-manual/cluster-management#bootstrapping-a-cluster)
  * [Node Objects](/docs/latest/user-manual/cluster-management#node-objects)
* [Member Discovery](/docs/latest/user-manual/cluster-management#member-discovery)
  * [IP Ranges](/docs/latest/user-manual/cluster-management#ip-ranges)
  * [Multicast Discovery](/docs/latest/user-manual/cluster-management#multicast-discovery)
* [Partition Groups](/docs/latest/user-manual/cluster-management#partition-groups)
  * [Raft Partition Groups](/docs/latest/user-manual/cluster-management#raft-partition-groups)
  * [Primary-Backup Partition Groups](/docs/latest/user-manual/cluster-management#primary-backup-partition-groups)
* [Member Groups](/docs/latest/user-manual/cluster-management#member-groups)
  * [Rack Awareness](/docs/latest/user-manual/cluster-management#rack-awareness)
* [Reading Cluster Membership](/docs/latest/user-manual/cluster-management#reading-cluster-membership)
* [Listening for Membership Changes](/docs/latest/user-manual/cluster-management#listening-for-membership-changes)
* [Failure Detection](/docs/latest/user-manual/cluster-management#failure-detection)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/cluster-communication"><img src="/assets/img/icons/communication.svg" class="cluster-communication"> Cluster Communication</a></span>

* [Direct Messaging](/docs/latest/user-manual/cluster-communication#direct-messaging)
* [Publish-subscribe Messaging](/docs/latest/user-manual/cluster-communication#publish-subscribe-messaging)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/primitives"><img src="/assets/img/icons/primitives.svg" class="primitives"> Primitives</a></span>

* [Overview](/docs/latest/user-manual/primitives#overview)
* [Primitive Protocols](/docs/latest/user-manual/primitives#primitive-protocols)
  * [RaftProtocol](/docs/latest/user-manual/primitives#raftprotocol)
  * [MultiPrimaryProtocol](/docs/latest/user-manual/primitives#multiprimaryprotocol)
* [ConsistentMap](/docs/latest/user-manual/primitives#consistentmap)
* [ConsistentMultimap](/docs/latest/user-manual/primitives#consistentmultimap)
* [DistributedSet](/docs/latest/user-manual/primitives#distributedset)
* [AtomicValue](/docs/latest/user-manual/primitives#atomicvalue)
* [AtomicCounter](/docs/latest/user-manual/primitives#atomiccounter)
* [DocumentTree](/docs/latest/user-manual/primitives#documenttree)
* [DistributedLock](/docs/latest/user-manual/primitives#distributedlock)
* [LeaderElection](/docs/latest/user-manual/primitives#leaderelection)
* [WorkQueue](/docs/latest/user-manual/primitives#workqueue)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/custom-primitives"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</a></span>

* [Defining the Primitive Type](/docs/latest/user-manual/custom-primitives#defining-the-primitive-type)
* [Creating the State Machine](/docs/latest/user-manual/custom-primitives#creating-the-state-machine)
  * [Defining Primitive Operations](/docs/latest/user-manual/custom-primitives#defining-primitive-operations)
    * [Commands](/docs/latest/user-manual/custom-primitives#commands)
    * [Queries](/docs/latest/user-manual/custom-primitives#queries)
  * [Handling Snapshots](/docs/latest/user-manual/custom-primitives#handling-snapshots)
* [Creating a Proxy](/docs/latest/user-manual/custom-primitives#creating-a-proxy)
* [Defining the Primitive Configuration](/docs/latest/user-manual/custom-primitives#defining-the-primitive-configuration)
* [Supplying a Primitive Builder](/docs/latest/user-manual/custom-primitives#supplying-a-primitive-builder)
* [Supporting REST API Access](/docs/latest/user-manual/custom-primitives#supporting-rest-api-access)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/configuration"><img src="/assets/img/icons/configuration.svg" class="configuration"> Configuration</a></span>

* [Cluster Configuration](/docs/latest/user-manual/configuration#cluster-configuration)
* [Partition Group Configuration](/docs/latest/user-manual/configuration#partition-group-configuration)
* [Primitive Configurations](/docs/latest/user-manual/configuration#primitive-configurations)
* [Serializer Configurations](/docs/latest/user-manual/configuration#serializer-configurations)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/serialization"><img src="/assets/img/icons/serialization.svg" class="serialization"> Serialization</a></span>

* [Configuring a Namespace](/docs/latest/user-manual/serialization#configuring-a-namepsace)
* [Registering Custom Serializers](/docs/latest/user-manual/serialization#registering-custom-serializers)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/agent"><img src="/assets/img/icons/agent.png" class="agent"> Agent</a></span>

* [Starting the Agent](/docs/latest/user-manual/agent#starting-the-agent)
* [Client Agents](/docs/latest/user-manual/agent#client-agents)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/rest"><img src="/assets/img/icons/rest.svg" class="rest"> REST API</a></span>

* [Managing the Cluster](/docs/latest/user-manual/rest#managing-the-cluster)
* [Sending Messages](/docs/latest/user-manual/rest#sending-messages)
* [Publishing Events](/docs/latest/user-manual/rest#publishing-events)
* [Operating on Distributed Primitives](/docs/latest/user-manual/rest#operating-on-distributed-primitives)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/cli"><img src="/assets/img/icons/cli.svg" class="cli"> CLI</a></span>

* [Building the CLI](/docs/latest/user-manual/cli#building-the-cli)
* [Running the CLI](/docs/latest/user-manual/cli#running-the-cli)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/test"><img src="/assets/img/icons/test.svg" class="test"> Test Framework</a></span>

* [Setting Up the Test Framework](/docs/latest/user-manual/test#setting-up-the-test-framework)
* [Bootstrapping a Test Cluster](/docs/latest/user-manual/test#bootstrapping-a-test-cluster)
* [Adding Nodes](/docs/latest/user-manual/test#adding-nodes)
* [Disrupting Nodes](/docs/latest/user-manual/test#disrupting-nodes)
  * [Killing Nodes](/docs/latest/user-manual/test#killing-nodes)
  * [Stress Testing Nodes](/docs/latest/user-manual/test#stress-testing-nodes)
* [Disrupting the Network](/docs/latest/user-manual/test#disrupting-the-network)
  * [Injecting Latency into the Network](/docs/latest/user-manual/test#injecting-latency-into-the-network)
  * [Creating Network Partitions](/docs/latest/user-manual/test#creating-network-partitions)
* [Running Tests](/docs/latest/user-manual/test#running-tests)
* [Writing New Tests](/docs/latest/user-manual/test#writing-new-tests)

<span class="user-guide-menu-header"><a href="/docs/latest/user-manual/architecture"><img src="/assets/img/icons/architecture.svg" class="architecture"> Architecture</a></span>

* [Cluster Communication](/docs/latest/user-manual/architecture#cluster-communication)
* [Group Membership](/docs/latest/user-manual/architecture#group-membership)
* [Partition Groups](/docs/latest/user-manual/architecture#partition-groups)
* [Primitive Protocols](/docs/latest/user-manual/architecture#primitive-protocols)
  * [Raft](/docs/latest/user-manual/architecture#raft)
  * [Primary-backup](/docs/latest/user-manual/architecture#primary-backup)