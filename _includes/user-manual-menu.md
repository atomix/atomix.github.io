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
  * [AntiEntropyProtocol](primitive-protocols#antientropyprotocol)
  * [CrdtProtocol](primitive-protocols#crdtprotocol)
* [AtomicCounter](AtomicCounter)
  * [Configuration](AtomicCounter#configuration)
  * [Operation](AtomicCounter#operation)
  * [Cleanup](AtomicCounter#cleanup)
* [AtomicCounterMap](AtomicCounterMap)
  * [Configuration](AtomicCounterMap#configuration)
  * [Operation](AtomicCounterMap#operation)
  * [Cleanup](AtomicCounterMap#cleanup)
* [AtomicDocumentTree](AtomicDocumentTree)
* [AtomicIdGenerator](AtomicIdGenerator)
  * [Configuration](AtomicIdGenerator#configuration)
  * [Operation](AtomicIdGenerator#operation)
  * [Cleanup](AtomicIdGenerator#cleanup)
* [AtomicLock](AtomicLock)
  * [Configuration](AtomicLock#configuration)
  * [Operation](AtomicLock#operation)
  * [Monitoring the Lock State](AtomicLock#monitoring-the-lock-state)
  * [Cleanup](AtomicLock#cleanup)
* [AtomicMap](AtomicMap)
  * [Configuration](AtomicMap#configuration)
  * [Operation](AtomicMap#operation)
  * [Optimistic Locking](AtomicMap#optimistic-locking)
  * [Asynchronous Operation](AtomicMap#asynchronous-operation)
  * [Event Notifications](AtomicMap#event-notifications)
  * [Map Views](AtomicMap#map-views)
  * [Iterators](AtomicMap#iterators)
  * [Streams](AtomicMap#streams)
  * [Cleanup](AtomicMap#cleanup)
* [AtomicMultimap](AtomicMultimap)
  * [Configuration](AtomicMultimap#configuration)
  * [Operation](AtomicMultimap#operation)
  * [Optimistic Locking](AtomicMultimap#optimistic-locking)
  * [Asynchronous Operation](AtomicMultimap#asynchronous-operation)
  * [Event Notifications](AtomicMultimap#event-notifications)
  * [Multimap Views](AtomicMultimap#multimap-views)
  * [Iterators](AtomicMultimap#iterators)
  * [Streams](AtomicMultimap#streams)
  * [Cleanup](AtomicMultimap#cleanup)
* [AtomicNavigableMap](AtomicNavigableMap)
  * [Configuration](AtomicNavigableMap#configuration)
  * [Operation](AtomicNavigableMap#operation)
  * [Optimistic Locking](AtomicNavigableMap#optimistic-locking)
  * [Asynchronous Operation](AtomicNavigableMap#asynchronous-operation)
  * [Event Notifications](AtomicNavigableMap#event-notifications)
  * [Map Views](AtomicNavigableMap#map-views)
  * [Iterators](AtomicNavigableMap#iterators)
  * [Streams](AtomicNavigableMap#streams)
  * [Cleanup](AtomicNavigableMap#cleanup)
* [AtomicSortedMap](AtomicSortedMap)
  * [Configuration](AtomicSortedMap#configuration)
  * [Operation](AtomicSortedMap#operation)
  * [Optimistic Locking](AtomicSortedMap#optimistic-locking)
  * [Asynchronous Operation](AtomicSortedMap#asynchronous-operation)
  * [Event Notifications](AtomicSortedMap#event-notifications)
  * [Map Views](AtomicSortedMap#map-views)
  * [Iterators](AtomicSortedMap#iterators)
  * [Streams](AtomicSortedMap#streams)
  * [Cleanup](AtomicSortedMap#cleanup)
* [AtomicValue](AtomicValue)
  * [Configuration](AtomicValue#configuration)
  * [Operation](AtomicValue#operation)
  * [Event Notifications](AtomicValue#event-notifications)
  * [Cleanup](AtomicValue#cleanup)
* [DistributedCounter](DistributedCounter)
* [DistributedCyclicBarrier](DistributedCyclicBarrier)
* [DistributedList](DistributedList)
  * [Configuration](DistributedList#configuration)
  * [Operation](DistributedList#operation)
  * [Asynchronous Operation](DistributedList#asynchronous-operation)
  * [Event Notifications](DistributedList#event-notifications)
  * [Iterators](DistributedList#iterators)
  * [Streams](DistributedList#streams)
  * [Cleanup](DistributedList#cleanup)
* [DistributedLock](DistributedLock)
* [DistributedMap](DistributedMap)
* [DistributedMultimap](DistributedMultimap)
* [DistributedMultiset](DistributedMultiset)
* [DistributedNavigableMap](DistributedNavigableMap)
* [DistributedNavigableSet](DistributedNavigableSet)
* [DistributedQueue](DistributedQueue)
  * [Configuration](DistributedQueue#configuration)
  * [Operation](DistributedQueue#operation)
  * [Asynchronous Operation](DistributedQueue#asynchronous-operation)
  * [Event Notifications](DistributedQueue#event-notifications)
  * [Iterators](DistributedQueue#iterators)
  * [Streams](DistributedQueue#streams)
  * [Cleanup](DistributedQueue#cleanup)
* [DistributedSemaphore](DistributedSemaphore)
* [DistributedSet](DistributedSet)
  * [Configuration](DistributedSet#configuration)
  * [Operation](DistributedSet#operation)
  * [Asynchronous Operation](DistributedSet#asynchronous-operation)
  * [Event Notifications](DistributedSet#event-notifications)
  * [Iterators](DistributedSet#iterators)
  * [Streams](DistributedSet#streams)
  * [Cleanup](DistributedSet#cleanup)
* [DistributedSortedMap](DistributedSortedMap)
* [DistributedSortedSet](DistributedSortedSet)
* [DistributedValue](DistributedValue)
* [LeaderElection](LeaderElection)
* [WorkQueue](WorkQueue)
* [Transactions](transactions)
  * [Working with Transactions](transactions#working-with-transactions)
* [Anti-Patterns](anti-patterns)
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