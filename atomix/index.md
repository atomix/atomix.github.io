---
layout: project-index
project: atomix
---

<!-- Reliable -->
<div class="highlight highlight-white">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Reliable</h2>
        <p>Atomix features reliable data consistency guarantees that are maintained even when machine or network failures occur.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/reliable14.svg">
      </div>
    </div>
  </div>
</div>

<!-- Simple -->
<div class="highlight highlight-gray">
  <div class="container">
    <div class="row">
    
<div class="col-sm-7" markdown="1">
{% include sync-tabs-params.html active="#distributed-value:Value" inactive="#distributed-map:Map,#distributed-lock:Lock,#distributed-leader:Leader Election,#distributed-group:Group,#distributed-bus:Bus" %}
<div class="tab-content" markdown="1">
<div class="tab-pane active" id="distributed-value" markdown="1">
```java
DistributedValue<String> value = 
  atomix.create("value", DistributedValue::new).get();

value.set("Hello world!").thenRun(() -> {
  value.get().thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```
</div>
<div class="tab-pane" id="distributed-map" markdown="1">
```java
DistributedMap<String, String> map = 
  atomix.create("map", DistributedMap::new).get();

map.put("foo", "Hello world!").thenRun(() -> {
  map.get("foo").thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```
</div>
<div class="tab-pane" id="distributed-lock" markdown="1">
```java
DistributedLock lock = 
  atomix.create("lock", DistributedLock::new).get();

lock.lock().thenRun(() -> System.out.println("Acquired a lock!"));
```
</div>
<div class="tab-pane" id="distributed-leader" markdown="1">
```java
DistributedLeaderElection election = 
  atomix.create("election", DistributedLeaderElection::new).get();

election.onElection(epoch -> System.out.println("Elected leader!"));
```
</div>
<div class="tab-pane" id="distributed-group" markdown="1">
```java
DistributedMembershipGroup group = 
  atomix.create("group", DistributedMembershipGroup::new).get();

group.join().thenRun(() -> System.out.println("Join successful"));

group.onJoin(member -> System.out.println(member.id() + " joined the group"));
```
</div>
<div class="tab-pane" id="distributed-bus" markdown="1">
```java
DistributedMessageBus bus = 
  atomix.create("bus", DistributedMessageBus::new).get();

bus.open(new Address("123.456.789.0", 5000)).join();

bus.producer("foo").send("hello").get();

bus.consumer("foo", message -> System.out.println("Consumed " + message));
```
</div>
</div>
</div>
    <div class="col-sm-5 text-right">
      <h2>Simple</h2>
      <p>Atomix provides dead simple, asynchronous APIs for managing powerful distributed resources.</p>
    </div>
    </div>
  </div>
</div>

<!--Resilient -->
<div class="highlight highlight-white">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Resilient</h2>
        <p>Atomix clusters are resilient to failure, automatically replacing cluster members as needed without any data loss.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/resilient.svg">
      </div>
    </div>
  </div>
</div>

<div class="highlight highlight-gray">
  <div class="container">
    <div class="row">
<div class="col-sm-6" markdown="1">
```java
AtomixReplica replica = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(StorageLevel.DISK))
  .build()
  .open()
  .get();
```
</div>
      <div class="col-sm-6 text-right">
        <h2>Embeddable</h2>
        <p>Atomix supports fully embeddable replicas that live in-process, eliminating the need to manage external coordination services.</p>
      </div>
    </div>
  </div>
</div>

<!--Learn more -->
<div class="highlight highlight-get-started">
  <div class="container">
    <div class="row">
      <div class="col-sm-12 text-center">
        <h2>Ready to learn more?</h2>
        <p>
          <a href="/{{ page.project }}/getting-started" class="btn btn-default btn-lg doc-btn">Get Started</a>
          <a href="/{{ page.project }}/user-manual" class="btn btn-default btn-lg doc-btn">User Manual</a>
        </p>
      </div>
    </div>
  </div>
</div>