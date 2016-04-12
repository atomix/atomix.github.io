---
layout: docs
project: atomix
menu: docs
title: Distributed Groups
pitch: Primitives for distributed group operations
---

The [`DistributedGroup`][DistributedGroup] resource facilitates managing group membership within an Atomix cluster. Membership is managed by members joining and leaving the group, and instances of the group throughout the cluster are notified on changes to the structure of the group. Groups can elect a leader, and members can communicate directly with one another or through persistent queues.

Groups membership is managed in a replicated state machine. When a member joins the group, the join request is replicated, the member is added to the group, and the state machine notifies instances of the [`DistributedGroup`][DistributedGroup] of the membership change. In the event that a group instance becomes disconnected from the cluster and its session times out, the replicated state machine will automatically remove the member from the group and notify the remaining instances of the group of the membership change.

To create a membership group resource, use the [`Atomix#getGroup(String)`][Atomix.getGroup] method:

```java
atomix.getGroup("my-group").thenAccept(group -> {
  ...
});
```

An optional group configuration can be passed as a second argument when creating a group. The configuration is cluster-wide and will only apply to the group the first time the resource is created by any node:

```java
DistributedGroup.Config config = new DistributedGroup.Config()
  .withMemberExpiration(Duration.ofMinutes(10));
DistributedGroup group = atomix.getGroup("my-group").join();
```

### Joining the group

When a new instance of the resource is created, it is initialized with an empty [`members()`][DistributedGroup.members] list
as it is not yet a member of the group. Once the instance has been created, the user must join the group
via the [`join()`][DistributedGroup.join] method:

```java
group.join().thenAccept(member -> {
  System.out.println("Joined with member ID: " + member.id());
});
```

Once the group has been joined, a [`LocalMember`][LocalMember] instance will be returned. The local member can be used to register listeners for messages sent to the member via the member's [`MessageService`][MessageService].

### Leaving the group

Once a member has joined a group, the [`LocalMember`][LocalMember] can be used to remove the member from the group by calling the [`leave()`][LocalMember.leave] method:

```java
LocalMember localMember = group.join().join();
localMember.leave();
```

Even without explicitly leaving the group, it's important to note that when the node crashes or otherwise becomes partitioned from the cluster, members will be automatically removed from the group when their session expires.

### Listening for members joining the group

Clients can listen for members joining the group by registering event listeners through the [`onJoin(Consumer)`][DistributedGroup.onJoin] method.

```java
group.onJoin(member -> {
  System.out.println(member.id() + " joined the group!");
});
```

When a member joins the group, all open instances of the [`DistributedGroup`][DistributedGroup] will be notified. Event notifications occur in the Atomix event thread, and events are guaranteed to be received in the same order on all nodes.

### Listening for members leaving the group

As with listening for members joining the group, clients can also listen for members leaving the group by registering a listener through the [`onLeave(Consumer)`][DistributedGroup.onLeave] method:

```java
group.onLeave(member -> {
  System.out.println(member.id() + " left the group!");
});
```

Leave events may occur when a member explicitly leaves the group or when the node to which a member belongs crashes or is otherwise disconnected from the cluster. When a client's session expires, the group state machine automatically removes members associated with that session from the group.

### Listing the members in the group

Users of the distributed group do not have to join the group to interact with it. For instance, while a server may participate in the group by joining it, a client may interact with the group just to get a list of available members. To access the list of group members, use the [`members()`][DistributedGroup.members] getter:

```java
DistributedGroup group = atomix.getGroup("foo").join();
for (GroupMember member : group.members()) {
  ...
}
```

Once the group instance has been created, the group membership will be automatically updated each time the structure of the group changes. However, in the event that the client becomes disconnected from the cluster, it may not receive notifications of changes in the group structure.

### Persistent members

[`DistributedGroup`][DistributedGroup] supports a concept of persistent members that requires members to *explicitly* leave the group to be removed from it. Persistent member messages will remain in a failed member's queue until the member recovers.

In order to support recovery, persistent members must be configured with a user-provided member ID. The member ID is provided when the member joins the group, and providing a member ID is all that's required to create a persistent member via the [`join(String)`][DistributedGroup.join] method.

```java
DistributedGroup group = atomix.getGroup("persistent-members").join();
LocalGroupMember memberA = group.join("a").join();
LocalGroupMember memberB = group.join("b").join();
```

Persistent members are not limited to a single node. If a node crashes, any persistent members that existed on that node may rejoin the group on any other node. Persistent members rejoin simply by calling [`join(String)`][DistributedGroup.join] with the unique member ID. Once a persistent member has rejoined the group, its session will be updated and any tasks remaining in the member's [`MessageService`][MessageService] will be published to the member.

Persistent member state is retained *only* inside the group's replicated state machine and not on clients. From the perspective of [`DistributedGroup`][DistributedGroup] instances in a cluster, in the event that the node on which a persistent member is running fails, the member will leave the group. Once the persistent member rejoins the group, join listeners will be called again on each group instance in the cluster.

## Leader election

The [`DistributedGroup`][DistributedGroup] resource facilitates leader election which can be used to coordinate a group by ensuring only a single member of the group performs some set of operations at any given time. Leader election is a core concept of membership groups, and because leader election is a low-overhead process, leaders are elected for each group automatically.

Leaders are elected using a fair policy. The first member to join a group will always become the initial group leader. Thereafter, for each election the cluster will elect a random member of the group. Each unique leader in a group is associated with a [`term()`][Term.term]. The term represents a globally unique, monotonically increasing token that can be used for fencing. Users can listen for changes in group terms and leaders with event listeners:

```java
DistributedGroup group = atomix.getGroup("election-group").get();
group.election().onElection(term -> {
  ...
});
```

The `term()` is guaranteed to be unique for each [`leader()`][Term.leader] and is guaranteed to be monotonically increasing. Each instance of a group is guaranteed to see the same leader for the same term, and no two leaders can ever exist in the same term. In that sense, the terminology and constraints of leader election in Atomix borrow heavily from the Raft consensus algorithm that underlies it.

## Messaging

Members of a group and group instances can communicate with one another through the messaging API, [`MessageService`][MessageService]. Direct messaging between group members is reliable and is done as writes to the Atomix cluster. Messages are held in memory within the Atomix cluster and are published to consumers using Copycat's session event framework. Messages are guaranteed to be delivered to consumers in the order in which they were sent by a producer. Because each message is dependent on at least one or more writes to the Atomix cluster, messaging is not intended to support high-throughput use cases. Group messaging is designed for coordinating group behaviors. For example, a leader can instruct a random member to perform a task through the messaging API.

### Direct messaging

To send messages directly to a specific member of the group, use the associated [`GroupMember`][GroupMember]'s [`MessageClient`][MessageClient].

```java
GroupMember member = group.member("foo");
MessageProducer<String> producer = member.messaging().producer("bar");
producer.send("baz").thenRun(() -> {
  // Message acknowledged
});
```

Users can specify the criteria by which a producer determines when a message is completed by configuring the producer's [`MessageProducer.Execution`][MessageProducer.Execution] policy. To configure the execution policy, pass [`MessageProducer.Options`][MessageProducer.Options] when creating a [`MessageProducer`][MessageProducer].

```java
MessageProducer.Options options = new MessageProducer.Options()
  .withExecution(MessageProducer.Execution.SYNC);
MessageProducer<String> producer = member.messaging().producer("bar", options);
```

Producers can be configured to send messages using three execution policies:

* `SYNC` sends messages to consumers and awaits acknowledgement from the consumer side of the queue. If a producer is producing to an entire group, synchronous producers will await acknowledgement from all members of the group.
* `ASYNC` awaits acknowledgement of persistence in the cluster but not acknowledgement that messages have been received and processed by consumers.
* `REQUEST_REPLY` awaits arbitrary responses from all consumers to which a message is sent. If a message is sent to a group of consumers, message reply futures will be completed with a list of reply values.

When the [`MessageProducer`][MessageProducer] is configured with the `ASYNC` execution policy, the [`CompletableFuture`][CompletableFuture] returned by the [`send(Object)`][MessageProducer.send] method will be completed as soon as the message is persisted in the cluster.

### Broadcast messaging

Groups also provide a group-wide [`MessageClient`][MessageClient] that allows users to broadcast messages to all members of a group or send a direct message to a random member of a group. To use the group-wide message client, use the `messaging()` getter.

```java
MessageProducer<String> producer = group.messaging().producer("foo");
producer.send("Hello world!").thenRun(() -> {
  // Message delivered to all group members
});
```

By default, messages sent through the group-wide message producer will be sent to *all* members of the group. But just as [`MessageProducer.Execution`][MessageProducer.Execution] policies can be used to define the criteria by which message operations are completed, the [`MessageProducer.Delivery`][MessageProducer.Delivery] policy can be used to define how messages are delivered when using a group-wide producer.

```java
MessageProducer.Options options = new MessageProducer.Options()
  .withDelivery(MessageProducer.Delivery.RANDOM);
MessageProducer<String> producer = member.messaging().producer("bar", options);
```

Group-wide producers can be configured with the following [`MessageProducer.Delivery`][MessageProducer.Delivery] policies:

* `RANDOM` producers send each message to a random member of the group. In the event that a message is not successfully `ack`ed by a member and that member fails or leaves the group, random messages will be redelivered to remaining members of the group.
* `BROADCAST` producers send messages to all available members of a group. This option applies only to producers constructed from [`DistributedGroup`][DistributedGroup] messaging clients.

Delivery policies work in tandem with [`MessageProducer.Execution`][MessageProducer.Execution] policies described above. For example, a group-wide producer configured with the `REQUEST_REPLY` execution policy and the `BROADCAST` delivery policy will send each message to all members of the group and aggregate replies into a `Collection` once all consumers have replied to the message.

### Message consumers

Messages delivered to a group member must be received by listeners registered on the [`LocalMember`][LocalMember]'s
[`MessageService`][MessageService]. Only the node to which a member belongs can listen for messages sent to that member. Thus, to listen for messages, join a group and create a [`MessageConsumer`][MessageConsumer]. To listen for messages on a consumer, register a consumer callback via the [`onMessage(Consumer)`][MessageConsumer.onMessage] method:

```java
LocalMember localMember = group.join().join();
MessageConsumer<String> consumer = localMember.messaging().consumer("foo");
consumer.onMessage(message -> {
  message.ack();
});
```

When a [`Message`][Message] is received, consumers must always call [`ack()`][Message.ack], [`fail()`][Message.fail], or [`reply(Object)`][Message.reply]. Failure to complete handling of a message will result in a memory leak in the cluster and failure to deliver any additional messages to the consumer. When a consumer acknowledges a message, the message will be removed from memory in the cluster and the producer that sent the message will be notified according to its configuration.

### Persistent messaging

Messages sent directly to specific members of a group are typically delivered only while that member is connected to the group. In the event that a member to which a message is sent fails, the message is failed. This can result in transparent failures when using the `ASYNC` execution policy. A message can be persisted but may never actually be delivered and acknowledged. To ensure that direct messages are eventually delivered, persistent members must be used.

```java
LocalMember member = group.join("member-1").join();
MessageConsumer<String> consumer = member.messaging().consumer("foo");
consumer.onMessage(message -> {
  ...
});
```

When a message is sent to a persistent member, the message will be persisted in the cluster until it can be delivered to that member regardless of whether the member is actively connected to the cluster. If the persistent member crashes, once the member rejoins the group pending messages will be delivered. Persistent members are also free to switch nodes to rejoin the group on live nodes, and pending messages will still be redelivered.

Users must take care, however, when using persistent members. `BROADCAST` messages sent to groups with persistent members that are not connected to the cluster will be persisted in memory in the cluster until they can be delivered. If the producer that broadcasts the message is configured to await acknowledgement or replies from members, producer [`send(Object)`][MessageProducer.send] operations cannot be completed until dead members rejoin the group.

## Serialization

Users are responsible for ensuring the serializability of tasks, messages, and properties set on the group and members of the group. Serialization is controlled by the group's [`Serializer`][Serializer] which can be access via `serializer()` or on the parent [`Atomix`][Atomix] instance. Because objects are typically replicated throughout the cluster, *it's critical that any object sent from any node should be serializable by all other nodes*.

Users should register serializable types before performing any operations on the group.

```java
DistributedGroup group = atomix.getGroup("group").get();
group.serializer().register(User.class, UserSerializer.class);
```

For the best performance from serialization, it is recommended that serializable types be registered with unique type IDs. This allows the Catalyst [`Serializer`][Serializer] to identify the type by its serialization ID rather than its class name. It's essential that the ID for a given type is the same all all nodes in the cluster.

```java
group.serializer().register(User.class, 1, UserSerializer.class);
```

Users can also serialize `Serializable` types by simply registering the class without any other serializer. Catalyst will attempt to use the optimal serializer based on the interfaces implemented by the class.

## Group architecture

Group state is managed in a Copycat replicated [`StateMachine`][StateMachine]. When a [`DistributedGroup`][DistributedGroup] is created, an instance of the group state machine is created on each replica in the cluster. The state machine instance manages state for the specific membership group. When a member [`join`][DistributedGroup.join]s the group, a join request is sent to the cluster and logged and replicated before being applied to the group state machine. Once the join request has been committed and applied to the state machine, the group state is updated and existing group members are notified by `publish`ing state change notifications to open instances of the group. Membership change event notifications are received by all open instances of the resource.

Leader election is performed by the group state machine. When the first member joins the group, that member will automatically be assigned as the group member. Each time an additional member joins the group, the new member will be placed in a leader queue. In the event that the current group leader's [`Session`][Session] expires or is closed, the group state machine will assign a new leader by pulling from the leader queue and will publish an `elect` event to all remaining group members. Additionally, for each new leader of the group, the state machine will publish a `term` change event, providing a globally unique, monotonically increasing token uniquely associated with the new leader.

To track group membership, the group state machine tracks the state of the [`Session`][Session] associated with each open instance of the group. In the event that the session expires or is closed, the group member associated with that session will automatically be removed from the group and remaining instances of the group will be notified.

The group state machine facilitates direct and broadcast messaging through writes to the Atomix cluster. Each message sent to a group or a member of a group is committed as a single write to the cluster. Once persisted in the cluster, messages are delivered to clients through the state machine's session events API. The group state machine delivers messages to sessions based on the configured per-message delivery policy, and client-side group instances are responsible for dispatching received messages to the appropriate consumers. When a consumer acknowledges or replies to a message, another write is commited to the Atomix cluster, and the group state machine completes the associated message.

The group state machine manages compaction of the replicated log by tracking which state changes contribute to the state of the group at any given time. For instance, when a member joins the group, the commit that added the member to the group contributes to the group's state as long as the member remains a part of the group. Once the member leaves the group or its session is expired, the commit that created and remove the member no longer contribute to the group's state and are therefore released from the state machine and will be removed from the log during compaction.

{% include common-links.html %}

[leader]: http://atomix.io/atomix/api/latest/io/atomix/group/election/Term.html#leader--
[join]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#join--
[leave]: http://atomix.io/atomix/api/latest/io/atomix/group/LocalGroupMember.html#leave--
[members]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#members--
[on-join]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#onJoin-java.util.function.Consumer-
[on-leave]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.html#onLeave-java.util.function.Consumer-
[term]: http://atomix.io/atomix/api/latest/io/atomix/group/GroupElection.html#term--
[dgroup-config]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.Config.html
[dgroup-options]: http://atomix.io/atomix/api/latest/io/atomix/group/DistributedGroup.Options.html
