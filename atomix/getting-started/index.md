---
layout: content
project: atomix
menu: getting-started
title: Getting Started
pitch: Atomix in two minutes
first-section: getting-started
---

The high-level [Atomix API](/user-manual/atomix-api#the-atomix-api) is a single interface that aids in managing stateful resources (e.g. maps, sets, locks, leader elections) in a distributed system. The `Atomix` API is heavily influenced by [Hazelcast's][Hazelcast] API.

{% include sync-top-tabs.html %}

### DistributedMap

The `DistributedMap` resource provides a fully asynchronous and distributed implementation with an interface very similar to Java's `Map`.

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and block until it has found the cluster leader
atomix.open().join();

// Create a distributed map and block until it has been registered with the cluster
DistributedMap<String, String> map = atomix.create("test-map", DistributedMap.class).get();

// Put a key in the map and block until the operation has completed
map.put("key", "value").join();

// Get the value of "key" from the map and block waiting for the result
String value = map.get("key").get();

if (value.equals("value")) {
  // Put a value in the map with a TTL
  map.putIfAbsent("otherkey", "othervalue", Duration.ofSeconds(1)).join();
}
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and call the callback once it's open
atomix.open().thenRun(() -> {

  // Create a distributed map
  atomix.<DistributedMap<String, String>>create("test-map", DistributedMap.class).thenAccept(map -> {
  
    // Put a key in the map and call the following callback once complete
    map.put("key", "value").thenRun(() -> {
      // Get the "key" from the map and call the accept callback once complete
      map.get("key").thenAccept(value -> {
        if (value.equals("value")) {
          // Set a key with a TTL
          map.putIfAbsent("otherkey", "othervalue", Duration.ofSeconds(1)).get();
        }
      });
    });
  });

});
```
</div>
</div>

### DistributedMultiMap

The `DistributedMultiMap` resource provides a fully asynchronous interface that facilitates associating multiple values with each key in a map.

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and block until it has found the cluster leader
atomix.open().join();

// Create a distributed map and block until it has been registered with the cluster
DistributedMultiMap<String, String> multiMap = atomix.create("test-multimap", DistributedMultiMap.class).get();

// Put a set of values in the map for the "key" key and block until the operations have completed
multiMap.put("key", "value").join();
multiMap.put("key", "other").join();

// Get the value of "key" from the map and block waiting for the result
Collection<String> value = multiMap.get("key").get();

if (value.contains("value")) {
  // Put a value in the map with a TTL
  multiMap.putIfAbsent("otherkey", "othervalue", Duration.ofSeconds(1)).join();
}
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and call the callback once it's open
atomix.open().thenRun(() -> {

  // Create a distributed multimap
  atomix.<DistributedMultiMap<String, String>>create("test-multimap", DistributedMultiMap.class).thenAccept(multiMap -> {
    // Put two values in the "key" key concurrently and call the run callback once complete
    CompletableFuture<String> future1 = multiMap.put("key", "value1");
    CompletableFuture<String> future2 = multiMap.put("key", "value2");

    // Once both operations have completed successfully, check the value
    CompletableFuture.allOf(future1, future2).thenRun(() -> {
      multiMap.get("key").thenAccept(values -> {
        if (values.contains("value1")) {
          multiMap.putIfAbsent("other", "value", Duration.ofSeconds(1));
        }
      });
    });
  });
});
```
</div>
</div>

### DistributedSet

The `DistributedSet` resource provides a fully asynchronous and distributed implementation with an interface very similar to Java's `Set`.

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and block until it has found the cluster leader
atomix.open().join();

// Create a set and block until it has been registered with the cluster
DistributedSet<String> set = atomix.create("test-set", DistributedSet.class).get();

set.add("value").join();

if (set.contains("value").get()) {
  set.add("othervalue", Duration.ofSeconds()).join();
}
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and call the callback once it's open
atomix.open().thenRun(() -> {

  // Create a distributed set.
  atomix.<DistributedSet<String>>create("test-set", DistributedSet.class).thenAccept(set -> {

    // Add a value to the set and, once complete, check the value
    set.add("value").thenRun(() -> {
      set.contains("value").thenAccept(result -> {
        if (result) {
          // Add a value with a TTL
          set.add("othervalue", Duration.ofSeconds(1));
        }
      });
    });
  });
});
```
</div>
</div>

### DistributedQueue

The `DistributedQueue` resource provides a fully asynchronous and distributed implementation with an interface very similar to Java's `Queue`.

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and block until it has found the cluster leader
atomix.open().join();

// Create a distributed queue
DistributedQueue<String> queue = atomix.<DistributedQueue<String>>create("test-queue", DistributedQueue::new).get();

// Add a value to the queue and block until complete
queue.add("value").join();

// Pop a value off of the queue and block for the result
String value = queue.poll().get();
assert value.equals("value");
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and call the callback once it's open
atomix.open().thenRun(() -> {

  // Create a distributed queue.
  atomix.<DistributedQueue<String>>create("test-set", DistributedQueue.class).thenAccept(queue -> {

    // Add a value to the set and, once complete, poll the queue
    queue.add("value").thenRun(() -> {
      queue.poll().thenAccept(value -> {
        System.out.println("value is: " + value);
      });
    });
  });
});
```
</div>
</div>

### DistributedLock

The `DistributedLock` resource provides a fully asynchronous and distributed implementation with an interface very similar to Java's `Lock`. It guarantees that no two `DistributedLock` instances will believe themselves to be the lock holder simultaneously.

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and block until it has found the cluster leader
atomix.open().join();

// Create a distributed lock and block until complete
DistributedLock lock = atomix.create("test-lock", DistributedLock.class).get();

// Lock the lock
lock.lock().join();

// Unlock the lock
lock.unlock().join();
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and call the callback once it's open
atomix.open().thenRun(() -> {

  // Create a distributed lock and call the callback once it has been created
  atomix.create("test-lock", DistributedLock.class).thenAccept(lock -> {
    // Lock the lock and call the callback once the lock has been acquired
    lock.lock().thenRun(() -> {
      // Do stuff...
      lock.unlock().thenRun(() -> {
        // Did stuff
      });
    });
  });
});
```
</div>
</div>

### DistributedLeaderElection

The `DistributedLeaderElection` resource facilitates electing a leader from a set of leader election instances distributed within a cluster. It guarantees that no two resource instances will believe themselves to be the leader simultaneously.

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and block until it has found the cluster leader
atomix.open().join();

// Create a distributed leader election and block until it has been registered in the cluster
DistributedLeaderElection election = atomix.create("test-election", DistributedLeaderElection.class).get();

// Register an election handler and block until the handler has been registered in the cluster
election.onElection(epoch -> {
  System.out.println("Elected leader!");
}).join();
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and call the callback once it's open
atomix.open().thenRun(() -> {

  // Create a distributed leader election.
  atomix.create("test-election", DistributedLeaderElection.class).thenAccept(election -> {
    // Register an election handler and once complete log a message indicating we're waiting to become the leader
    election.onElection(epoch -> {
      System.out.println("Elected leader!");
    }).thenRun(() -> {
      System.out.println("Waiting for election");
    });
  });
});
```
</div>
</div>

### DistributedMembershipGroup

The `DistributedMembershipGroup` resource facilitates tracking group/cluster membership in a distributed system. Instances of the resource can join and leave the group, and other members will be notified.

{% include common-links.html %}

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and block until it has found the cluster leader
atomix.open().join();

// Create a distributed membership group and block until it has been created
DistributedMembershipGroup group = atomix.create("test-group", DistributedMembershipGroup::new).get();

// Join the membership group and block until the join is complete
group.join().join();

// Execute a callback on a member and block until complete
GroupMember member = group.members().iterator().next();
member.execute(() -> System.out.println("I'm printed on member " + member.id()).join();

// Register a listener to be called when a member joins the membership group
group.onJoin(member -> {
  // Schedule a callback to be executed on the member in 10 seconds
  member.schedule(Duration.ofSeconds(10), () -> System.out.println("I'm printed in 10 seconds on member " + member.id()));
});

// Leave the membership group and block until the leave is complete
group.leave().join();
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and call the callback once it's open
atomix.open().thenRun(() -> {

  // Create a distributed membership group and block until it has been created
  atomix.create("test-group", DistributedMembershipGroup::new).thenAccept(group -> {
  
    // Join the membership group and block until the join is complete
    group.join().thenRun(() -> {
      // Execute a callback on a member
      GroupMember member = group.members().iterator().next();
      member.execute(() -> System.out.println("I'm printed on member " + member.id());
      
      // Register a listener to be called when a member joins the membership group
      group.onJoin(member -> {
        // Schedule a callback to be executed on the member in 10 seconds
        member.schedule(Duration.ofSeconds(10), () -> System.out.println("I'm printed in 10 seconds on member " + member.id())).thenRun(() -> {
          System.out.println("Message printed on member " + member.id());
        });
      });
      
      // Leave the membership group and block until the leave is complete
      group.leave().thenRun(() -> System.out.println("Left the group"));
    });
  });
});
```
</div>
</div>

### DistributedMessageBus

The `DistributedMessageBus` resource facilitates direct messaging between instances of the resource within the cluster.

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
// Create a replica and connect it to a set of existing members
Atomix atomix = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(new StorageLevel.MEMORY))
  .build();

// Open the replica and block until it has found the cluster leader
atomix.open().join();

// Create a distributed message bus and block until it has been registered with the cluster
DistributedMessageBus bus = atomix.create("bus", DistributedMessageBus::new).get();

// Open the message bus server at localhost:5000 and block until the server has started
bus.open(new Address("localhost", 5000)).join();

// Register a message consumer and block until the registration is complete
bus.consumer("foo", message -> {
  System.out.println("Got: " + message);
}).join();

// Create a producer and send a message to the "foo" consumer and block until it has been received
Producer<String> producer = bus.producer("foo").get();
producer.send("Hello world!").join();
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
// Create a distributed message bus
atomix.create("bus", DistributedMessageBus::new).thenAccept(bus -> {

  // Register a named consumer and, once complete, send a message to the consumer
  bus.consumer("foo", message -> System.out.println("Got: " + message)).thenRun(() -> {
    bus.producer("foo").thenAccept(producer -> {
      producer.send("Hello world!");
    });
  });

});
```
</div>
</div>
