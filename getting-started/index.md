---
layout: content
menu: getting-started
title: Getting Started
---

# Getting Started

The high-level [Copycat API](#the-copycat-api) is a single interface that aids in managing stateful resources
(e.g. maps, sets, locks, leader elections) in a distributed system. The `Copycat` API is heavily influenced by
[Hazelcast's](http://hazelcast.org/) API.

The one critical method in Copycat's high-level API is the `create` method. The `create` method gets or creates a
user-defined distributed resource.

{:.java}
	copycat.create("test-lock", DistributedLock.class).thenAccept(lock -> {
	  // Do stuff...
	});

Copycat's API is fully asynchronous and relies heavily on Java 8's [CompletableFuture][CompletableFuture].

#### DistributedMap

{:.java}
	DistributedMap<String, String> map = copycat.create("test-map", DistributedMap.class).get();
	
	map.put("key", "value").thenRun(() -> {
	  map.get("key").thenAccept(value -> {
	    if (value.equals(value)) {
	      // Set a key with a TTL
	      map.putIfAbsent("otherkey", "othervalue", Duration.ofSeconds(1)).get();
	    }
	  });
	});

#### DistributedSet

{:.java}
	DistributedSet<String> set = copycat.create("test-set", DistributedSet.class).get();
	
	set.add("value").thenRun(() -> {
	  set.contains("value").thenAccept(result -> {
	    if (result) {
	      // Add a value with a TTL
	      set.add("othervalue", Duration.ofSeconds(1));
	    }
	  });
	});

#### DistributedLock

{:.java}
	DistributedLock lock = copycat.create("test-lock", DistributedLock.class).get();
	
	lock.lock().thenRun(() -> {
	  // Do stuff...
	  lock.unlock().thenRun(() -> {
	    // Did stuff
	  });
	});

#### DistributedLeaderElection

{:.lang-java}
	DistributedLeaderElection election = copycat.create("test-election", DistributedLeaderElection.class).get();
	
	election.onElection(epoch -> {
	  System.out.println("Elected leader!");
	});