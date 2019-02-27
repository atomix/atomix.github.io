<h3 class="user-guide-menu-header"><img src="/assets/img/icons/introduction.svg" class="introduction"> Introduction</h3>
<div markdown="1">
{% capture toc %}
* [What is Atomix](/docs/latest/user-manual/introduction/what-is-atomix)
* [Installation and Setup](/docs/latest/user-manual/introduction/installation-and-setup)
* [Comparisons](/docs/latest/user-manual/introduction/comparisons)
  * [Hazelcast](/docs/latest/user-manual/introduction/comparisons#hazelcast)
  * [ZooKeeper](/docs/latest/user-manual/introduction/comparisons#zookeeper)
* [Architectures](/docs/latest/user-manual/introduction/architectures)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/concepts.svg" class="concepts"> Concepts</h3>
<div markdown="1">
{% capture toc %}
* [Cluster](/docs/latest/user-manual/concepts/cluster)
* [Replication Protocols](/docs/latest/user-manual/concepts/replication-protocols)
* [Partition Groups](/docs/latest/user-manual/concepts/partition-groups)
* [Distributed Primitives](/docs/latest/user-manual/concepts/distributed-primitives)
* [Primitive Protocols](/docs/latest/user-manual/concepts/primitive-protocols)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/clustering.png" class="cluster-management"> Cluster Management</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Configuration](/docs/latest/user-manual/cluster-management/cluster-configuration)
  * [Members](/docs/latest/user-manual/cluster-management/cluster-configuration#members)
  * [Bootstrapping a New Cluster](/docs/latest/user-manual/cluster-management/cluster-configuration#bootstrapping-a-new-cluster)
  * [Joining an Existing Cluster](/docs/latest/user-manual/cluster-management/cluster-configuration#joining-an-existing-cluster)
  * [File-based Configuration](/docs/latest/user-manual/cluster-management/cluster-configuration#file-based-configuration)
* [Member Discovery](/docs/latest/user-manual/cluster-management/member-discovery)
  * [Multicast Discovery](/docs/latest/user-manual/cluster-management/member-discovery#multicast-discovery)
* [Partition Groups](/docs/latest/user-manual/cluster-management/partition-groups)
  * [Configuring Partition Groups](/docs/latest/user-manual/cluster-management/partition-groups#configuring-partition-groups)
  * [Group Discovery](/docs/latest/user-manual/cluster-management/partition-groups#group-discovery)
  * [The Management Group](/docs/latest/user-manual/cluster-management/partition-groups#the-management-group)
  * [Primitive Groups](/docs/latest/user-manual/cluster-management/partition-groups#primitive-groups)
  * [Raft Partition Groups](/docs/latest/user-manual/cluster-management/partition-groups#raft-partition-groups)
  * [Primary-Backup Partition Groups](/docs/latest/user-manual/cluster-management/partition-groups#primary-backup-partition-groups)
  * [Profiles](/docs/latest/user-manual/partition-groups#profiles)
* [Member Groups](/docs/latest/user-manual/cluster-management/member-groups)
  * [Rack Awareness](/docs/latest/user-manual/cluster-management/member-groups#rack-awareness)
* [Cluster Membership](/docs/latest/user-manual/cluster-management/cluster-membership)
  * [Getting the Set of Members in the Cluster](/docs/latest/user-manual/cluster-management/cluster-membership#getting-the-set-of-members-in-the-cluster)
  * [Member States](/docs/latest/user-manual/cluster-management/cluster-membership#member-states)
  * [Listening for Membership Changes](/docs/latest/user-manual/cluster-management/cluster-membership#listening-for-membership-changes)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/communication.svg" class="cluster-communication"> Cluster Communication</h3>
<div markdown="1">
{% capture toc %}
* [Direct Messaging](/docs/latest/user-manual/cluster-communication/direct-messaging)
* [Publish-subscribe Messaging](/docs/latest/user-manual/cluster-communication/publish-subscribe-messaging)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/primitives.svg" class="primitives"> Primitives</h3>
<div>
{% capture toc %}
* [Overview](/docs/latest/user-manual/primitives/overview)
  * [Constructing Distributed Primitives](/docs/latest/user-manual/primitives/overview#constructing-distributed-primitives)
  * [Synchronous and Asynchronous Primitives](/docs/latest/user-manual/primitives/overview#synchronous-and-asynchronous-primitives)
* [Primitive Protocols](/docs/latest/user-manual/primitives/primitive-protocols)
  * [MultiRaftProtocol](/docs/latest/user-manual/primitives/primitive-protocols#multiraftprotocol)
  * [MultiPrimaryProtocol](/docs/latest/user-manual/primitives/primitive-protocols#multiprimaryprotocol)
  * [Protocol Partitioners](/docs/latest/user-manual/primitives/primitive-protocols#protocol-partitioners)
  * [AntiEntropyProtocol](/docs/latest/user-manual/primitives/primitive-protocols#antientropyprotocol)
  * [CrdtProtocol](/docs/latest/user-manual/primitives/primitive-protocols#crdtprotocol)
* [AtomicCounter](/docs/latest/user-manual/primitives/AtomicCounter)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicCounter#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicCounter#operation)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicCounter#cleanup)
* [AtomicCounterMap](/docs/latest/user-manual/primitives/AtomicCounterMap)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicCounterMap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicCounterMap#operation)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicCounterMap#cleanup)
* [AtomicDocumentTree](/docs/latest/user-manual/primitives/AtomicDocumentTree)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicDocumentTree#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicDocumentTree#operation)
  * [Optimistic Locking](/docs/latest/user-manual/primitives/AtomicDocumentTree#optimistic-locking)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/AtomicDocumentTree#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/AtomicDocumentTree#event-notifications)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicDocumentTree#cleanup)
* [AtomicIdGenerator](/docs/latest/user-manual/primitives/AtomicIdGenerator)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicIdGenerator#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicIdGenerator#operation)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicIdGenerator#cleanup)
* [AtomicLock](/docs/latest/user-manual/primitives/AtomicLock)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicLock#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicLock#operation)
  * [Monitoring the Lock State](/docs/latest/user-manual/primitives/AtomicLock#monitoring-the-lock-state)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicLock#cleanup)
* [AtomicMap](/docs/latest/user-manual/primitives/AtomicMap)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicMap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicMap#operation)
  * [Optimistic Locking](/docs/latest/user-manual/primitives/AtomicMap#optimistic-locking)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/AtomicMap#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/AtomicMap#event-notifications)
  * [Map Views](/docs/latest/user-manual/primitives/AtomicMap#map-views)
  * [Iterators](/docs/latest/user-manual/primitives/AtomicMap#iterators)
  * [Streams](/docs/latest/user-manual/primitives/AtomicMap#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicMap#cleanup)
* [AtomicMultimap](/docs/latest/user-manual/primitives/AtomicMultimap)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicMultimap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicMultimap#operation)
  * [Optimistic Locking](/docs/latest/user-manual/primitives/AtomicMultimap#optimistic-locking)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/AtomicMultimap#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/AtomicMultimap#event-notifications)
  * [Multimap Views](/docs/latest/user-manual/primitives/AtomicMultimap#multimap-views)
  * [Iterators](/docs/latest/user-manual/primitives/AtomicMultimap#iterators)
  * [Streams](/docs/latest/user-manual/primitives/AtomicMultimap#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicMultimap#cleanup)
* [AtomicNavigableMap](/docs/latest/user-manual/primitives/AtomicNavigableMap)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicNavigableMap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicNavigableMap#operation)
  * [Navigable Map Views](/docs/latest/user-manual/primitives/AtomicNavigableMap#navigable-map-views)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicNavigableMap#cleanup)
* [AtomicSemaphore](/docs/latest/user-manual/primitives/AtomicSemaphore)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicSemaphore#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicSemaphore#operation)
  * [Monitoring the Semaphore State](/docs/latest/user-manual/primitives/AtomicSemaphore#monitoring-the-semaphore-state)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicSemaphore#cleanup)
* [AtomicSortedMap](/docs/latest/user-manual/primitives/AtomicSortedMap)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicSortedMap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicSortedMap#operation)
  * [Sorted Map Views](/docs/latest/user-manual/primitives/AtomicSortedMap#sorted-map-views)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicSortedMap#cleanup)
* [AtomicValue](/docs/latest/user-manual/primitives/AtomicValue)
  * [Configuration](/docs/latest/user-manual/primitives/AtomicValue#configuration)
  * [Operation](/docs/latest/user-manual/primitives/AtomicValue#operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/AtomicValue#event-notifications)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicValue#cleanup)
* [DistributedCounter](/docs/latest/user-manual/primitives/DistributedCounter)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedCounter#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedCounter#operation)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedCounter#cleanup)
* [DistributedCyclicBarrier](/docs/latest/user-manual/primitives/DistributedCyclicBarrier)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedCyclicBarrier#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedCyclicBarrier#operation)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedCyclicBarrier#cleanup)
* [DistributedList](/docs/latest/user-manual/primitives/DistributedList)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedList#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedList#operation)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/DistributedList#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedList#event-notifications)
  * [Iterators](/docs/latest/user-manual/primitives/DistributedList#iterators)
  * [Streams](/docs/latest/user-manual/primitives/DistributedList#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedList#cleanup)
* [DistributedLock](/docs/latest/user-manual/primitives/DistributedLock)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedLock#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedLock#operation)
  * [Monitoring the Lock State](/docs/latest/user-manual/primitives/DistributedLock#monitoring-the-lock-state)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedLock#cleanup)
* [DistributedMap](/docs/latest/user-manual/primitives/DistributedMap)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedMap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedMap#operation)
  * [Optimistic Locking](/docs/latest/user-manual/primitives/DistributedMap#optimistic-locking)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/DistributedMap#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedMap#event-notifications)
  * [Map Views](/docs/latest/user-manual/primitives/DistributedMap#map-views)
  * [Iterators](/docs/latest/user-manual/primitives/DistributedMap#iterators)
  * [Streams](/docs/latest/user-manual/primitives/DistributedMap#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedMap#cleanup)
* [DistributedMultimap](/docs/latest/user-manual/primitives/DistributedMultimap)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedMultimap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedMultimap#operation)
  * [Optimistic Locking](/docs/latest/user-manual/primitives/DistributedMultimap#optimistic-locking)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/DistributedMultimap#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedMultimap#event-notifications)
  * [Multimap Views](/docs/latest/user-manual/primitives/DistributedMultimap#multimmap-views)
  * [Iterators](/docs/latest/user-manual/primitives/DistributedMultimap#iterators)
  * [Streams](/docs/latest/user-manual/primitives/DistributedMultimap#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedMultimap#cleanup)
* [DistributedMultiset](/docs/latest/user-manual/primitives/DistributedMultiset)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedMultiset#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedMultiset#operation)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/DistributedMultiset#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedMultiset#event-notifications)
  * [Iterators](/docs/latest/user-manual/primitives/DistributedMultiset#iterators)
  * [Streams](/docs/latest/user-manual/primitives/DistributedMultiset#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedMultiset#cleanup)
* [DistributedNavigableMap](/docs/latest/user-manual/primitives/DistributedNavigableMap)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedNavigableMap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedNavigableMap#operation)
  * [Navigable Map Views](/docs/latest/user-manual/primitives/DistributedNavigableMap#navigable-map-views)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedNavigableMap#cleanup)
* [DistributedNavigableSet](/docs/latest/user-manual/primitives/DistributedNavigableSet)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedNavigableSet#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedNavigableSet#operation)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/DistributedNavigableSet#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedNavigableSet#event-notifications)
  * [Iterators](/docs/latest/user-manual/primitives/DistributedNavigableSet#iterators)
  * [Streams](/docs/latest/user-manual/primitives/DistributedNavigableSet#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedNavigableSet#cleanup)
* [DistributedQueue](/docs/latest/user-manual/primitives/DistributedQueue)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedQueue#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedQueue#operation)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/DistributedQueue#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedQueue#event-notifications)
  * [Iterators](/docs/latest/user-manual/primitives/DistributedQueue#iterators)
  * [Streams](/docs/latest/user-manual/primitives/DistributedQueue#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedQueue#cleanup)
* [DistributedSemaphore](/docs/latest/user-manual/primitives/DistributedSemaphore)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedSemaphore#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedSemaphore#operation)
  * [Monitoring the Semaphore State](/docs/latest/user-manual/primitives/DistributedSemaphore#monitoring-the-semaphore-state)
  * [Cleanup](/docs/latest/user-manual/primitives/AtomicSemaphore#cleanup)
* [DistributedSet](/docs/latest/user-manual/primitives/DistributedSet)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedSet#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedSet#operation)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/DistributedSet#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedSet#event-notifications)
  * [Iterators](/docs/latest/user-manual/primitives/DistributedSet#iterators)
  * [Streams](/docs/latest/user-manual/primitives/DistributedSet#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedSet#cleanup)
* [DistributedSortedMap](/docs/latest/user-manual/primitives/DistributedSortedMap)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedSortedMap#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedSortedMap#operation)
  * [Sorted Map Views](/docs/latest/user-manual/primitives/DistributedSortedMap#sorted-map-views)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedSortedMap#cleanup)
* [DistributedSortedSet](/docs/latest/user-manual/primitives/DistributedSortedSet)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedSortedSet#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedSortedSet#operation)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/DistributedSortedSet#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedSortedSet#event-notifications)
  * [Iterators](/docs/latest/user-manual/primitives/DistributedSortedSet#iterators)
  * [Streams](/docs/latest/user-manual/primitives/DistributedSortedSet#streams)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedSortedSet#cleanup)
* [DistributedValue](/docs/latest/user-manual/primitives/DistributedValue)
  * [Configuration](/docs/latest/user-manual/primitives/DistributedValue#configuration)
  * [Operation](/docs/latest/user-manual/primitives/DistributedValue#operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/DistributedValue#event-notifications)
  * [Cleanup](/docs/latest/user-manual/primitives/DistributedValue#cleanup)
* [LeaderElection](/docs/latest/user-manual/primitives/LeaderElection)
  * [Configuration](/docs/latest/user-manual/primitives/LeaderElection#configuration)
  * [Operation](/docs/latest/user-manual/primitives/LeaderElection#operation)
  * [Asynchronous Operation](/docs/latest/user-manual/primitives/LeaderElection#asynchronous-operation)
  * [Event Notifications](/docs/latest/user-manual/primitives/LeaderElection#event-notifications)
  * [Cleanup](/docs/latest/user-manual/primitives/LeaderElection#cleanup)
* [WorkQueue](/docs/latest/user-manual/primitives/WorkQueue)
* [Transactions](/docs/latest/user-manual/primitives/transactions)
  * [Working with Transactions](/docs/latest/user-manual/primitives/transactions#working-with-transactions)
* [Anti-Patterns](/docs/latest/user-manual/primitives/anti-patterns)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/custom-primitives.svg" class="custom-primitives"> Custom Primitives</h3>
<div markdown="1">
{% capture toc %}
* [Overview](/docs/latest/user-manual/custom-primitives/overview)
* [Defining the Primitive Type](/docs/latest/user-manual/custom-primitives/primitive-type)
* [Creating the Primitive Service](/docs/latest/user-manual/custom-primitives/primitive-service)
  * [Service Proxy](/docs/latest/user-manual/custom-primitives/primitive-service#service-proxy)
  * [Client Proxy](/docs/latest/user-manual/custom-primitives/primitive-service#client-proxy)
  * [Defining the Service](/docs/latest/user-manual/custom-primitives/primitive-service#defining-the-service)
  * [Listening for Disconnections](/docs/latest/user-manual/custom-primitives/primitive-service#listening-for-disconnections)
  * [Backing Up the State](/docs/latest/user-manual/custom-primitives/primitive-service#backing-up-the-state)
* [Creating a Proxy](/docs/latest/user-manual/custom-primitives/primitive-proxy)
* [Supplying a Primitive Builder](/docs/latest/user-manual/custom-primitives/primitive-builder)
* [Supporting REST API Access](/docs/latest/user-manual/custom-primitives/primitive-rest-api)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/configuration.svg" class="configuration"> Configuration</h3>
<div markdown="1">
{% capture toc %}
* [Configuration Reference](/docs/latest/user-manual/configuration/configuration/reference)
  * [Atomix Configuration](/docs/latest/user-manual/configuration/reference#atomix-configuration)
  * [Cluster Configuration](/docs/latest/user-manual/configuration/reference#cluster-configuration)
  * [Cluster Discovery Protocols](/docs/latest/user-manual/configuration/reference#cluster-discovery-protocols)
    * [Bootstrap Discovery Protocol](/docs/latest/user-manual/configuration/reference#bootstrap-discovery-protocol)
    * [Multicast Discovery Protocol](/docs/latest/user-manual/configuration/reference#multicast-discovery-protocol)
    * [DNS Discovery Protocol](/docs/latest/user-manual/configuration/reference#dns-discovery-protocol)
  * [Cluster Membership Protocols](/docs/latest/user-manual/configuration/reference#cluster-membership-protocols)
    * [Heartbeat Protocol](/docs/latest/user-manual/configuration/reference#heartbeat-protocol)
    * [SWIM Protocol](/docs/latest/user-manual/configuration/reference#swim-protocol)
  * [Raft](/docs/latest/user-manual/configuration/reference#raft)
    * [Raft Partition Group](/docs/latest/user-manual/configuration/refrence#raft-partition-group)
    * [Multi-Raft Protocol](/docs/latest/user-manual/configuration/reference#multi-raft-protocol)
  * [Primary-Backup](/docs/latest/user-manual/configuration/reference#primary-backup)
    * [Primary-Backup Partition Group](/docs/latest/user-manual/configuration/reference#primary-backup-partition-group)
    * [Multi-Primary Protocol](/docs/latest/user-manual/configuration/reference#multi-primary-protocol)
  * [Distributed Log](/docs/latest/user-manual/configuration/reference#distributed-log)
    * [Log Partition Group](/docs/latest/user-manual/configuration/reference#log-partition-group)
    * [Multi-Log Protocol](/docs/latest/user-manual/configuration/reference#multi-log-protocol)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/serialization.svg" class="serialization"> Serialization</h3>
<div markdown="1">
{% capture toc %}
* [Configuring a Namespace](/docs/latest/user-manual/serialization/configuring-a-namespace)
* [Registering Custom Serializers](/docs/latest/user-manual/serialization/registering-custom-serializers)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/agent.png" class="agent"> Agent</h3>
<div>
{% capture toc %}
* [Running the Agent](/docs/latest/user-manual/agent/running-the-agent)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/deployment.png" class="deployment"> Deployment</h3>
<div>
{% capture toc %}
* [Docker](/docs/latest/user-manual/deployment/docker)
* [Kubernetes](/docs/latest/user-manual/deployment/kubernetes)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/rest.svg" class="rest"> REST API</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Management](/docs/latest/user-manual/rest/cluster-management)
* [Direct Messaging](/docs/latest/user-manual/rest/direct-messaging)
* [Publish-Subscribe Messaging](/docs/latest/user-manual/rest/publish-subscribe-messaging)
* [Distributed Primitives](/docs/latest/user-manual/rest/distributed-primitives)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/python.svg" class="python"> Python API</h3>
<div markdown="1">
{% capture toc %}
* [Setup](/docs/latest/user-manual/python/setup)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/cli.svg" class="cli"> CLI</h3>
<div markdown="1">
{% capture toc %}
* [Setup](/docs/latest/user-manual/cli/setup)
* [Operation](/docs/latest/user-manual/cli/operation)
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/test.svg" class="test"> Test Framework</h3>
<div markdown="1">
{% capture toc %}
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
{% endcapture %}
{{ toc | markdownify }}
</div>

<h3 class="user-guide-menu-header"><img src="/assets/img/icons/architecture.svg" class="architecture"> Architecture</h3>
<div markdown="1">
{% capture toc %}
* [Cluster Communication](/docs/latest/user-manual/architecture/cluster-communication)
* [Group Membership](/docs/latest/user-manual/architecture/group-membership)
* [Partition Groups](/docs/latest/user-manual/architecture/partition-groups)
* [Primitive Protocols](/docs/latest/user-manual/architecture/primitive-protocols)
  * [Raft](/docs/latest/user-manual/architecture/primitive-protocols#raft)
  * [Primary-backup](/docs/latest/user-manual/architecture/primitive-protocols#primary-backup)
{% endcapture %}
{{ toc | markdownify }}
</div>