---
layout: content
project: atomix
menu: user-manual
title: Distributed Coordination
pitch: Coordinating processes
first-section: distributed-coordination
---

## Distributed coordination

The `atomix-coordination` module provides a set of distributed coordination tools. These tools are designed tofacilitate decision making and communication in a distributed system.

If your project does not depend on `atomix-all`, you must add the `atomix-coordination` dependency in order to access the coordination classes:

```
<dependency>
  <groupId>io.atomix</groupId>
  <artifactId>atomix-coordination</artifactId>
  <version>{{ site.version }}</version>
</dependency>
```

### DistributedLock

The [DistributedLock][DistributedLock] resources provides an asynchronous API similar to that of `java.util.concurrent.locks.Lock`.

To create a `DistributedLock`, pass the class to `Atomix.create(String, Class)`:

```java
atomix.create("/test-lock", DistributedLock.class).thenAccept(lock -> {
  // Do something with the lock
});
```

Once the lock has been created, the methods closely mimic those of `java.util.concurrent.locks.Lock`. `DistributedLock` returns `CompletableFuture` for all methods:

```java
lock.lock().thenRun(() -> {
  // Do some stuff and then...
  lock.unlock();
});
```

To block and wait for the lock to be acquired instead, call `join()` or `get()` on the returned `CompletableFuture`s:

```java
lock.lock().join();

// Do some stuff

lock.unlock().join();
```

### DistributedLeaderElection

The [DistributedLeaderElection][DistributedLeaderElection] resource provides an asynchronous API for coordinating tasks among a set of clients.

[Leader election](https://en.wikipedia.org/wiki/Leader_election) is a pattern commonly used in distributed systems to coordinate some task or access to a resource among a set of processes. Atomix's `DistributedLeaderElection` handles the coordination of a leader and notifies processes when they become the leader.

To create a `DistributedLeaderElection`, pass the class to `Atomix.create(String, Class)`:

```java
atomix.create("/test-election", DistributedLeaderElection.class).thenAccept(election -> {
  // Do something with the election
});
```

Once the election has been created, register a listener callback to be called when the calling node is elected the leader:

```java
election.onElection(epoch -> {
  System.out.println("Elected leader!");
});
```

The registration of a listener via `onElection` is asynchronous. The resource will not become electable until the `CompletableFuture` returned has been completed:

```java
election.onElection(epoch -> {
  System.out.println("Elected leader!");
}).thenRun(() -> {
  System.out.println("Awaiting election!");
});
```

When a session creates a new `DistributedLeaderElection` at the `/test-election` path, the session will be queued to be elected. When a client/session disconnects from the Atomix cluster or times out, the next session awaiting the leadership role will take over the leadership and the registered `onElection` listener will be called.

The argument provided to the election listener is commonly known as an *epoch* (or in some cases a `term` as in [Raft][Raft]). The epoch is a monotonically increasing, unique `long` that is representative of a single election.

It is important to note that while from the Atomix cluster's perspective, only one client will hold the leadership at any given point in time, the same may not be true for clients. It's possible that a client can believe itself to be the leader even though its session has timed out and a new leader has been elected. Users can guard against this scenario by verifying leadership with the `isLeader(long)` method prior to critical operations in order to ensure consistency:

```java
election.onElection(epoch -> {
  // Verify that this node is still the leader
  election.isLeader(epoch).thenAccept(leader -> {
    if (leader) {
      System.out.println("Still the leader");
      // Do something important
    } else {
      System.out.println("Lost leadership!");
    }
  });
});
```

In the event that a `DistributedLeaderElection` wins an election and loses its leadership without the node crashes, it's likely that the client's session expired due to a failure to communicate with the cluster.

### DistributedMembershipGroup

The [DistributedMembershipGroup] resources provides an asynchronous API for coordinating group membership across the cluster. Group membership can be used to track, for example, nodes in a cluster.

When new members [join](#joining-the-group) a membership group, all existing members of the group may be [notified](#listening-for-membership-changes). Typically, in fault tolerant systems members join the group until they fail. When a member's session is disconnected from the cluster, remaining members of the group will again be notified that the member has left the cluster.

To create a `DistributedMembershipGroup`, pass the class to `Atomix.create(String, Class)`:

```java
DistributedMembershipGroup group = atomix.create("group", DistributedMembershipGroup::new).get();
```

#### Joining the group

Once a new group membership instance has been created, `join` the group:

```java
group.join().join();
```

When the member joins the group, a new [GroupMember] will be added and all existing group members will be notified. Atomix guarantees that existing members will be notified prior to the `join` operation's completion.

#### Leaving the group

Typically, members remain part of the group until their session becomes disconnected from the cluster, at which time they will be automatically removed from the group and remaining members will be [notified](#listening-for-membership-changes). Alternatively, members can explicitly `leave` the group:

```java
group.leave().join();
```

#### Listening for membership changes

To listen for group members joining the group, use the `onJoin` event listener:

```java
group.onJoin(member -> {
  System.out.println(member.id() + " joined the group");
});
```

When a new member joins the group, all existing members of the group are guaranteed to be notified of the new member prior to that member's join completing.

To listen for group members leaving the group, use the `onLeave` event listener:

```java
group.onLeave(member -> {
  System.out.println(member.id() + " left the group");
});
```

#### Scheduling remote callbacks

Members in a [DistributedMembershipGroup] are represented as [GroupMember] objects. The `GroupMember` class provides an interface for remote execution on specific members of the group.

```java
group.onJoin(member -> {
  member.execute(() -> System.out.println("Printed on member " + member.id());
});
```

The `GroupMember` API supports two types of remote executions, *instant* and *scheduled*. To execute a remote callback immediately, use the `execute` method:

```java
member.execute(() -> System.out.println("Printed on member " + member.id());
```

To schedule a remote execution, use the `schedule` method, passing a `Duration` after which to execute the callback:

```java
member.schedule(Duration.ofSeconds(10), () -> System.out.println("Printed after 10 seconds on member " + member.id()));
```

### DistributedMessageBus

The [DistributedMessageBus] resource provides a simple asynchronous framework for unreliable synchronous messaging between instances of the resource in a cluster. Message bus resource instances communicate with one another by each starting a [Server] and connecting to each other instance via a [Client]. Users can register message bus handlers which are identified by an *address*, and handler address registrations are shared across the cluster via an internal replicated state machine.

To use the message bus, create a `DistributedMessageBus` resource:

```java
DistributedMessageBus bus = copycat.create("bus", DistributedMessageBus::new).get();
```

Each instance of the message bus must be `open`ed by providing the bus with a local [Address] to which to bind the server:

```java
Address address = new Address("123.456.789.0", 5000);

bus.open(address).join();
```

When the message bus is opened, all other instances of the message bus resource will be notified before the `open` operation completes.

#### Message producers

To send a message to a registered message bus address, create a `MessageProducer` and `send` the message:

```java
MessageProducer<String> producer = bus.producer("foo").get();

producer.send("hello");
```

The `send` method returns a `CompletableFuture` which will be completed with the response value of the receiver once received.

#### Message consumers

To register a message consumer, create a `MessageConsumer` for a message bus *address*:

```java
bus.consumer("foo", message -> {
  return "world!";
});
```

The `consumer` method will return a `CompletableFuture` which will be completed once all instances of the message bus have been notified of the new consumer registration.

### DistributedTopic

The [DistributedTopic] resource provides persistent, publish subscribe messaging between instances of the resource. Topic resource instances can subscribe to receive messages for a topic, and when a message is `publish`ed to a topic, the message will be committed to the underlying [Raft] commit log and then asynchronously sent to all available subscribers.

To use the topic resource, create a `DistributedTopic` resource:

```java
DistributedTopic<String> topic = copycat.create("topic", DistributedTopic::new).get();
```

To register a topic message listener, use the `onMessage` method:

```java
topic.onMessage(message -> System.out.println("Got message: " + message));
```

To publish a message to the topic, use the `publish` method:

```java
topic.publish("Hello world!").thenRun(() -> System.out.println("Published message!"));
```

The returned [CompletableFuture] will be completed once the message has been replicated and stored in the Atomix cluster. By default, messages will be sent to subscribers asynchronously. To configure the resource to synchronously send messages to all subscribers before completing the `publish` operation, configure the resource's `Consistency` to `ATOMIC`:

```java
topic.with(Consistency.ATOMIC).publish("Hello world!").join();
```

{% include common-links.html %}