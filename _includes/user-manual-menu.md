<h3 class="user-guide-menu-header"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</h3>
<div markdown="1">
{% capture toc %}
* [What is Atomix](introduction/what-is-atomix)
* [Installation and Setup](introduction/installation-and-setup)
* [Comparisons](introduction/comparisons)
  * [Hazelcast](introduction/comparisons#hazelcast)
  * [ZooKeeper](introduction/comparisons#zookeeper)
* [Architectures](introduction/architectures)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</h3>
<div markdown="1">
{% capture toc %}
* [Cluster](concepts/scluster)
* [Replication Protocols](concepts/replication-protocols)
* [Partition Groups](concepts/partition-groups)
* [Distributed Primitives](concepts/distributed-primitives)
* [Primitive Protocols](concepts/primitive-protocols)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Configuration](cluster-management/cluster-configuration)
  * [Members](cluster-management/cluster-configuration#members)
  * [Bootstrapping a New Cluster](cluster-management/cluster-configuration#bootstrapping-a-new-cluster)
  * [Joining an Existing Cluster](cluster-management/cluster-configuration#joining-an-existing-cluster)
  * [File-based Configuration](cluster-management/cluster-configuration#file-based-configuration)
* [Member Discovery](cluster-management/member-discovery)
  * [Multicast Discovery](cluster-management/member-discovery#multicast-discovery)
* [Partition Groups](cluster-management/partition-groups)
  * [Configuring Partition Groups](cluster-management/partition-groups#configuring-partition-groups)
  * [Group Discovery](cluster-management/partition-groups#group-discovery)
  * [The Management Group](cluster-management/partition-groups#the-management-group)
  * [Primitive Groups](cluster-management/partition-groups#primitive-groups)
  * [Raft Partition Groups](cluster-management/partition-groups#raft-partition-groups)
  * [Primary-Backup Partition Groups](cluster-management/partition-groups#primary-backup-partition-groups)
  * [Profiles](partition-groups#profiles)
* [Member Groups](cluster-management/member-groups)
  * [Rack Awareness](cluster-management/member-groups#rack-awareness)
* [Cluster Membership](cluster-management/cluster-membership)
  * [Getting the Set of Members in the Cluster](cluster-management/cluster-membership#getting-the-set-of-members-in-the-cluster)
  * [Member States](cluster-management/cluster-membership#member-states)
  * [Listening for Membership Changes](cluster-management/cluster-membership#listening-for-membership-changes)
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
  * [Constructing Distributed Primitives](primitives/overview#constructing-distributed-primitives)
  * [Synchronous and Asynchronous Primitives](primitives/overview#synchronous-and-asynchronous-primitives)
* [Primitive Protocols](primitives/primitive-protocols)
  * [MultiRaftProtocol](primitives/primitive-protocols#multiraftprotocol)
  * [MultiPrimaryProtocol](primitives/primitive-protocols#multiprimaryprotocol)
  * [Protocol Partitioners](primitives/primitive-protocols#protocol-partitioners)
  * [AntiEntropyProtocol](primitives/primitive-protocols#antientropyprotocol)
  * [CrdtProtocol](primitives/primitive-protocols#crdtprotocol)
* [AtomicCounter](primitives/AtomicCounter)
  * [Configuration](primitives/AtomicCounter#configuration)
  * [Operation](primitives/AtomicCounter#operation)
  * [Cleanup](primitives/AtomicCounter#cleanup)
* [AtomicCounterMap](primitives/AtomicCounterMap)
  * [Configuration](primitives/AtomicCounterMap#configuration)
  * [Operation](primitives/AtomicCounterMap#operation)
  * [Cleanup](primitives/AtomicCounterMap#cleanup)
* [AtomicDocumentTree](primitives/AtomicDocumentTree)
  * [Configuration](primitives/AtomicDocumentTree#configuration)
  * [Operation](primitives/AtomicDocumentTree#operation)
  * [Optimistic Locking](primitives/AtomicDocumentTree#optimistic-locking)
  * [Asynchronous Operation](primitives/AtomicDocumentTree#asynchronous-operation)
  * [Event Notifications](primitives/AtomicDocumentTree#event-notifications)
  * [Cleanup](primitives/AtomicDocumentTree#cleanup)
* [AtomicIdGenerator](primitives/AtomicIdGenerator)
  * [Configuration](primitives/AtomicIdGenerator#configuration)
  * [Operation](primitives/AtomicIdGenerator#operation)
  * [Cleanup](primitives/AtomicIdGenerator#cleanup)
* [AtomicLock](primitives/AtomicLock)
  * [Configuration](primitives/AtomicLock#configuration)
  * [Operation](primitives/AtomicLock#operation)
  * [Monitoring the Lock State](primitives/AtomicLock#monitoring-the-lock-state)
  * [Cleanup](primitives/AtomicLock#cleanup)
* [AtomicMap](primitives/AtomicMap)
  * [Configuration](primitives/AtomicMap#configuration)
  * [Operation](primitives/AtomicMap#operation)
  * [Optimistic Locking](primitives/AtomicMap#optimistic-locking)
  * [Asynchronous Operation](primitives/AtomicMap#asynchronous-operation)
  * [Event Notifications](primitives/AtomicMap#event-notifications)
  * [Map Views](primitives/AtomicMap#map-views)
  * [Iterators](primitives/AtomicMap#iterators)
  * [Streams](primitives/AtomicMap#streams)
  * [Cleanup](primitives/AtomicMap#cleanup)
* [AtomicMultimap](primitives/AtomicMultimap)
  * [Configuration](primitives/AtomicMultimap#configuration)
  * [Operation](primitives/AtomicMultimap#operation)
  * [Optimistic Locking](primitives/AtomicMultimap#optimistic-locking)
  * [Asynchronous Operation](primitives/AtomicMultimap#asynchronous-operation)
  * [Event Notifications](primitives/AtomicMultimap#event-notifications)
  * [Multimap Views](primitives/AtomicMultimap#multimap-views)
  * [Iterators](primitives/AtomicMultimap#iterators)
  * [Streams](primitives/AtomicMultimap#streams)
  * [Cleanup](primitives/AtomicMultimap#cleanup)
* [AtomicNavigableMap](primitives/AtomicNavigableMap)
  * [Configuration](primitives/AtomicNavigableMap#configuration)
  * [Operation](primitives/AtomicNavigableMap#operation)
  * [Navigable Map Views](primitives/AtomicNavigableMap#navigable-map-views)
  * [Cleanup](primitives/AtomicNavigableMap#cleanup)
* [AtomicSemaphore](primitives/AtomicSemaphore)
  * [Configuration](primitives/AtomicSemaphore#configuration)
  * [Operation](primitives/AtomicSemaphore#operation)
  * [Monitoring the Semaphore State](primitives/AtomicSemaphore#monitoring-the-semaphore-state)
  * [Cleanup](primitives/AtomicSemaphore#cleanup)
* [AtomicSortedMap](primitives/AtomicSortedMap)
  * [Configuration](primitives/AtomicSortedMap#configuration)
  * [Operation](primitives/AtomicSortedMap#operation)
  * [Sorted Map Views](primitives/AtomicSortedMap#sorted-map-views)
  * [Cleanup](primitives/AtomicSortedMap#cleanup)
* [AtomicValue](primitives/AtomicValue)
  * [Configuration](primitives/AtomicValue#configuration)
  * [Operation](primitives/AtomicValue#operation)
  * [Event Notifications](primitives/AtomicValue#event-notifications)
  * [Cleanup](primitives/AtomicValue#cleanup)
* [DistributedCounter](primitives/DistributedCounter)
  * [Configuration](primitives/DistributedCounter#configuration)
  * [Operation](primitives/DistributedCounter#operation)
  * [Cleanup](primitives/DistributedCounter#cleanup)
* [DistributedCyclicBarrier](primitives/DistributedCyclicBarrier)
  * [Configuration](primitives/DistributedCyclicBarrier#configuration)
  * [Operation](primitives/DistributedCyclicBarrier#operation)
  * [Cleanup](primitives/DistributedCyclicBarrier#cleanup)
* [DistributedList](primitives/DistributedList)
  * [Configuration](primitives/DistributedList#configuration)
  * [Operation](primitives/DistributedList#operation)
  * [Asynchronous Operation](primitives/DistributedList#asynchronous-operation)
  * [Event Notifications](primitives/DistributedList#event-notifications)
  * [Iterators](primitives/DistributedList#iterators)
  * [Streams](primitives/DistributedList#streams)
  * [Cleanup](primitives/DistributedList#cleanup)
* [DistributedLock](primitives/DistributedLock)
  * [Configuration](primitives/DistributedLock#configuration)
  * [Operation](primitives/DistributedLock#operation)
  * [Monitoring the Lock State](primitives/DistributedLock#monitoring-the-lock-state)
  * [Cleanup](primitives/DistributedLock#cleanup)
* [DistributedMap](primitives/DistributedMap)
  * [Configuration](primitives/DistributedMap#configuration)
  * [Operation](primitives/DistributedMap#operation)
  * [Optimistic Locking](primitives/DistributedMap#optimistic-locking)
  * [Asynchronous Operation](primitives/DistributedMap#asynchronous-operation)
  * [Event Notifications](primitives/DistributedMap#event-notifications)
  * [Map Views](primitives/DistributedMap#map-views)
  * [Iterators](primitives/DistributedMap#iterators)
  * [Streams](primitives/DistributedMap#streams)
  * [Cleanup](primitives/DistributedMap#cleanup)
* [DistributedMultimap](primitives/DistributedMultimap)
  * [Configuration](primitives/DistributedMultimap#configuration)
  * [Operation](primitives/DistributedMultimap#operation)
  * [Optimistic Locking](primitives/DistributedMultimap#optimistic-locking)
  * [Asynchronous Operation](primitives/DistributedMultimap#asynchronous-operation)
  * [Event Notifications](primitives/DistributedMultimap#event-notifications)
  * [Multimap Views](primitives/DistributedMultimap#multimmap-views)
  * [Iterators](primitives/DistributedMultimap#iterators)
  * [Streams](primitives/DistributedMultimap#streams)
  * [Cleanup](primitives/DistributedMultimap#cleanup)
* [DistributedMultiset](primitives/DistributedMultiset)
  * [Configuration](primitives/DistributedMultiset#configuration)
  * [Operation](primitives/DistributedMultiset#operation)
  * [Asynchronous Operation](primitives/DistributedMultiset#asynchronous-operation)
  * [Event Notifications](primitives/DistributedMultiset#event-notifications)
  * [Iterators](primitives/DistributedMultiset#iterators)
  * [Streams](primitives/DistributedMultiset#streams)
  * [Cleanup](primitives/DistributedMultiset#cleanup)
* [DistributedNavigableMap](primitives/DistributedNavigableMap)
  * [Configuration](primitives/DistributedNavigableMap#configuration)
  * [Operation](primitives/DistributedNavigableMap#operation)
  * [Navigable Map Views](primitives/DistributedNavigableMap#navigable-map-views)
  * [Cleanup](primitives/DistributedNavigableMap#cleanup)
* [DistributedNavigableSet](primitives/DistributedNavigableSet)
  * [Configuration](primitives/DistributedNavigableSet#configuration)
  * [Operation](primitives/DistributedNavigableSet#operation)
  * [Asynchronous Operation](primitives/DistributedNavigableSet#asynchronous-operation)
  * [Event Notifications](primitives/DistributedNavigableSet#event-notifications)
  * [Iterators](primitives/DistributedNavigableSet#iterators)
  * [Streams](primitives/DistributedNavigableSet#streams)
  * [Cleanup](primitives/DistributedNavigableSet#cleanup)
* [DistributedQueue](primitives/DistributedQueue)
  * [Configuration](primitives/DistributedQueue#configuration)
  * [Operation](primitives/DistributedQueue#operation)
  * [Asynchronous Operation](primitives/DistributedQueue#asynchronous-operation)
  * [Event Notifications](primitives/DistributedQueue#event-notifications)
  * [Iterators](primitives/DistributedQueue#iterators)
  * [Streams](primitives/DistributedQueue#streams)
  * [Cleanup](primitives/DistributedQueue#cleanup)
* [DistributedSemaphore](primitives/DistributedSemaphore)
  * [Configuration](primitives/DistributedSemaphore#configuration)
  * [Operation](primitives/DistributedSemaphore#operation)
  * [Monitoring the Semaphore State](primitives/DistributedSemaphore#monitoring-the-semaphore-state)
  * [Cleanup](primitives/AtomicSemaphore#cleanup)
* [DistributedSet](primitives/DistributedSet)
  * [Configuration](primitives/DistributedSet#configuration)
  * [Operation](primitives/DistributedSet#operation)
  * [Asynchronous Operation](primitives/DistributedSet#asynchronous-operation)
  * [Event Notifications](primitives/DistributedSet#event-notifications)
  * [Iterators](primitives/DistributedSet#iterators)
  * [Streams](primitives/DistributedSet#streams)
  * [Cleanup](primitives/DistributedSet#cleanup)
* [DistributedSortedMap](primitives/DistributedSortedMap)
  * [Configuration](primitives/DistributedSortedMap#configuration)
  * [Operation](primitives/DistributedSortedMap#operation)
  * [Sorted Map Views](primitives/DistributedSortedMap#sorted-map-views)
  * [Cleanup](primitives/DistributedSortedMap#cleanup)
* [DistributedSortedSet](primitives/DistributedSortedSet)
  * [Configuration](primitives/DistributedSortedSet#configuration)
  * [Operation](primitives/DistributedSortedSet#operation)
  * [Asynchronous Operation](primitives/DistributedSortedSet#asynchronous-operation)
  * [Event Notifications](primitives/DistributedSortedSet#event-notifications)
  * [Iterators](primitives/DistributedSortedSet#iterators)
  * [Streams](primitives/DistributedSortedSet#streams)
  * [Cleanup](primitives/DistributedSortedSet#cleanup)
* [DistributedValue](primitives/DistributedValue)
  * [Configuration](primitives/DistributedValue#configuration)
  * [Operation](primitives/DistributedValue#operation)
  * [Event Notifications](primitives/DistributedValue#event-notifications)
  * [Cleanup](primitives/DistributedValue#cleanup)
* [LeaderElection](primitives/LeaderElection)
  * [Configuration](primitives/LeaderElection#configuration)
  * [Operation](primitives/LeaderElection#operation)
  * [Asynchronous Operation](primitives/LeaderElection#asynchronous-operation)
  * [Event Notifications](primitives/LeaderElection#event-notifications)
  * [Cleanup](primitives/LeaderElection#cleanup)
* [WorkQueue](primitives/WorkQueue)
* [Transactions](primitives/transactions)
  * [Working with Transactions](primitives/transactions#working-with-transactions)
* [Anti-Patterns](primitives/anti-patterns)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</h3>
<div markdown="1">
{% capture toc %}
* [Overview](custom-primitives/overview)
* [Defining the Primitive Type](custom-primitives/primitive-type)
* [Creating the Primitive Service](custom-primitives/primitive-service)
  * [Service Proxy](custom-primitives/primitive-service#service-proxy)
  * [Client Proxy](custom-primitives/primitive-service#client-proxy)
  * [Defining the Service](custom-primitives/primitive-service#defining-the-service)
  * [Listening for Disconnections](custom-primitives/primitive-service#listening-for-disconnections)
  * [Backing Up the State](custom-primitives/primitive-service#backing-up-the-state)
* [Creating a Proxy](custom-primitives/primitive-proxy)
* [Supplying a Primitive Builder](custom-primitives/primitive-builder)
* [Supporting REST API Access](custom-primitives/primitive-rest-api)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/configuration.svg" class="configuration"> Configuration</h3>
<div markdown="1">
{% capture toc %}
* [Configuration Reference](configuration/configuration/reference)
  * [Atomix Configuration](configuration/reference#atomix-configuration)
  * [Cluster Configuration](configuration/reference#cluster-configuration)
  * [Cluster Discovery Protocols](configuration/reference#cluster-discovery-protocols)
    * [Bootstrap Discovery Protocol](configuration/reference#bootstrap-discovery-protocol)
    * [Multicast Discovery Protocol](configuration/reference#multicast-discovery-protocol)
    * [DNS Discovery Protocol](configuration/reference#dns-discovery-protocol)
  * [Cluster Membership Protocols](configuration/reference#cluster-membership-protocols)
    * [Heartbeat Protocol](configuration/reference#heartbeat-protocol)
    * [SWIM Protocol](configuration/reference#swim-protocol)
  * [Raft](configuration/reference#raft)
    * [Raft Partition Group](configuration/refrence#raft-partition-group)
    * [Multi-Raft Protocol](configuration/reference#multi-raft-protocol)
  * [Primary-Backup](configuration/reference#primary-backup)
    * [Primary-Backup Partition Group](configuration/reference#primary-backup-partition-group)
    * [Multi-Primary Protocol](configuration/reference#multi-primary-protocol)
  * [Distributed Log](configuration/reference#distributed-log)
    * [Log Partition Group](configuration/reference#log-partition-group)
    * [Multi-Log Protocol](configuration/reference#multi-log-protocol)
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
* [Running the Agent](agent/running-the-agent)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/deployment.png" class="deployment"> Deployment</h3>
<div>
{% capture toc %}
* [Docker](deployment/docker)
* [Kubernetes](deployment/kubernetes)
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