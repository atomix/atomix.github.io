---
layout: docs
project: copycat
menu: docs
title: Working with Clients
first-section: client
---

{:.no-margin-top}
The [`CopycatClient`][CopycatClient] provides an interface for submitting [commands](#commands) and [queries](#queries) to a cluster of [Copycat servers][copycat-server].

## Client Lifecycle

Clients communicate with the cluster through sessions. Sessions represent a connection between a single client and all servers in a Raft cluster. When a client connects to the cluster, it registers a new session through which it can submit [`Command`][Command] and [`Query`][Query] operations and receive session events. Clients' consistency guarantees are preserved as long as a client's session remains open. In the event a client's session is expired by the cluster, all consistency guarantees for commands, queries, and events are lost.

### Client States

Client states are indicative of a client's ability to communicate with a cluster. Throughout the lifetime of a client, the client will transition through various states based on its ability to maintain its session and submit operations to the cluster. Client states are represented by the [`CopycatClient.State`][CopycatClient.State] enum:

* [`CONNECTED`][CopycatClient.State] - The client has an open connection to the cluster and its previous operation or keep-alive attempt was succesful
* [`SUSPENDED`][CopycatClient.State] - The client cannot communicate with any server in the cluster and its session may have been expired
* [`CLOSED`][CopycatClient.State] - The client has not yet registered a new session or its session was expired

The state of a client is exposed through the [`CopycatClient#state()`][CopycatClient.state] getter, and client code can [listen for changes in the client's state](#listening-for-client-state-changes) to detect losses of consistency guarantees.

## Configuring the Client

To create a client, you must supply the client [`Builder`][builders] with a set of [`Address`][Address]es to which to connect.

The provided [`Address`][Address]es do not have to be representative of the full Copycat cluster, but they do have to provide at least one correct server to which the client can connect. In other words, the client must be able to communicate with at least one [`CopycatServer`][CopycatServer] that is the leader or can communicate with the leader, and a majority of the cluster must be able to communicate with one another in order for the client to register a new [`Session`][Session].

```java
CopycatClient client = CopycatClient.builder()
  .withTransport(new NettyTransport())
  .build();
```

Once a [`CopycatClient`][CopycatClient] has been created, connect to the cluster by calling [`connect(Address...)`][CopycatClient.connect] on the client, passing a list of server [`Address`][Address]es to which to connect:

{% include sync-tabs.html target1="#async-open" desc1="Async" target2="#sync-open" desc2="Sync" %}
{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active" id="async-open">
```java
List<Address> cluster = Arrays.asList(
  new Address("123.456.789.0", 8700),
  new Address("123.456.789.1", 8700),
  new Address("123.456.789.2", 8700)
);

client.connect(cluster).thenRun(() -> System.out.println("Successfully connected to the cluster!"));
```
</div>

<div class="tab-pane" id="sync-open">
```java
List<Address> cluster = Arrays.asList(
  new Address("123.456.789.0", 8700),
  new Address("123.456.789.1", 8700),
  new Address("123.456.789.2", 8700)
);

client.connect(cluster).join();
```
</div>
</div>

{:.callout .callout-info}
Clients only have to specify at least one live server's [`Address`][Address] through which the client can register its session with the cluster. Once a client's session has been registered, the client will discover unknown servers and be notified any time a new server joins the cluster.

When the client connects to the cluster, it will attempt to connect to each server in the provided [`Address`][Address] list to register a new session. By default, if the client cannot register a new session through any of the provided servers, the [`CompletableFuture`][CompletableFuture] returned by [`connect(Address...)`][CopycatClient.connect] will be completed exceptionally.

### Connection Strategies

By default, when a client's attempt to register a new session with the cluster fails, the [`connect(Address...)`][CopycatClient.connect] operation will be completed exceptionally. However, clients may be configured with a [`ConnectionStrategy`][ConnectionStrategy] to define how they should handle failed connection attempts.

To configure a client's [`ConnectionStrategy`][ConnectionStrategy], set the strategy in the client's [`Builder`][CopycatClient.Builder]:

```java
CopycatClient client = CopycatClient.builder()
  .withTransport(new NettyTransport())
  .withConnectionStrategy(ConnectionStrategies.EXPONENTIAL_BACKOFF)
  .build();
```

Copycat provides several [`ConnectionStrategy`][ConnectionStrategy] implementations in the [`ConnectionStrategies`][ConnectionStrategies] enum:

* [`ONCE`][ConnectionStrategies] - Attempts to register a session via each known server once
* [`EXPONENTIAL_BACKOFF`][ConnectionStrategies] - Attempts to register a session through all known servers using exponential backoff in the event that registration is rejected by all servers
* [`FIBONACCI_BACKOFF`][ConnectionStrategies] - Attempts to register a session through all known servers using fibonacci backoff in the event that registration is rejected by all servers

### Recovery Strategies

Sessions provide consistency guarantees for clients that would otherwise not be possible. Once a client connects to the cluster and registers a new session, Copycat guarantees that write operations submitted by that client will be linearizable as long as its session is open, and read operations will adhere to their configured [consistency levels](#consistency-guarantees-for-client-operations). But when a client fails or otherwise disconnects from the cluster, servers will expire the client's session. By default, when a client's session is expired, all pending operations submitted by the client will be completed exceptionally, and the client will be closed. However, this behavior may be configured by setting a [`RecoveryStrategy`][RecoveryStrategy] on the client to allow it to transparently reconnect to the cluster and open a new session in the event an existing session is expired by the cluster.

To configure a client's [`RecoveryStrategy`][RecoveryStrategy], set the strategy in the client's [`Builder`][CopycatClient.Builder]:

```java
CopycatClient client = CopycatClient.builder()
  .withTransport(new NettyTransport())
  .withRecoveryStrategy(RecoveryStrategies.RECOVER)
  .build();
```

Copycat provides two simple recovery strategies through the [`RecoveryStrategies`][RecoveryStrategies] enum:

* [`CLOSE`][RecoveryStrategies] - Closes the client in the event its session is expired by the cluster
* [`RECOVER`][RecoveryStrategies] - Recovers the client by registering a *new* session in the event its existing session is expired by the cluster

When a client's attempt to submit an operation to the cluster fails as a result of an expired session, the client will consult the configured [`RecoveryStrategy`][RecoveryStrategy] to determine how to handle the failure. The default strategy used is [`RecoveryStrategies.CLOSE`][RecoveryStrategies].

{:.callout .callout-warning}
The involuntary expiration of a client's session implies a loss of linearizable semantics. Client code should monitor clients for [state changes](#listening-for-client-state-changes) to detect any loss of consistency guarantees.

Client code may provide a custom [`RecoveryStrategy`][RecoveryStrategy] by implementing that interface. Additionally, clients can also *manually* recover a session by calling the [`CopycatClient#recover()`][CopycatClient.recover] method directly. Recovering a client directly will result in a new session being registered regardless of the current state of the client.

### Server Selection Strategies

The Raft consensus algorithm dictates that clients are typically implemented by talking directly to the cluster's leader. However, because Copycat allows clients to read from followers and passive servers, clients may benefit from the scalability afforded when connecting to non-leader nodes. To facilitate the ability to connect to different types of servers, clients can be configured with a [`ServerSelectionStrategy`][ServerSelectionStrategy] which prioritizes the servers with which a client communicates. Each time the structure of a cluster or its leader changes, clients retrieve an updated prioritized of server [`Address`][Address]es to which to connect. This allows clients to favor communication with leaders or followers based on their read and write patterns.

To configure a client's [`ServerSelectionStrategy`][ServerSelectionStrategy], set the strategy in the client's [`Builder`][CopycatClient.Builder]:

```java
CopycatClient client = CopycatClient.builder()
  .withTransport(new NettyTransport())
  .withServerSelectionStrategy(ServerSelectionStrategies.FOLLOWERS)
  .build();
```

By default, clients will simply connect to any server in the cluster, and no particular server is prioritized over any other. But Copycat provides several alternative strategies for connecting to servers in the [`ServerSelectionStrategies`][ServerSelectionStrategies] enum:

* [`ANY`][ServerSelectionStrategies] - Connects to any server in the cluster and prioritizes servers in no particular order
* [`LEADER`][ServerSelectionStrategies] - Prioritizes connecting to the current cluster leader. In the event a leader change occurs, the client will disconnect from the old leader and reconnect to the new one.
* [`FOLLOWERS`][ServerSelectionStrategies] - Prioritizes connecting to non-leader nodes. For single-node clusters, the client will be allowed to connect to the leader.

Server selection strategies should be selected based on the patterns with which a client reads and writes to the cluster. In general, the rules for choosing between the `LEADER` and `FOLLOWERS` strategies are as follows:

* Clients for which a majority of operations are commands or for which queries are always [`LINEARIZABLE`][Query.ConsistencyLevel] should connect directly to the leader via [`ServerSelectionStrategies.LEADER`][ServerSelectionStrategies]
* Clients for which the majority of *all* operations are [`SEQUENTIAL`][Query.ConsistencyLevel] queries should connect to followers via [`ServerSelectionStrategies.FOLLOWERS`][ServerSelectionStrategies]

## Submitting State Machine Operations

Commands and queries can be submitted to the server-side replicated [`StateMachine`][StateMachine] using the [`submit(Operation)`][CopycatClient.submit] method:

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
Object result = client.submit(new PutCommand("foo", "Hello world!")).join();
```
</div>
</div>

The [`CompletableFuture`][CompletableFuture] returned by the [`CopycatClient.submit(Operation)`][CopycatClient.submit] method will be completed in the client's event thread once an operation result is received from the cluster. If the event thread is blocked, the future will be completed in the client's I/O thread. This allows clients to block within [`CompletableFuture`][CompletableFuture] callbacks, meaning the following is perfectly valid code:

```java
client.submit(new PutCommand("foo", "Hello world!")).thenRun(() -> {
  Object value = client.submit(new GetQuery("foo")).join();
});
```

In the event that the client's session is expired while submitting an operation, the operation's associated [`CompletableFuture`][CompletableFuture] will be completed exceptionally with a `ClosedSessionException`. This exception implies a loss of linearizability guarantees, so it's the responsibility of the client code to resubmit operations failed with this exception.

## Listening for Session Events

The client will remain connected to the server through which the session was registered for as long as possible. If the server fails, the client can reconnect to another random server and maintain its open session.

The client's session can be used to receive events `publish`ed by the server's [`StateMachine`][StateMachine]. To register a session event listener, use the [`onEvent(String, Consumer)`][CopycatClient.onEvent] method:

```java
client.<ChangeEvent>onEvent("change", event -> System.out.println(event.oldValue() + " changed to " + event.newValue()));
```

When events are sent from a server state machine to a client via the client's session, only the server to which the client is connected will send the event. Copycat servers guarantee that state machine events will be received by the client session in the order in which they're sent even if the client switches servers.

When an event listener callback is registered, a [`Listener`][Listener] object will be returned. The [`Listener`][Listener] can be used to unregister the event callback by calling the `close()` method:

```java
Listener<ChangeEvent> eventListener = client.onEvent("change", event -> {
  ...
});

// Unregister the event listener
eventListener.close();
```

## Listening for Client State Changes

When using the [`RecoveryStrategy.RECOVER`][RecoveryStrategies] recovery strategy, the loss of linearizability guarantees can become supressed. To detect a loss of guarantees in a client configured to recover its session in the event of an expiration by the cluster, client code can listen to the client's state for changes. Client states are defined by the [`CopycatClient.State`][CopycatClient.State] enum. Each client may be in one of three states at any given time:

* [`CONNECTED`][CopycatClient.State] - The client has an open connection to the cluster and its previous operation or keep-alive attempt was succesful
* [`SUSPENDED`][CopycatClient.State] - The client cannot communicate with any server in the cluster and its session may have been expired
* [`CLOSED`][CopycatClient.State] - The client has not yet registered a new session or its session was expired

Clients should assume a loss of consistency guarantees any time the client is in the [`SUSPENDED`][CopycatClient.State] state. Clients will transition to this state any time communication with the cluster fails or their session is expired by the cluster. Client code can listen for changes in the client's state by registering a state change listener callback via [`CopycatClient#onStateChange(Consumer)`][CopycatClient.onStateChange]:

```java
client.onStateChange(state -> {
  if (state == CopycatClient.State.SUSPENDED) {
    // Linearizability guarantees lost
  }
});
```

When a client state change listener callback is registered, a [`Listener`][Listener] object will be returned. The [`Listener`][Listener] can be used to unregister the state change callback by calling the `close()` method:

```java
Listener<CopycatClient.State> stateChangeListener = client.onStateChange(state -> {
  ...
});

// Unregister the state change listener
stateChangeListener.close();
```

{% include common-links.html %}
