<h3 class="user-guide-menu-header"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</h3>
<div markdown="1">
{% capture toc %}
* [What is Atomix](introduction/what-is-atomix)
* [Features](introduction/features)
* [Installation and Setup](introduction/installation-and-setup)
* [Comparisons](introduction/comparisons)
  * [Something Unique](introduction/comparisons#something-unique)
  * [ZooKeeper](introduction/comparisons#zookeeper)
  * [Hazelcast](introduction/comparisons#hazelcast)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Architecture](concepts/cluster-architecture)
  * [Core Nodes](concepts/cluster-architecture#core-nodes)
  * [Data Nodes](concepts/cluster-architecture#data-nodes)
  * [Client Nodes](concepts/cluster-architecture#client-nodes)
  * [Partition Groups](concepts/cluster-architecture#partition-groups)
* [Distributed Primitives](concepts/distributed-primitives)
  * [Data Primitives](concepts/distributed-primitives#data-primitives)
  * [Coordination Primitives](concepts/distributed-primitives#coordination-primitives)
  * [Primitive Protocols](concepts/distributed-primitives#primitive-protocols)
* [Consistency](concepts/consistency)
  * [CAP Theorem](concepts/consistency#cap-theorem)
  * [Consistency Models](concepts/consistency#consistency-models)
  * [Event Consistency](concepts/consistency#event-consistency)
  * [Cross-primitive Consistency](concepts/consistency#cross-primitive-consistency)
* [Fault Tolerance](concepts/fault-tolerance)
  * [Node Failures](concepts/fault-tolerance#node-failures)
  * [Network Partitions](concepts/fault-tolerance#network-partitions)
* [Threading Model](concepts/threading-model)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</h3>
<div markdown="1">
{% capture toc %}
* [Bootstrapping a Cluster](cluster-management/bootstrapping-a-cluster)
  * [Node Objects](cluster-management/bootstrapping-a-cluster#node-objects)
* [Member Discovery](cluster-management/member-discovery)
  * [IP Ranges](cluster-management/member-discovery#ip-ranges)
  * [Multicast Discovery](cluster-management/member-discovery#multicast-discovery)
* [Partition Groups](cluster-management/partition-groups)
  * [Raft Partition Groups](cluster-management/partition-groups#raft-partition-groups)
  * [Primary-Backup Partition Groups](cluster-management/partition-groups#primary-backup-partition-groups)
* [Member Groups](cluster-management/member-groups)
  * [Rack Awareness](cluster-management/member-groups#rack-awareness)
* [Cluster Membership](cluster-management/cluster-membership)
* [Failure Detection](cluster-management/failure-detection)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/communication.svg" class="cluster-communication"> Cluster Communication</h3>
<div markdown="1">
{% capture toc %}
* [Direct Messaging](cluster-communication/direct-messaging)
* [Publish-subscribe Messaging](cluster-communication/publish-subscribe-messaging)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/primitives.svg" class="primitives"> Primitives</h3>
<div>
{% capture toc %}
* [Overview](primitives/overview)
* [Primitive Protocols](primitives/primitive-protocols)
  * [RaftProtocol](primitives/primitive-protocols#raftprotocol)
  * [MultiPrimaryProtocol](primitives/primitive-protocols#multiprimaryprotocol)
* [AtomicCounter](primitives/AtomicCounter)
* [AtomicCounterMap](primitives/AtomicCounterMap)
* [AtomicIdGenerator](primitives/AtomicIdGenerator)
* [AtomicValue](primitives/AtomicValue)
* [ConsistentMap](primitives/ConsistentMap)
* [ConsistentMultimap](primitives/ConsistentMultimap)
* [ConsistentTreeMap](primitives/ConsistentTreeMap)
* [DistributedLock](primitives/DistributedLock)
* [DistributedSet](primitives/DistributedSet)
* [DocumentTree](primitives/DocumentTree)
* [LeaderElection](primitives/LeaderElection)
* [WorkQueue](primitives/WorkQueue)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</h3>
<div markdown="1">
{% capture toc %}
* [Defining the Primitive Type](custom-primitives/primitive-type)
* [Creating the State Machine](custom-primitives/primitive-service)
  * [Defining Primitive Operations](custom-primitives/primitive-service#defining-primitive-operations)
    * [Commands](custom-primitives/primitive-service#commands)
    * [Queries](custom-primitives/primitive-service#queries)
  * [Handling Snapshots](custom-primitives/primitive-service#handling-snapshots)
* [Creating a Proxy](custom-primitives/primitive-proxy)
* [Defining the Primitive Configuration](custom-primitives/primitive-configuration)
* [Supplying a Primitive Builder](custom-primitives/primitive-builder)
* [Supporting REST API Access](custom-primitives/primitive-rest-api)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/configuration.svg" class="configuration"> Configuration</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Configuration](configuration/cluster-configuration)
* [Partition Group Configuration](configuration/partition-group-configuration)
* [Primitive Configurations](configuration/primitive-configurations)
* [Serializer Configurations](configuration/serializer-configurations)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/serialization.svg" class="serialization"> Serialization</h3>
<div markdown="1">
{% capture toc %}
* [Configuring a Namespace](serialization/configuring-a-namespace)
* [Registering Custom Serializers](serialization/registering-custom-serializers)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/agent.png" class="agent"> Agent</h3>
<div>
{% capture toc %}
* [Starting the Agent](agent/starting-the-agent)
* [Client Agents](agent/client-agents)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/rest.svg" class="rest"> REST API</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Management](rest/cluster-management)
* [Direct Messaging](rest/direct-messaging)
* [Publish-Subscribe Messaging](rest/publish-subscribe-messaging)
* [Distributed Primitives](rest/distributed-primitives)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/python.svg" class="python"> Python API</h3>
<div markdown="1">
{% capture toc %}
* [Setup](python/setup)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/cli.svg" class="cli"> CLI</h3>
<div markdown="1">
{% capture toc %}
* [Setup](cli/setup)
* [Operation](cli/operation)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/test.svg" class="test"> Test Framework</h3>
<div markdown="1">
{% capture toc %}
* [Setting up the Framework](test/setup)
* [Bootstrapping a Test Cluster](test/bootstrapping)
* [Adding Nodes](test/adding-nodes)
* [Disrupting Nodes](test/disrupting-nodes)
  * [Killing Nodes](test/disrupting-nodes#killing-nodes)
  * [Stress Testing Nodes](test/disrupting-nodes#stress-testing-nodes)
* [Disrupting the Network](test/disrupting-networks)
  * [Injecting Latency into the Network](test/disrupting-networks#injecting-latency-into-the-network)
  * [Creating Network Partitions](test/disrupting-networks#creating-network-partitions)
* [Running Tests](test/running-tests)
* [Writing New Tests](test/writing-tests)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/architecture.svg" class="architecture"> Architecture</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Communication](architecture/cluster-communication)
* [Group Membership](architecture/group-membership)
* [Partition Groups](architecture/partition-groups)
* [Primitive Protocols](architecture/primitive-protocols)
  * [Raft](architecture/primitive-protocols#raft)
  * [Primary-backup](architecture/primitive-protocols#primary-backup)
{% endcapture %}
{{ toc | markdownify }}
</div>