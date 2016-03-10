---
layout: project
project: atomix
---

<div class="feature intro">
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <p>
Atomix is an embeddable library that provides strong, fault-tolerant consistency for stateful resources in your distributed application, along with a high-level API for creating and managing custom user-defined resources where fault-tolerance and consistency is provided automatically.
        </p>
      </div>
    </div>
  </div>
</div>

<!-- Reliable -->
<div class="feature gray-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Reliable</h2>
        <p>Atomix features reliable data consistency guarantees that are maintained even when machine or network failures occur.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/icons/reliable.svg">
      </div>
    </div>
  </div>
</div>

<!-- Simple -->
<div class="feature white-background">
  <div class="container">
    <div class="row">
    
<div class="col-sm-7" markdown="1">
{% include sync-tabs-params.html active="#distributed-value:Value" inactive="#distributed-long:Long,#distributed-map:Map,#distributed-multimap:MultiMap,#distributed-set:Set,#distributed-queue:Queue,#distributed-lock:Lock,#distributed-group:Group,#distributed-bus:Message Bus,#distributed-topic:Topic,#distributed-task-queue:Task Queue,#distributed-leader:Leader Election,#consistent-hashing:Consistent Hashing,#remote-execution:Remote Execution" %}
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
DistributedGroup group = atomix.getGroup("group").get();

group.join().thenAccept(member -> {
  System.out.println("Joined with member ID: " + member.id());
});

group.onJoin(member -> {
  System.out.println(member + " joined the group");
});
```
</div>
<div class="tab-pane" id="distributed-leader" markdown="1">
```java
DistributedGroup group = atomix.getGroup("group").get();

group.election().onElection(leader -> {
  System.out.println("Elected leader: " + leader);
});
```
</div>
<div class="tab-pane" id="consistent-hashing" markdown="1">
```java
DistributedGroup.Config config = DistributedGroup.config()
  .withPartitions(32)
  .withVirtualNodes(200)
  .withReplicationFactor(3);

DistributedGroup group = atomix.getGroup("group", config);
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
<div class="tab-pane" id="distributed-topic" markdown="1">
```java
DistributedTopic<String> topic = atomix.getTopic("topic").get();

topic.onMessage(message -> System.out.println("Got message: " + message));

topic.publish("Hello world!").thenRun(() -> System.out.println("Published!"));
```
</div>
<div class="tab-pane" id="distributed-task-queue" markdown="1">
```java
DistributedTaskQueue<String> queue = atomix.getTaskQueue("tasks").get();

queue.consumer(task -> {
  System.out.println("Received " + task);
});

queue.submit("work task");
```
</div>
<div class="tab-pane" id="remote-execution" markdown="1">
```java
DistributedGroup group = atomix.getGroup("election").get();

group.join().join();

group.members().forEach(member -> {
  member.execute(() -> System.out.println("On member " + member.id());
});
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

<!--Scalable -->
<div class="feature gray-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Scalable</h2>
        <p>Copycat scales along with the rest of your system, providing high read throughput while maintaining strong write consistency.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/icons/scalable.svg">
      </div>
    </div>
  </div>
</div>

<!--Resilient -->
<div class="feature white-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-5 col-sm-offset-1">
        <img class="svg" src="/assets/img/icons/resilient.svg">
      </div>
      <div class="col-sm-6 text-right">
        <h2>Resilient</h2>
        <p>Atomix clusters are resilient to failure, automatically replacing cluster members as needed without any data loss.</p>
      </div>
    </div>
  </div>
</div>

<!-- Embeddable -->
<!-- <div class="feature gray-background">
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
</div> -->

<!--Learn more -->
<div class="feature get-started">
  <div class="container">
    <div class="row">
      <div class="col-sm-12 text-center">
        <h2>Ready to learn more?</h2>
        <p>
          <a href="/{{ page.project }}/docs/getting-started" class="btn btn-default btn-lg doc-btn">Get Started</a>
        </p>
      </div>
    </div>
  </div>
</div>