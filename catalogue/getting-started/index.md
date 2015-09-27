---
layout: content
menu: getting-started
title: Getting Started
pitch: Copycat in two minutes
first-section: getting-started
---

The high-level [Copycat API](/user-manual/copycat-api#the-copycat-api) is a single interface that aids in managing stateful resources (e.g. maps, sets, locks, leader elections) in a distributed system. The `Copycat` API is heavily influenced by [Hazelcast's](http://hazelcast.org/) API.

The one critical method in Copycat's high-level API is the `create` method. The `create` method gets or creates a user-defined distributed resource.

```java
copycat.create("test-lock", DistributedLock.class).thenAccept(lock -> {
  // Do stuff...
});
```

Copycat's API is fully asynchronous and relies heavily on Java 8's [CompletableFuture][CompletableFuture].

{% include sync-top-tabs.html %}

### DistributedMap

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
DistributedMap<String, String> map = copycat.create("test-map", DistributedMap.class).get();

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
DistributedMap<String, String> map = copycat.create("test-map", DistributedMap.class).thenAccept(map -> {
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
DistributedSet<String> set = copycat.create("test-set", DistributedSet.class).get();

set.add("value").join();

if (set.contains("value").get()) {
  set.add("othervalue", Duration.ofSeconds()).join();
}
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
DistributedSet<String> set = copycat.create("test-set", DistributedSet.class).thenAccept(set -> {
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
DistributedLock lock = copycat.create("test-lock", DistributedLock.class).get();

// Lock the lock
lock.lock().join();

// Unlock the lock
lock.unlock().join();
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
DistributedLock lock = copycat.create("test-lock", DistributedLock.class).thenAccept(lock -> {
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
DistributedLeaderElection election = copycat.create("test-election", DistributedLeaderElection.class).get();

election.onElection(epoch -> {
  System.out.println("Elected leader!");
}).join();
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
DistributedLeaderElection election = copycat.create("test-election", DistributedLeaderElection.class).thenAccept(election -> {
  election.onElection(epoch -> {
    System.out.println("Elected leader!");
  }).thenRun(() -> {
    System.out.println("Waiting for election");
  });
});
```
</div>
</div>

[CompletableFuture]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html