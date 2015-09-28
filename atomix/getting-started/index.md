---
layout: content
project: atomix
menu: getting-started
title: Getting Started
pitch: Atomix in two minutes
first-section: getting-started
---

The high-level [Atomix API](/user-manual/atomix-api#the-atomix-api) is a single interface that aids in managing stateful resources (e.g. maps, sets, locks, leader elections) in a distributed system. The `Atomix` API is heavily influenced by [Hazelcast's][Hazelcast] API.

The one critical method in Atomix's high-level API is the `create` method. The `create` method gets or creates a user-defined distributed resource.

```java
atomix.create("test-lock", DistributedLock.class).thenAccept(lock -> {
  // Do stuff...
});
```

Atomix's API is fully asynchronous and relies heavily on Java 8's [CompletableFuture].

{% include sync-top-tabs.html %}

### DistributedMap

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
DistributedMap<String, String> map = atomix.create("test-map", DistributedMap.class).get();

map.put("key", "value").join();

String value = map.get("key").get();

if (value.equals("value")) {
  map.putIfAbsent("otherkey", "othervalue", Duration.ofSeconds(1)).join();
}
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
DistributedMap<String, String> map = atomix.create("test-map", DistributedMap.class).thenAccept(map -> {
  map.put("key", "value").thenRun(() -> {
    map.get("key").thenAccept(value -> {
      if (value.equals("value")) {
        // Set a key with a TTL
        map.putIfAbsent("otherkey", "othervalue", Duration.ofSeconds(1)).get();
      }
    });
  });
});
```
</div>
</div>

### DistributedSet

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
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
DistributedSet<String> set = atomix.create("test-set", DistributedSet.class).thenAccept(set -> {
  set.add("value").thenRun(() -> {
    set.contains("value").thenAccept(result -> {
      if (result) {
        // Add a value with a TTL
        set.add("othervalue", Duration.ofSeconds(1));
      }
    });
  });
});
```
</div>
</div>

### DistributedLock

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
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
DistributedLock lock = atomix.create("test-lock", DistributedLock.class).thenAccept(lock -> {
  lock.lock().thenRun(() -> {
    // Do stuff...
    lock.unlock().thenRun(() -> {
      // Did stuff
    });
  });
});
```
</div>
</div>

### DistributedLeaderElection

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
DistributedLeaderElection election = atomix.create("test-election", DistributedLeaderElection.class).get();

election.onElection(epoch -> {
  System.out.println("Elected leader!");
}).join();
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
DistributedLeaderElection election = atomix.create("test-election", DistributedLeaderElection.class).thenAccept(election -> {
  election.onElection(epoch -> {
    System.out.println("Elected leader!");
  }).thenRun(() -> {
    System.out.println("Waiting for election");
  });
});
```
</div>
</div>

{% include common-links.html %}