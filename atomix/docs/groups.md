---
layout: docs
project: atomix
menu: docs
title: Distributed Groups
pitch: Primitives for distributed group operations
---

The [DistributedGroup] resource provides an API for managing process or node groups in an Atomix cluster. The API can be used for group membership, service discovery, leader election, and remote scheduling and execution.

To create a distributed group, use the `DistributedGroup` class or constructor:

```java
DistributedGroup group = atomix.getGroup("my-group").get();
```

Each instance of `DistributedGroup` resource represents a single [GroupMember].

## Joining the Group

After creating a `DistributedGroup`, you can join the group by calling [join()][join]:

```java
group.join().thenAccept(member -> {
  System.out.println("Joined with member ID: " + member.id());
});
```

After joining a group, all existing members of the group may be notified via the [onJoin(Consumer)][on-join] event handlers:

```java
group.onJoin(member -> {
  System.out.println(member.id() + " joined the group!");
});
```

When new members [join](#joining-the-group) a membership group, all existing members of the group may be [notified](#listening-for-membership-changes). Typically, in fault tolerant systems members remain in the group until they fail. When a member's session is disconnected from the cluster, remaining members of the group will again be notified that the member has left the cluster.

## Leaving the Group

[Leaving][leave] a group is similarly straightforward to joining:

```java
group.leave();
```

The [onLeave(Consumer)][on-leave] event handler can be used to learn when members leave the group:

```java
group.onLeave(member -> {
  System.out.println(member.id() + " left the group!");
});
```

If a group member loses its session connection or otherwise fails, it will automatically be removed from the group and members will be notified.

## Listing Group Members

The [members()][members] list provides an up-to-date view of the group which will be automatically updated as members [join] and [leave] the group:

```java
DistributedGroup group = atomix.getGroup("my-group").get();
for (GroupMember member : group.members()) {
  System.out.println("Member: " + member);
}
```

Users of the distributed group do not have to join the group to interact with it. For instance, while a server may participate in the group by joining it, a client may interact with the group just to get a list of available members.

Once the group instance has been created, the group membership will be automatically updated each time the structure of the group changes. However, in the event that the client becomes disconnected from the cluster, it may not receive notifications of changes in the group structure.

## Leader election

The [DistributedGroup] resource facilitates leader election which can be used to coordinate a group by ensuring only a single member of the group performs some set of operations at any given time. Leader election is a core concept of membership groups, and because leader election is a low-overhead process, leaders are elected for each group automatically.

Leaders are elected using a fair policy. The first member to [join] a group will always become the initial group [leader]. Each unique leader in a group is associated with a [term]. The term is a globally unique, monotonically increasing token that can be used for fencing. Users can listen for changes in group terms and leaders with event listeners:

```java
DistributedGroup group = atomix.getGroup("my-group").get();
group.election().onTerm(term -> {
  System.out.println("New term: " + term);
});

group.election().onElection(leader -> {
  System.out.println("Elected leader: " + leader);
});
```

The [term] is guaranteed to be incremented prior to the election of a new [leader], and only a single leader for any given term will ever be elected. Each instance of a group is guaranteed to see terms and leaders progress monotonically, and no two leaders can exist in the same term. In that sense, the terminology and constrains of leader election in Atomix borrow heavily from the Raft algorithm that underlies it.

While terms and leaders are guaranteed to progress in the same order from the perspective of all clients of the resource, Atomix cannot guarantee that two leaders cannot exist at any given time. The group state machine will make a best effort attempt to ensure that all clients are notified of a term or leader change prior to the change being completed, but arbitrary process pauses due to garbage collection and other effects can cause a client's session to expire and thus prevent the client from being updated in real time. Only clients that can maintain their session are guaranteed to have a consistent view of the membership, term, and leader in the group at any given time.

To guard against inconsistencies resulting from arbitrary process pauses, clients can use the monotonically increasing term for coordination and managing optimistic access to external resources.

## Task queues

### Task queue producers

Tasks are arbitrary serializable values that are submitted to a queue via a [`TaskProducer`][TaskProducer]. Producers are created via a factory method on a [`TaskClient`][TaskClient].

```java
TaskProducer<String> producer = group.tasks().producer("foo");
```

Each producer is associated with a queue name. The producer for a given queue can be uniquely configured by passing a `TaskProducer.Options` instance when creating the producer. Once a producer has been referenced, future calls to the `producer` method will return the same [`TaskProducer`][TaskProducer] instance.

Once a producer has been created, tasks are submitted to the named queue via the `submit` method:

```java
producer.submit("Hello world!").thenRun(() -> {
  System.out.println("Task complete!");
});
```

The returned [`CompletableFuture`][CompletableFuture] will be completed once the task has been processed. The criteria for determining when a task has been processed is dependent on the producer configuration.

### Task queue consumers

Tasks are consumed from a task queue via a [`TaskConsumer`][TaskConsumer]. Consumers are created in a manner similar to producers with a factory `consumer` method on a [`TaskService`][TaskService].

```java
TaskConsumer<String> consumer = group.tasks().consumer("foo");
```

Each consumer is associated with a unique queue name. As with producers, the consumer for a given queue can be configured by passing a `TaskConsumer.Options` instance when creating the consumer. Once a consumer has been referenced, future calls to the `consumer` method will return the same [`TaskConsumer`][TaskConsumer] instance.

Once a consumer has been created, a callback must be registered for receiving tasks on the queue via the `onTask` method:

```java
consumer.onTask(task -> {
  ...
});
```

When a task is received by the consumer, the task callback will be called with the [`Task`][Task] instance as the argument. [`Task`][Task] is a wrapper object that provides context for the task and facilitates acks. Task consumer callbacks may be asynchronous. Once a callback is finished processing a task, it must call `ack()` on the [`Task`][Task] object to acknowledge completion of the task.

```java
consumer.onTask(task -> {
  ...
  task.ack();
});
```

When a task is acknowledged, the acknowledgement will be sent back to the process that produced the task and the task future will be completed. However, Atomix cannot guarantee that once a task has been acknowledged by a consumer it will be completed on the producer. In order to acknowledge a task, the acknowledgement must be submitted back to the Atomix cluster. The `ack()` method returns a [`CompletableFuture`][CompletableFuture] that will be completed once the task acknowledgement is complete.

```java
consumer.onTask(task -> {
  ...
  task.ack().thenRun(() -> System.out.println("Task acknowledged"));
});
```

Alternatively, consumers can explicitly fail processing of a task by calling the `fail()` method:

```java
consumer.onTask(task -> {
  // Task failed
  task.fail();
});
```

Failing a task will result in the task future being completed exceptionally on the producer.

## Direct messaging

### Message producers

Messages are arbitrary serializable values that are submitted to a destination via a [`MessageProducer`][MessageProducer]. Producers are created via a factory method on a [`MessageClient`][MessageClient].

```java
MessageProducer<String> producer = member.messages().producer("foo");
```

Each producer is associated with a connection name. The producer for a given connection can be uniquely configured by passing a `MessageProducer.Options` instance when creating the producer. Once a producer has been referenced, future calls to the `producer` method will return the same [`MessageProducer`][MessageProducer] instance.

Once a producer has been created, tasks are submitted to the named queue via the `send` method:

```java
producer.send("Hello world!").thenAccept(reply -> {
  System.out.println("Reply is " + reply);
});
```

The returned [`CompletableFuture`][CompletableFuture] will be completed once the destination responds to the message.

### Message consumers

Messages are consumed from the messaging service via a [`TaskConsumer`][TaskConsumer]. Consumers are created in a manner similar to producers with a factory `consumer` method on a [`MessageService`][MessageService].

```java
TaskConsumer<String> consumer = group.messages().consumer("foo");
```

Each consumer is associated with a unique connection name. As with producers, the consumer for a given connection can be configured by passing a `MessageConsumer.Options` instance when creating the consumer. Once a consumer has been referenced, future calls to the `consumer` method will return the same [`MessageConsumer`][MessageConsumer] instance.

Once a consumer has been created, a callback must be registered for receiving messages on the connection via the `onMessage` method:

```java
consumer.onMessage(message -> {
  ...
});
```

When a message is received by the consumer, the message callback will be called with the [`Message`][Message] instance as the argument. [`Message`][Message] is a wrapper object that provides context for the message and facilitates acks. Task consumer callbacks may be asynchronous. Once a callback is finished processing a message, it must call `reply(Object)` or `ack()` on the [`Message`][Message] object to send a response or acknowledge reception of the message respectively.

```java
consumer.onMessage(message -> {
  ...
  message.reply("Back at you!");
});
```

When a reply to a message is sent, the reply will be sent directly back to the sender. As with request messages, replies must be serializable by the Catalyst serializer.

{% include common-links.html %}

[leader]: http://atomix.io/atomix/api/latest/io/atomix/group/election/Election.html#leader--
[join]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#join--
[leave]: http://atomix.io/atomix/api/latest/io/atomix/group/LocalGroupMember.html#leave--
[members]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#members--
[on-join]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#onJoin-java.util.function.Consumer-
[on-leave]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#onLeave-java.util.function.Consumer-
[term]: http://atomix.io/atomix/api/latest/io/atomix/group/GroupElection.html#term--
[dgroup-config]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.Config.html
[dgroup-options]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.Options.html
