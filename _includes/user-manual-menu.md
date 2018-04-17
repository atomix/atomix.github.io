<span class="user-guide-menu-header"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</span>

* [What is Atomix](/docs/latest/user-manual/introduction/what-is-atomix)
* [Features](/docs/latest/user-manual/introduction/features)
* [Installation and Setup](/docs/latest/user-manual/introduction/installation-and-setup)
* [Comparisons](/docs/latest/user-manual/introduction/comparisons)
  * [Something Unique](/docs/latest/user-manual/introduction/comparisons#something-unique)
  * [ZooKeeper](/docs/latest/user-manual/introduction/comparisons#zookeeper)
  * [Hazelcast](/docs/latest/user-manual/introduction/comparisons#hazelcast)

<span class="user-guide-menu-header"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</span>

* [Cluster Architecture](/docs/latest/user-manual/concepts/cluster-architecture)
  * [Core Nodes](/docs/latest/user-manual/concepts/cluster-architecture#core-nodes)
  * [Data Nodes](/docs/latest/user-manual/concepts/cluster-architecture#data-nodes)
  * [Client Nodes](/docs/latest/user-manual/concepts/cluster-architecture#client-nodes)
  * [Partition Groups](/docs/latest/user-manual/concepts/cluster-architecture#partition-groups)
* [Distributed Primitives](/docs/latest/user-manual/concepts/distributed-primitives)
  * [Data Primitives](/docs/latest/user-manual/concepts/distributed-primitives#data-primitives)
  * [Coordination Primitives](/docs/latest/user-manual/concepts/distributed-primitives#coordination-primitives)
  * [Primitive Protocols](/docs/latest/user-manual/concepts/distributed-primitives#primitive-protocols)
* [Consistency](/docs/latest/user-manual/concepts/consistency)
  * [CAP Theorem](/docs/latest/user-manual/concepts/consistency#cap-theorem)
  * [Consistency Models](/docs/latest/user-manual/concepts/consistency#consistency-models)
  * [Event Consistency](/docs/latest/user-manual/concepts/consistency#event-consistency)
  * [Cross-primitive Consistency](/docs/latest/user-manual/concepts/consistency#cross-primitive-consistency)
* [Fault Tolerance](/docs/latest/user-manual/concepts/fault-tolerance)
  * [Node Failures](/docs/latest/user-manual/concepts/fault-tolerance#node-failures)
  * [Network Partitions](/docs/latest/user-manual/concepts/fault-tolerance#network-partitions)
* [Threading Model](/docs/latest/user-manual/concepts/threading-model)

<span class="user-guide-menu-header"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</span>

* [Bootstrapping a Cluster](/docs/latest/user-manual/cluster-management/bootstrapping-a-cluster)
  * [Node Objects](/docs/latest/user-manual/cluster-management/bootstrapping-a-cluster#node-objects)
* [Member Discovery](/docs/latest/user-manual/cluster-management/member-discovery)
  * [IP Ranges](/docs/latest/user-manual/cluster-management/member-discovery#ip-ranges)
  * [Multicast Discovery](/docs/latest/user-manual/cluster-management/member-discovery#multicast-discovery)
* [Partition Groups](/docs/latest/user-manual/cluster-management/partition-groups)
  * [Raft Partition Groups](/docs/latest/user-manual/cluster-management/partition-groups#raft-partition-groups)
  * [Primary-Backup Partition Groups](/docs/latest/user-manual/cluster-management/partition-groups#primary-backup-partition-groups)
* [Member Groups](/docs/latest/user-manual/cluster-management/member-groups)
  * [Rack Awareness](/docs/latest/user-manual/cluster-management/member-groups#rack-awareness)
* [Cluster Membership](/docs/latest/user-manual/cluster-management/cluster-membership)
* [Failure Detection](/docs/latest/user-manual/cluster-management/failure-detection)

<span class="user-guide-menu-header"><img src="/assets/img/icons/communication.svg" class="cluster-communication"> Cluster Communication</span>

* [Direct Messaging](/docs/latest/user-manual/cluster-communication/direct-messaging)
* [Publish-subscribe Messaging](/docs/latest/user-manual/cluster-communication/publish-subscribe-messaging)

<span class="user-guide-menu-header"><img src="/assets/img/icons/primitives.svg" class="primitives"> Primitives</span>

* [Overview](/docs/latest/user-manual/primitives/overview)
* [Primitive Protocols](/docs/latest/user-manual/primitives/primitive-protocols)
  * [RaftProtocol](/docs/latest/user-manual/primitives/primitive-protocols#raftprotocol)
  * [MultiPrimaryProtocol](/docs/latest/user-manual/primitives/primitive-protocols#multiprimaryprotocol)
* [AtomicCounter](/docs/latest/user-manual/primitives/AtomicCounter)
* [AtomicCounterMap](/docs/latest/user-manual/primitives/AtomicCounterMap)
* [AtomicIdGenerator](/docs/latest/user-manual/primitives/AtomicIdGenerator)
* [AtomicValue](/docs/latest/user-manual/primitives/AtomicValue)
* [ConsistentMap](/docs/latest/user-manual/primitives/ConsistentMap)
* [ConsistentMultimap](/docs/latest/user-manual/primitives/ConsistentMultimap)
* [ConsistentTreeMap](/docs/latest/user-manual/primitives/ConsistentTreeMap)
* [DistributedLock](/docs/latest/user-manual/primitives/DistributedLock)
* [DistributedSet](/docs/latest/user-manual/primitives/DistributedSet)
* [DocumentTree](/docs/latest/user-manual/primitives/DocumentTree)
* [LeaderElection](/docs/latest/user-manual/primitives/LeaderElection)
* [WorkQueue](/docs/latest/user-manual/primitives/WorkQueue)

<span class="user-guide-menu-header"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</span>

* [Defining the Primitive Type](/docs/latest/user-manual/custom-primitives/primitive-type)
* [Creating the State Machine](/docs/latest/user-manual/custom-primitives/primitive-service)
  * [Defining Primitive Operations](/docs/latest/user-manual/custom-primitives/primitive-service#defining-primitive-operations)
    * [Commands](/docs/latest/user-manual/custom-primitives/primitive-service#commands)
    * [Queries](/docs/latest/user-manual/custom-primitives/primitive-service#queries)
  * [Handling Snapshots](/docs/latest/user-manual/custom-primitives/primitive-service#handling-snapshots)
* [Creating a Proxy](/docs/latest/user-manual/custom-primitives/primitive-proxy)
* [Defining the Primitive Configuration](/docs/latest/user-manual/custom-primitives/primitive-configuration)
* [Supplying a Primitive Builder](/docs/latest/user-manual/custom-primitives/primitive-builder)
* [Supporting REST API Access](/docs/latest/user-manual/custom-primitives/primitive-rest-api)

<span class="user-guide-menu-header"><img src="/assets/img/icons/configuration.svg" class="configuration"> Configuration</span>

* [Cluster Configuration](/docs/latest/user-manual/configuration/cluster-configuration)
* [Partition Group Configuration](/docs/latest/user-manual/configuration/partition-group-configuration)
* [Primitive Configurations](/docs/latest/user-manual/configuration/primitive-configurations)
* [Serializer Configurations](/docs/latest/user-manual/configuration/serializer-configurations)

<span class="user-guide-menu-header"><img src="/assets/img/icons/serialization.svg" class="serialization"> Serialization</span>

* [Configuring a Namespace](/docs/latest/user-manual/serialization/configuring-a-namespace)
* [Registering Custom Serializers](/docs/latest/user-manual/serialization/registering-custom-serializers)

<span class="user-guide-menu-header"><img src="/assets/img/icons/agent.png" class="agent"> Agent</span>

* [Starting the Agent](/docs/latest/user-manual/agent/starting-the-agent)
* [Client Agents](/docs/latest/user-manual/agent/client-agents)

<span class="user-guide-menu-header"><img src="/assets/img/icons/rest.svg" class="rest"> REST API</span>

* [Cluster Management](/docs/latest/user-manual/rest/cluster-management)
* [Direct Messaging](/docs/latest/user-manual/rest/direct-messaging)
* [Publish-Subscribe Messaging](/docs/latest/user-manual/rest/publish-subscribe-messaging)
* [Distributed Primitives](/docs/latest/user-manual/rest/distributed-primitives)

<span class="user-guide-menu-header"><img src="/assets/img/icons/cli.svg" class="cli"> CLI</span>

* [Setup](/docs/latest/user-manual/cli/setup)
* [Operation](/docs/latest/user-manual/cli/operation)

<span class="user-guide-menu-header"><img src="/assets/img/icons/test.svg" class="test"> Test Framework</span>

* [Setting up the Framework](/docs/latest/user-manual/test/setup)
* [Bootstrapping a Test Cluster](/docs/latest/user-manual/test/bootstrapping)
* [Adding Nodes](/docs/latest/user-manual/test/adding-nodes)
* [Disrupting Nodes](/docs/latest/user-manual/test/disrupting-nodes)
  * [Killing Nodes](/docs/latest/user-manual/test/disrupting-nodes#killing-nodes)
  * [Stress Testing Nodes](/docs/latest/user-manual/test/disrupting-nodes#stress-testing-nodes)
* [Disrupting the Network](/docs/latest/user-manual/test/disrupting-networks)
  * [Injecting Latency into the Network](/docs/latest/user-manual/test/disrupting-networks#injecting-latency-into-the-network)
  * [Creating Network Partitions](/docs/latest/user-manual/test/disrupting-networks#creating-network-partitions)
* [Running Tests](/docs/latest/user-manual/test/running-tests)
* [Writing New Tests](/docs/latest/user-manual/test/writing-tests)

<span class="user-guide-menu-header"><img src="/assets/img/icons/architecture.svg" class="architecture"> Architecture</span>

* [Cluster Communication](/docs/latest/user-manual/architecture/cluster-communication)
* [Group Membership](/docs/latest/user-manual/architecture/group-membership)
* [Partition Groups](/docs/latest/user-manual/architecture/partition-groups)
* [Primitive Protocols](/docs/latest/user-manual/architecture/primitive-protocols)
  * [Raft](/docs/latest/user-manual/architecture/primitive-protocols#raft)
  * [Primary-backup](/docs/latest/user-manual/architecture/primitive-protocols#primary-backup)