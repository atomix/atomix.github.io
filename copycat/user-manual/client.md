---
layout: content
project: copycat
menu: user-manual
title: Raft Consensus Algorithm
pitch: Sophisticated Raft Consensus implementation
first-section: client
---

Copycat is a standalone, feature-complete implementation of the [Raft consensus algorithm][Raft].

## CopycatClient

The [CopycatClient][CopycatClient] provides an interface for submitting [commands](#commands) and [queries](#queries) to a cluster of [Raft servers](#copycatserver).

To create a client, you must supply the client [Builder][builders] with a set of `Address`es to which to connect.

```java
List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5555),
  new Address("123.456.789.1", 5555),
  new Address("123.456.789.2", 5555)
);
```

The provided `Address`es do not have to be representative of the full Copycat cluster, but they do have to provide at least one correct server to which the client can connect. In other words, the client must be able to communicate with at least one `CopycatServer` that is the leader or can communicate with the leader, and a majority of the cluster must be able to communicate with one another in order for the client to register a new [Session](#client-sessions).

```java
CopycatClient client = CopycatClient.builder(members)
  .withTransport(new NettyTransport())
  .build();
```

Once a `CopycatClient` has been created, connect to the cluster by calling `open()` on the client:

{% include sync-tabs.html target1="#async-open" desc1="Async" target2="#sync-open" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-open">
```java
client.open().thenRun(() -> System.out.println("Successfully connected to the cluster!"));
```
</div>

<div class="tab-pane" id="sync-open">
```java
client.open().join();
```
</div>
</div>

### Client lifecycle

When the client is opened, it will connect to a random server and attempt to register its session. If session registration fails, the client will continue to attempt registration via random servers until all servers have been tried. If the session cannot be registered, the `CompletableFuture` returned by `open()` will fail.

### Submitting state machine operations

Commands and queries can be submitted to the server-side replicated `StateMachine` using the `submit` method:

{% include sync-tabs.html target1="#async-submit" desc1="Async" target2="#sync-submit" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-submit">
```java
client.submit(new PutCommand("foo", "Hello world")).thenAccept(result -> {
  System.out.println("State machine output: " + result);
});
```
</div>

<div class="tab-pane" id="sync-submit">
```java
Object result = client.submit(new PutCommand("foo", "Hello world!")).get();
```
</div>
</div>

### Client sessions

Once the client's session has been registered, the `Session` object can be accessed via `CopycatClient.session()`.

The client will remain connected to the server through which the session was registered for as long as possible. If the server fails, the client can reconnect to another random server and maintain its open session.

The `Session` object can be used to receive events `publish`ed by the server's `StateMachine`. To register a session event listener, use the `onEvent` method:

```java
client.session().onEvent(message -> System.out.println("Received " + message));
```

When events are sent from a server state machine to a client via the `Session` object, only the server to which the client is connected will send the event. Copycat servers guarantee that state machine events will be received by the client session in the order in which they're sent even if the client switches servers.

{% include common-links.html %}