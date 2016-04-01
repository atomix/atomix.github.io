---
layout: project
project: atomix
---

<div class="feature intro">
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <p>
Atomix is an event-driven framework for coordinating fault-tolerant distributed systems built on the Raft consensus algorithm. It provides the building blocks that solve many common distributed systems problems including group membership, leader election, distributed concurrency control, partitioning, and replication.
        </p>
      </div>
    </div>
  </div>
</div>

<!-- Simple -->
<div class="feature white-background">
  <div class="container">
    <div class="row">

<div class="col-sm-7" markdown="1">
{% include sync-tabs-params.html active="#distributed-value:Value" inactive="#distributed-long:Long,#distributed-map:Map,#distributed-multimap:MultiMap,#distributed-set:Set,#distributed-queue:Queue,#distributed-lock:Lock,#distributed-group:Group Membership,#task-queue:Task Queue,#direct-messaging:Direct Messaging,#distributed-leader:Leader Election" %}
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

group.election().onElection(term -> {
  System.out.println(term.leader() + " elected leader for term " + term.term());
});
```
</div>
<div class="tab-pane" id="task-queue" markdown="1">
```java
DistributedGroup group = atomix.getGroup("group").get();

Member member = group.member("foo");

TaskProducer<String> producer = member.tasks().producer("work");
producer.submit("doIt").thenRun(() -> {
  System.out.println("Task complete!");
});

LocalMember localMember = group.join().get();

TaskConsumer<String> consumer = localMember.tasks().consumer("work");
consumer.onTask(task -> {
  try {
    doWork();
    task.ack();
  } catch (Exception e) {
    task.fail();
  }
});
```
</div>
<div class="tab-pane" id="direct-messaging" markdown="1">
```java
DistributedGroup group = atomix.getGroup("group").get();

Member member = group.member("foo");

MessageProducer<String> producer = member.messages().producer("hello");
producer.send("Hello world!").thenAccept(reply -> {
  System.out.println(reply);
});

LocalMember localMember = group.join().get();

MessageConsumer<String> consumer = localMember.messages().consumer("hello");
consumer.onMessage(message -> {
  if (message.body().equals("Hello world!")) {
    messages.reply("Hello world back!");
  }
});
```
</div>
</div>
</div>
    <div class="col-sm-5 text-right">
      <h2>Simple</h2>
      <p>Atomix provides a collection of dead simple, asynchronous APIs for sharing mission critical state and solving a variety of common distributed systems problems.</p>
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

<!--Resilient -->
<div class="feature white-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-5 col-sm-offset-1">
        <img class="svg" src="/assets/img/icons/resilient.svg">
      </div>
      <div class="col-sm-6 text-right">
        <h2>Resilient</h2>
        <p>Atomix clusters are resilient to failure, automatically replacing failed replicas as needed without any data loss.</p>
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

<script type='text/javascript'>
// Format tabs
$(function(){
  var $container = $('#sync-tabs');
  
  updateTabs($container);
  $(window).resize(function(){
    updateTabs($container);
  })
  
  function updateTabs($tabsContainer){
      var $containerWidth = $tabsContainer.width();
      var tabWidths = [];
      var $tabs = $tabsContainer.find('li');
      $tabs.each(function(index, tab){
        tabWidths.push($(tab).width());
      });

      var formattedTabs = [];
      var maxWidth = $containerWidth;
      var maxWidthSet = false;
      var rowWidth = 0;
      for(var i = tabWidths.length - 1; i >= 0; i--){
          var tabWidth = tabWidths[i];
          if(rowWidth + tabWidth > maxWidth){
            if(!maxWidthSet){
              maxWidth = rowWidth;
              maxWidthSet = true;
            }
            rowWidth = tabWidth;
            formattedTabs.unshift($('<div class="spacer"></div>'));
          }else{
            rowWidth += tabWidth;
          }
          formattedTabs.unshift($tabs.get(i));
      }

      var $tempContainer = $('<div></div>');
      formattedTabs.forEach(function(tab, index){
        $tempContainer.append(tab);
      });
      $tabsContainer.html($tempContainer.html());
  }
});
</script>