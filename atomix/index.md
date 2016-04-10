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
<div class="feature gray-background">
  <div class="container">
    <div class="row">

<div class="col-sm-7" markdown="1">
{% include sync-tabs-params.html active="#distributed-value:Value" inactive="#distributed-long:Long,#distributed-map:Map,#distributed-multimap:MultiMap,#distributed-set:Set,#distributed-queue:Queue,#distributed-lock:Lock,#distributed-group:Group Membership,#direct-messaging:Direct Messaging,#publish-subscribe:Publish-Subscribe,#request-reply:Request-Reply,#distributed-leader:Leader Election" %}
<div class="tab-content" markdown="1">
<div class="tab-pane active" id="distributed-value" markdown="1">
```java
// Get or create a DistributedValue and block until the resource is created
DistributedValue<String> value = atomix.getValue("value").join();

// Set the value and wait for completion of the operation
value.set("Hello world!").join();

// Read the value and call the provided callback on response
value.get().thenAccept(result -> {
  System.out.println("The value is " + result);
});
```
</div>
<div class="tab-pane" id="distributed-long" markdown="1">
```java
// Get or create a DistributedLong and block until the resource is created
DistributedLong value = atomix.getLong("long").join();

// Increment the value and call the provided callback on response
value.incrementAndGet().thenAccept(result -> {
  assert result == 1;
});
```
</div>
<div class="tab-pane" id="distributed-map" markdown="1">
```java
// Get or create a DistributedMap and block until the resource is created
DistributedMap<String, String> map = atomix.getMap("map").join();

// Put a value in the map and call the completion callback on response
map.put("bar", "Hello world!").thenRun(() -> {
  // Get the value of the map and block until it's received
  String value = map.get("bar").join();
});
```
</div>
<div class="tab-pane" id="distributed-multimap" markdown="1">
```java
// Get or create a DistributedMultiMap and block until the resource is created
DistributedMultiMap<String, String> multimap = atomix.getMultiMap("multimap").join();

// Put a value in the map and call the completion callback on response
multimap.put("bar", "Hello world!").thenRun(() -> {
  // Put another value in the map and call the completion callback on response
  multimap.put("bar", "Hello world again!").thenRun(() -> {
    // Get the values for the "bar" key and block until received
    Collection<String> values = multimap.get("bar").join();
  });
});
```
</div>
<div class="tab-pane" id="distributed-set" markdown="1">
```java
// Get or create a DistributedSet and block until the resource is created
DistributedSet<String> set = atomix.getSet("set").join();

// Add a value to the set and call the completion callback on response
set.add("foo").thenRun(() -> {
  // Check whether the set contains the added value and block until the response is received
  if (set.contains("foo").join()) {
    // The set contains "foo"
  }
});
```
</div>
<div class="tab-pane" id="distributed-queue" markdown="1">
```java
// Get or create a DistributedQueue and block until the resource is created
DistributedQueue<Integer> queue = atomix.getQueue("queue").join();

// Add two values to the queue and block until both are added
CompletableFuture.allOf(queue.offer(1), queue.offer(2)).join();

// Pull the first item off the queue and call the completion callback once it's received
queue.poll().thenAccept(value -> {
  System.out.println("retrieved " + value);
});
```
</div>
<div class="tab-pane" id="distributed-lock" markdown="1">
```java
// Get or create a DistributedLock and block until the resource is created
DistributedLock lock = atomix.getLock("foo").join();

// Acquire the lock and call the completion callback once the lock is acquired
lock.lock().thenRun(() -> {
  System.out.println("Acquired a lock!");

  // Release the lock and block until complete
  lock.unlock().join();
});
```
</div>
<div class="tab-pane" id="distributed-group" markdown="1">
```java
// Get or create a DistributedGroup and block until the resource is created
DistributedGroup group = atomix.getGroup("group").join();

// Join the group and block until the join is complete
LocalMember member = group.join().join();

// When a member joins the group, print a message
group.onJoin(member -> {
  System.out.println(member + " joined the group");
});

// Iterate over the set of members in the group
group.members().forEach(member -> {
  // ...
});
```
</div>
<div class="tab-pane" id="distributed-leader" markdown="1">
```java
// Get or create a DistributedGroup and block until the resource is created
DistributedGroup group = atomix.getGroup("group").join();

// Register an election listener
group.election().onElection(term -> {
  System.out.println(term.leader() + " elected leader for term " + term.term());
});

// Join the group to get elected leader
LocalMember member = group.join().join();
```
</div>
<div class="tab-pane" id="direct-messaging" markdown="1">
```java
// Get or create a DistributedGroup and block until the resource is created
DistributedGroup group = atomix.getGroup("group").join();

// Get a member of the group by name
Member member = group.member("foo");

// Create a direct synchronous message producer
MessageProducer.Options options = new MessageProducer.Options()
  .withExecution(Execution.SYNC)
  .withDelivery(Delivery.DIRECT);
MessageProducer<String> producer = member.messaging().producer("hello");

// Send a direct message to the member and await acknowledgement
producer.send("Hello world!").thenAccept(reply -> {
  System.out.println(reply);
});

// Join the group and block until the join is complete
LocalMember localMember = group.join().join();

// Create a message consumer and ack messages when received for this member
MessageConsumer<String> consumer = localMember.messaging().consumer("hello");
consumer.onMessage(message -> {
  // ...
  message.ack();
});
```
</div>
<div class="tab-pane" id="publish-subscribe" markdown="1">
```java
// Get or create a DistributedGroup and block until the resource is created
DistributedGroup group = atomix.getGroup("group").join();

// Create an asynchroous broadcast message producer
MessageProducer.Options options = new MessageProducer.Options()
  .withExecution(Execution.ASYNC)
  .withDelivery(Delivery.BROADCAST);
MessageProducer<String> producer = group.messaging().producer("events", options);

// Publish a message to all members of the group
producer.send("change").thenRun(() -> {
  // Change event has been published
});

// Join the group and block until the join is complete
LocalMember localMember = group.join().join();

// Create a message consumer and ack messages when received for this member
MessageConsumer<String> consumer = localMember.messaging().consumer("events");
consumer.onMessage(message -> {
  if (message.body().equals("change")) {
    message.ack();
  }
});
```
</div>
<div class="tab-pane" id="request-reply" markdown="1">
```java
// Get or create a DistributedGroup and block until the resource is created
DistributedGroup group = atomix.getGroup("group").join();

// Get a member of the group by name
Member member = group.member("foo");

// Create a direct request-reply message producer
MessageProducer.Options options = new MessageProducer.Options()
  .withExecution(Execution.REQUEST_REPLY);
MessageProducer<String> producer = member.messaging().producer("hello");

// Send a message to the member and await a reply
producer.send("Hello world!").thenAccept(reply -> {
  System.out.println(reply);
});

// Join the group and block until the join is complete
LocalMember localMember = group.join().join();

// Create a message consumer for messages sent to this member
MessageConsumer<String> consumer = localMember.messaging().consumer("hello");
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
<div class="feature white-background">
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
<div class="feature gray-background">
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
<div class="feature white-background">
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
  .join();
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