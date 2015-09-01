---
layout: content
menu: getting-started
title: Getting Started
---

The high-level [Copycat API](#the-copycat-api) is a single interface that aids in managing stateful resources (e.g. maps, sets, locks, leader elections) in a distributed system. The `Copycat` API is heavily influenced by [Hazelcast's](http://hazelcast.org/) API.

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

[Javadoc]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/
[CAP]: https://en.wikipedia.org/wiki/CAP_theorem
[Raft]: https://raft.github.io/
[Executor]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/Executor.html
[CompletableFuture]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html
[collections]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections.html
[atomic]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/atomic.html
[coordination]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination.html
[copycat]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat.html
[protocol]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol.html
[io]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io.html
[serializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer.html
[transport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport.html
[storage]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage.html
[utilities]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util.html
[Copycat]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/Copycat.html
[CopycatReplica]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/CopycatReplica.html
[CopycatClient]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/CopycatClient.html
[Resource]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/Resource.html
[Transport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/Transport.html
[LocalTransport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/LocalTransport.html
[NettyTransport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/NettyTransport.html
[Storage]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage/Storage.html
[Log]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage/Log.html
[Buffer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/Buffer.html
[BufferReader]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/BufferReader.html
[BufferWriter]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/BufferWriter.html
[Serializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/Serializer.html
[CopycatSerializable]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/CopycatSerializable.html
[TypeSerializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/TypeSerializer.html
[SerializableTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[PrimitiveTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[JdkTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[ServiceLoaderTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/ServiceLoaderTypeResolver.html
[RaftServer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/RaftServer.html
[RaftClient]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/RaftClient.html
[Session]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/session/Session.html
[Operation]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Operation.html
[Command]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Command.html
[Query]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Query.html
[Commit]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Commit.html
[ConsistencyLevel]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/ConsistencyLevel.html
[DistributedAtomicValue]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/atomic/DistributedAtomicValue.html
[DistributedSet]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections/DistributedSet.html
[DistributedMap]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections/DistributedMap.html
[DistributedLock]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedLock.html
[DistributedLeaderElection]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedLeaderElection.html
[DistributedTopic]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedTopic.html
[Builder]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/Builder.html
[Listener]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/Listener.html
[Context]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/concurrent/Context.html