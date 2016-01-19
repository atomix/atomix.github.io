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
{% include sync-tabs-params.html active="#distributed-value:Value" inactive="#distributed-long:Long,#distributed-map:Map,#distributed-multimap:MultiMap,#distributed-set:Set,#distributed-queue:Queue,#distributed-lock:Lock,#distributed-group:Membership Group,#distributed-leader:Leader Election,#distributed-bus:Message Bus" %}
<div class="tab-content" markdown="1">
<div class="tab-pane active" id="distributed-value" markdown="1">
```java
DistributedValue<String> value = atomix.getValue("value").get();

value.set("Hello world!").thenRun(() -> {
  value.get().thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```
</div>
<div class="tab-pane" id="distributed-long" markdown="1">
```java
DistributedLong value = atomix.getLong("long").get();

value.incrementAndGet().thenAccept(result -> {
  assert result == 1;
});
```
</div>
<div class="tab-pane" id="distributed-map" markdown="1">
```java
DistributedMap<String, String> map = atomix.getMap("map").get();

map.put("bar", "Hello world!").thenRun(() -> {
  map.get("bar").thenAccept(result -> {
    assert result.equals("Hello world!");
  });
});
```
</div>
<div class="tab-pane" id="distributed-multimap" markdown="1">
```java
DistributedMultiMap<String, String> multimap = atomix.getMultiMap("multimap").get();

multimap.put("bar", "Hello world!").thenRun(() -> {
  multimap.put("bar", "Hello world again!").thenRun(() -> {
    multimap.get("bar").thenAccept(values -> {
      values.forEach(value -> System.out.println(value));
    });
  });
});
```
</div>
<div class="tab-pane" id="distributed-set" markdown="1">
```java
DistributedSet<String> set = atomix.getSet("set").get();

set.add("foo").thenRun(() -> {
  set.contains("foo").thenAccept(result -> {
    if (result) {
      System.out.println("set contains 'foo'");
    }
  });
});
```
</div>
<div class="tab-pane" id="distributed-queue" markdown="1">
```java
DistributedQueue<Integer> queue = atomix.getQueue("queue").get();

queue.offer(1).join();
queue.offer(2).join();
queue.poll().thenAccept(value -> {
  System.out.println("retrieved " + value);
});
```
</div>
<div class="tab-pane" id="distributed-lock" markdown="1">
```java
DistributedLock lock = atomix.getLock("foo").get();

lock.lock().thenRun(() -> {
  System.out.println("Acquired a lock!");
  lock.unlock();
});
```
</div>
<div class="tab-pane" id="distributed-group" markdown="1">
```java
DistributedMembershipGroup group = atomix.getMembershipGroup("group").get();

group.join().thenRun(() -> System.out.println("Join successful"));

group.onJoin(member -> System.out.println(member.id() + " joined the group"));
```
</div>
<div class="tab-pane" id="distributed-leader" markdown="1">
```java
DistributedMembershipGroup group = atomix.getMembershipGroup("election").get();

LocalGroupMember member = group.join().get();
member.onElection(term -> {
  System.out.println("Elected leader!");
  member.resign();
});
```
</div>
<div class="tab-pane" id="distributed-bus" markdown="1">
```java
DistributedMessageBus bus = atomix.getMessageBus("bus").get();

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