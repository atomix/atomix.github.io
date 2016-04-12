---
layout: docs
project: copycat
menu: docs
title: Getting Started
first-section: getting-started
---

{:.no-margin-top}
## Installation

Copycat consists of two core modules. To use the Raft server library, add the `copycat-server` jar
to your classpath:

```
<dependency>
  <groupId>io.atomix.copycat</groupId>
  <artifactId>copycat-server</artifactId>
  <version>{{ site.copycat-version }}</version>
</dependency>
```

To use the Raft client library, add the `copycat-client` jar to your classpath:

```
<dependency>
  <groupId>io.atomix.copycat</groupId>
  <artifactId>copycat-client</artifactId>
  <version>{{ site.copycat-version }}</version>
</dependency>
```

In addition to client and server libraries, typically you must include a [`Transport`][Transport] via which clients and servers can communicate with each other:

```
<dependency>
  <groupId>io.atomix.catalyst</groupId>
  </artifactId>catalyst-netty</artifactId>
  <version>{{ site.catalyst-version }}</version>
</dependency>
```

### Creating a State Machine

Copycat's primary role is as a framework for building highly consistent, fault-tolerant replicated state machines. Copycat servers receive state machine operations from clients, log and replicate the operations as necessary, and apply them to a state machine on each server. State machine operations are guaranteed to be applied in the same order on all servers, and Copycat handles the persistence and replication of the state machine state internally.

To create a state machine, extend the base [`StateMachine`][StateMachine] class:

```java
public class MapStateMachine extends StateMachine {
}
```

Copycat servers will create an instance of the state machine class and manage method calls to the state machine.

### Defining State Machine Operations

Copycat replicated state machines are modified and queried by defining operations through which a client and state machine can communicate. Operations are replicated by the Copycat cluster and are translated into arguments to methods on the replicated state machine. Users must define the interface between the client and the cluster by implementing [`Operation`][Operation] classes that clients will submit to the replicated state machine.

Commands are state machine operations that alter the system's state. For example, in a map state machine some commands might include `put` and `remove`. To implement a state machine command, simply implement the [`Command`][Command] interface. The generic argument to the [`Command`][Command] interface indicates the return type of the command:

```java
public class PutCommand implements Command<Object> {
  private final Object key;
  private final Object value;

  public PutCommand(Object key, Object value) {
    this.key = key;
    this.value = value;
  }

  public Object key() {
    return key;
  }

  public Object value() {
    return value;
  }
}
```

Queries are state machine operations that *read* the system's state but *do not modify it*. For example, in a map state machine some queries might include `get`, `size`, and `isEmpty`. To implement a state machine query, implement the [`Query`][Query] interface. The generic argument to the [`Query`][Query] interface indicates the return type of the query:

```java
public class GetQuery implements Query<Object> {
  private final Object key;

  public GetQuery(Object key) {
    this.key = key;
  }

  public Object key() {
    return key;
  }
}
```

It's critical that command and query operations be correctly implemented based on how they operate on the state machine's state. Implementing commands that simply read the system's state will result in a significant loss of performance by unnecessarily writing reads to disk and replicating them to a majority of the cluster. Implementing a query that modifies the state machine state can result in lost writes and inconsistent state across servers.

### Implementing State Machine Operations

State machine operations are implemented as `public` methods on the state machine class which accept a single [`Commit`][Commit] parameter where the generic argument for the commit is the operation accepted by the method. Copycat automatically detects the command or query that applies to a given state machine methods based on the generic argument to the [`Commit`][Commit] parameter.

```java
public class MapStateMachine extends StateMachine {
  private Map<Object, Object> map = new HashMap<>();

  public Object put(Commit<PutCommand> commit) {
    try {
      map.put(commit.operation().key(), commit.operation().value());
    } finally {
      commit.close();
    }
  }

  public Object get(Commit<GetQuery> commit) {
    try {
      return map.get(commit.operation().key());
    } finally {
      commit.close();
    }
  }
}
```

In each operation method, once the commit has been applied to the state machine, the [`Commit`][Commit] must be `close`d. This releases the [`Commit`][Commit] object back to a pool. In certain types of state machines, commits can be held open across method calls. This is explained in more detail in the [state machine][state-machines] documentation.

### Implementing Snapshot Support

State machine operations are replicated and written to a log on disk on each server in the cluster. As commands are submitted to the cluster over time, the disk capacity will eventually be consumed. Copycat must periodically remove unneeded commands from the replicated log to conserve disk space. This is known as log compaction.

State machines are responsible for ensuring that state is persisted so that Copycat can compact its logs. The simplest and most common approach to supporting log compaction is through snapshots. To support snapshots in a Copycat state machine, implement the [`Snapshottable`][Snapshottable] interface.

Let's extend the `MapStateMachine` to support snapshotting:

```java
public class MapStateMachine extends StateMachine implements Snapshottable {
  private Map<Object, Object> map = new HashMap<>();

  @Override
  public void snapshot(SnapshotWriter writer) {
    writer.writeObject(map);
  }

  @Override
  public void install(SnapshotReader reader) {
    map = reader.readObject();
  }
}
```

For snapshottable state machines, Copycat will periodically request a binary snapshot of the state machine's state and write the snapshot to disk. If the server is restarted, the state machine's state will be recovered from the on-disk snapshot. When a new server joins the cluster, the snapshot of the state machine will be replicated to the joining server to catch up its state. This allows Copycat to remove commits that contributed to the snapshot from the replicated log, thus conserving disk space.

### Creating a server

Once a state machine and its operations have been defined, we can create a [`CopycatServer`][CopycatServer] to manage the state machine. Copycat uses the builder pattern for configuring and constructing servers. Each Copycat server must be initialized with a local server [`Address`][Address].

```java
Address address = new Address("123.456.789.0", 5000);
CopycatServer.Builder builder = CopycatServer.builder(address);
```

Each server must be configured with the same state machine, in this case our `MapStateMachine`:

```java
builder.withStateMachine(MapStateMachine::new);
```

Finally, the server must be provided a [`Transport`][Transport] through which it will communicate with other servers in the cluster and a [`Storage`][Storage] object through which it will store the cluster configuration and state changes.

```java
builder.withTransport(NettyTransport.builder()
  .withThreads(4)
  .build());

builder.withStorage(Storage.builder()
  .withDirectory(new File("logs"))
  .withStorageLevel(StorageLevel.DISK)
  .build());

CopycatServer server = builder.build();
```

{:.callout .callout-danger}
The server's [`Storage`][Storage] directory *must* be unique to the server.

The server builder methods can then be chained for a more concise representation of the server configuration:

```java
CopycatServer server = CopycatServer.builder(address)
  .withStateMachine(MapStateMachine::new)
  .withTransport(NettyTransport.builder()
    .withThreads(4)
    .build())
  .withStorage(Storage.builder()
    .withDirectory(new File("logs"))
    .withStorageLevel(StorageLevel.DISK)
    .build())
  .build();
```

One final task is necessary to complete the configuration of the server. We've created two state machine operations - `PutCommand` and `GetQuery` - which are `Serializable`. By default, Copycat's serialization framework will serialize these operations using Java's serialization. However, users can explicitly register serializable classes and implement custom binary serializers for more efficient serialization.

```java
server.serializer().register(PutCommand.class);
server.serializer().register(GetQuery.class);
```

## Bootstrapping the cluster

Once the server has been built, we can bootstrap a new cluster by calling the [`bootstrap()`][CopycatServer.bootstrap] method:

```java
CompletableFuture<CopycatServer> future = server.bootstrap();
future.join();
```

When a server is bootstrapped, it forms a *new* cluster single node cluster to which additional servers can be joined.

## Joining an existing cluster

Once an initial cluster has been bootstrapped, additional servers can be added to the cluster via the [`join()`][CopycatServer.join] method. When joining an existing cluster, the existing cluster configuration must be provided to the [`join`][CopycatServer.join] method:

```java
Collection<Address> cluster = Collections.singleton(new Address("127.0.0.1", 8700))
server.join(cluster).join();
```

### Submitting operations

Clients are built in a manner very similar to servers. To construct a client, create a [`CopycatClient.Builder`][CopycatClient.Builder]:

```java
CopycatClient.Builder builder = CopycatClient.builder();
```

To configure the client to connect to the cluster, we must set the same [`Transport`][Transport] as was used in the cluster of servers:

```java
builder.withTransport(NettyTransport.builder()
  .withThreads(2)
  .build());

CopycatClient client = builder.build();
```

Once again, we can chain builder method calls for a more concise client configuration:

```java
CopycatClient client = CopycatClient.builder(members)
  .withTransport(NettyTransport.builder()
    .withThreads(2)
    .build())
  .build();
```

Because the client will be submitting `PutCommand` and `GetQuery` to the cluster, we need to register those operations with the client's serializer as well to ensure they can be serialized in the same way the server expects them:

```java
client.serializer().register(PutCommand.class);
client.serializer().register(GetQuery.class);
```

Finally, we can build the client and [`connect`][CopycatClient.connect] to the cluster. When connecting to a cluster, a collection of server addresses must be passed to the [`connect`][CopycatClient.connect] method. The address list does not have to be representative of the entire cluster, but the client must be able to reach at least one server to establish a new session.

```java
CopycatClient client = builder.build();


Collection<Address> cluster = Arrays.asList(
  new Address("123.456.789.0", 8700),
  new Address("123.456.789.1", 8700),
  new Address("123.456.789.2", 8700)
);

CompletableFuture<CopycatClient> future = client.connect(cluster);
future.join();
```

Clients' communication with the cluster is completely transparent to the user. If a client's connection to a server fails, the client will automatically attempt to reconnect to remaining servers and keep its session alive. Users can control client fault-tolerance behavior through various strategies configurable in the client builder.

Once a client has been started, we can submit state machine commands and queries to the cluster using the [`submit`][CopycatClient.submit] methods:

```java
CompletableFuture<Object> future = client.submit(new PutCommand("foo", "Hello world!"));
Object result = future.join();
```

For synchronous operation of the Copycat API, the `Future` API provides the blocking method `get`. However, all Copycat APIs are asynchronous and rely upon Java 8's [`CompletableFuture`][CompletableFuture] as a promises API. So, instead of blocking on a single operation, a client can submit multiple operations and either await the result or react to the result once it has been received:

```java
// Submit three PutCommands to the replicated state machine
CompletableFuture[] futures = new CompletableFuture[3];
futures[0] = client.submit(new PutCommand("foo", "Hello world!"));
futures[1] = client.submit(new PutCommand("bar", "Hello world!"));
futures[2] = client.submit(new PutCommand("baz", "Hello world!"));

// Print a message once all three commands have completed
CompletableFuture.allOf(futures).thenRun(() -> System.out.println("Commands completed!"));
```

Queries are submitted to the cluster in exactly the same way as commands, using the [`submit`][CopycatClient.submit] method:

```java
client.submit(new GetQuery("foo")).thenAccept(result -> {
  System.out.println("foo is: " + result);
});
```

When a [`CompletableFuture`][CompletableFuture] callback like the one above is called, it will be called on an internal Copycat thread once the result of the operation is received by the client. Operations submitted to the cluster from a single client are guaranteed to be committed in the order in which they were submitted, and [`CompletableFuture`][CompletableFuture] callbacks are guaranteed to be called in the order in which the operations were submitted and on the same Copycat thread.

{% include common-links.html %}
