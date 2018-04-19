<h3 class="user-guide-menu-header"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</h3>
<div markdown="1">
{% capture toc %}
* [What is Atomix](what-is-atomix)
* [Features](features)
* [Installation and Setup](installation-and-setup)
* [Comparisons](comparisons)
  * [Something Unique](comparisons#something-unique)
  * [ZooKeeper](comparisons#zookeeper)
  * [Hazelcast](comparisons#hazelcast)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Architecture](cluster-architecture)
  * [Core Nodes](cluster-architecture#core-nodes)
  * [Data Nodes](cluster-architecture#data-nodes)
  * [Client Nodes](cluster-architecture#client-nodes)
  * [Partition Groups](cluster-architecture#partition-groups)
* [Distributed Primitives](distributed-primitives)
  * [Data Primitives](distributed-primitives#data-primitives)
  * [Coordination Primitives](distributed-primitives#coordination-primitives)
  * [Primitive Protocols](distributed-primitives#primitive-protocols)
* [Consistency](consistency)
  * [CAP Theorem](consistency#cap-theorem)
  * [Consistency Models](consistency#consistency-models)
  * [Event Consistency](consistency#event-consistency)
  * [Cross-primitive Consistency](consistency#cross-primitive-consistency)
* [Fault Tolerance](fault-tolerance)
  * [Node Failures](fault-tolerance#node-failures)
  * [Network Partitions](fault-tolerance#network-partitions)
* [Threading Model](threading-model)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</h3>
<div markdown="1">
{% capture toc %}
* [Bootstrapping a Cluster](bootstrapping-a-cluster)
  * [Node Objects](bootstrapping-a-cluster#node-objects)
* [Member Discovery](member-discovery)
  * [IP Ranges](member-discovery#ip-ranges)
  * [Multicast Discovery](member-discovery#multicast-discovery)
* [Partition Groups](partition-groups)
  * [Raft Partition Groups](partition-groups#raft-partition-groups)
  * [Primary-Backup Partition Groups](partition-groups#primary-backup-partition-groups)
* [Member Groups](member-groups)
  * [Rack Awareness](member-groups#rack-awareness)
* [Cluster Membership](cluster-membership)
* [Failure Detection](failure-detection)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/communication.svg" class="cluster-communication"> Cluster Communication</h3>
<div markdown="1">
{% capture toc %}
* [Direct Messaging](direct-messaging)
* [Publish-subscribe Messaging](publish-subscribe-messaging)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/primitives.svg" class="primitives"> Primitives</h3>
<div>
{% capture toc %}
* [Overview](overview)
* [Primitive Protocols](primitive-protocols)
  * [RaftProtocol](primitive-protocols#raftprotocol)
  * [MultiPrimaryProtocol](primitive-protocols#multiprimaryprotocol)
* [AtomicCounter](AtomicCounter)
* [AtomicCounterMap](AtomicCounterMap)
* [AtomicIdGenerator](AtomicIdGenerator)
* [AtomicValue](AtomicValue)
* [ConsistentMap](ConsistentMap)
* [ConsistentMultimap](ConsistentMultimap)
* [ConsistentTreeMap](ConsistentTreeMap)
* [DistributedLock](DistributedLock)
* [DistributedSet](DistributedSet)
* [DocumentTree](DocumentTree)
* [LeaderElection](LeaderElection)
* [WorkQueue](WorkQueue)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</h3>
<div markdown="1">
{% capture toc %}
* [Defining the Primitive Type](primitive-type)
* [Creating the State Machine](primitive-service)
  * [Defining Primitive Operations](primitive-service#defining-primitive-operations)
    * [Commands](primitive-service#commands)
    * [Queries](primitive-service#queries)
  * [Handling Snapshots](primitive-service#handling-snapshots)
* [Creating a Proxy](primitive-proxy)
* [Defining the Primitive Configuration](primitive-configuration)
* [Supplying a Primitive Builder](primitive-builder)
* [Supporting REST API Access](primitive-rest-api)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/configuration.svg" class="configuration"> Configuration</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Configuration](cluster-configuration)
* [Partition Group Configuration](partition-group-configuration)
* [Primitive Configurations](primitive-configurations)
* [Serializer Configurations](serializer-configurations)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/serialization.svg" class="serialization"> Serialization</h3>
<div markdown="1">
{% capture toc %}
* [Configuring a Namespace](configuring-a-namespace)
* [Registering Custom Serializers](registering-custom-serializers)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/agent.png" class="agent"> Agent</h3>
<div>
{% capture toc %}
* [Starting the Agent](starting-the-agent)
* [Client Agents](client-agents)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/rest.svg" class="rest"> REST API</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Management](cluster-management)
* [Direct Messaging](direct-messaging)
* [Publish-Subscribe Messaging](publish-subscribe-messaging)
* [Distributed Primitives](distributed-primitives)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/python.svg" class="python"> Python API</h3>
<div markdown="1">
{% capture toc %}
* [Setup](setup)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/cli.svg" class="cli"> CLI</h3>
<div markdown="1">
{% capture toc %}
* [Setup](setup)
* [Operation](operation)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/test.svg" class="test"> Test Framework</h3>
<div markdown="1">
{% capture toc %}
* [Setting up the Framework](setup)
* [Bootstrapping a Test Cluster](bootstrapping)
* [Adding Nodes](adding-nodes)
* [Disrupting Nodes](disrupting-nodes)
  * [Killing Nodes](disrupting-nodes#killing-nodes)
  * [Stress Testing Nodes](disrupting-nodes#stress-testing-nodes)
* [Disrupting the Network](disrupting-networks)
  * [Injecting Latency into the Network](disrupting-networks#injecting-latency-into-the-network)
  * [Creating Network Partitions](disrupting-networks#creating-network-partitions)
* [Running Tests](running-tests)
* [Writing New Tests](writing-tests)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/architecture.svg" class="architecture"> Architecture</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Communication](cluster-communication)
* [Group Membership](group-membership)
* [Partition Groups](partition-groups)
* [Primitive Protocols](primitive-protocols)
  * [Raft](primitive-protocols#raft)
  * [Primary-backup](primitive-protocols#primary-backup)
{% endcapture %}
{{ toc | markdownify }}
</div>