<h3 class="user-guide-menu-header"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</h3>
<div markdown="1">
{% capture toc %}
* [What is Atomix](what-is-atomix)
* [Installation and Setup](installation-and-setup)
* [Comparisons](comparisons)
  * [Hazelcast](comparisons#hazelcast)
  * [ZooKeeper](comparisons#zookeeper)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</h3>
<div markdown="1">
{% capture toc %}
* [Cluster](cluster)
* [Replication Protocols](replication-protocols)
* [Partition Groups](partition-groups)
* [Distributed Primitives](distributed-primitives)
* [Primitive Protocols](primitive-protocols)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Configuration](cluster-configuration)
  * [Members](cluster-configuration#members)
  * [Bootstrapping a New Cluster](cluster-configuration#bootstrapping-a-new-cluster)
  * [Joining an Existing Cluster](cluster-configuration#joining-an-existing-cluster)
  * [File-based Configuration](cluster-configuration#file-based-configuration)
* [Member Discovery](member-discovery)
  * [Multicast Discovery](member-discovery#multicast-discovery)
* [Partition Groups](partition-groups)
  * [Configuring Partition Groups](partition-groups#configuring-partition-groups)
  * [Group Discovery](partition-groups#group-discovery)
  * [The Management Group](partition-groups#the-management-group)
  * [Primitive Groups](partition-groups#primitive-groups)
  * [Raft Partition Groups](partition-groups#raft-partition-groups)
  * [Primary-Backup Partition Groups](partition-groups#primary-backup-partition-groups)
  * [Profiles](partition-groups#profiles)
* [Member Groups](member-groups)
  * [Rack Awareness](member-groups#rack-awareness)
* [Cluster Membership](cluster-membership)
  * [Getting the Set of Members in the Cluster](cluster-membership#getting-the-set-of-members-in-the-cluster)
  * [Member States](cluster-membership#member-states)
  * [Listening for Membership Changes](cluster-membership#listening-for-membership-changes)
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
  * [Constructing Distributed Primitives](overview#constructing-distributed-primitives)
  * [Synchronous and Asynchronous Primitives](overview#synchronous-and-asynchronous-primitives)
* [Primitive Protocols](primitive-protocols)
  * [MultiRaftProtocol](primitive-protocols#multiraftprotocol)
  * [MultiPrimaryProtocol](primitive-protocols#multiprimaryprotocol)
  * [Protocol Partitioners](primitive-protocols#protocol-partitioners)
* [AtomicCounter](AtomicCounter)
* [AtomicCounterMap](AtomicCounterMap)
* [AtomicIdGenerator](AtomicIdGenerator)
* [AtomicValue](AtomicValue)
* [ConsistentMap](ConsistentMap)
* [ConsistentMultimap](ConsistentMultimap)
* [ConsistentTreeMap](ConsistentTreeMap)
* [DistributedLock](DistributedLock)
* [DistributedSemaphore](DistributedSemaphore)
* [DistributedSet](DistributedSet)
* [DocumentTree](DocumentTree)
* [LeaderElection](LeaderElection)
* [WorkQueue](WorkQueue)
* [Primitive Anti-Patterns](primitive-anti-patterns)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</h3>
<div markdown="1">
{% capture toc %}
* [Overview](overview)
* [Defining the Primitive Type](primitive-type)
* [Creating the Primitive Service](primitive-service)
  * [Service Proxy](primitive-service#service-proxy)
  * [Client Proxy](primitive-service#client-proxy)
  * [Defining the Service](primitive-service#defining-the-service)
  * [Listening for Disconnections](primitive-service#listening-for-disconnections)
  * [Backing Up the State](primitive-service#backing-up-the-state)
* [Creating a Proxy](primitive-proxy)
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