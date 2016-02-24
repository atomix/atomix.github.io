---
layout: docs
project: copycat
menu: docs
title: Getting Started
pitch: Copycat in five minutes
first-section: getting-started
---

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

In addition to client and server libraries, typically you must include a `transport` via which clients and servers can communicate with each other:

```
<dependency>
  <groupId>io.atomix.catalyst</groupId>
  </artifactId>catalyst-netty</artifactId>
  <version>{{ site.catalyst-version }}</version>
</dependency>
```

### Creating a state machine

Copycat's primary role is as a framework for building highly consistent, fault-tolerant replicated state machines. Copycat servers receive state machine operations from clients, log and replicate the operations as necessary, and apply them to a state machine on each server. State machine operations are guaranteed to be applied in the same order on all servers, and Copycat handles the persistence and replication of the state machine state internally.

To create a state machine, extend the base [StateMachine][StateMachine] class:

```java
public class MapStateMachine extends StateMachine {
}
```

Copycat servers will create an instance of the state machine class and manage method calls to the state machine.

### Defining state machine operations

Copycat replicated state machines are modified and queried by defining operations through which a client and state machine can communicate. Operations are replicated by the Copycat cluster and are translated into arguments to methods on the replicated state machine. Users must define the interface between the client and the cluster by implementing `Operation` classes that clients will submit to the replicated state machine.

Commands are state machine operations that alter the system's state. For example, in a map state machine some commands might include `put` and `remove`. To implement a state machine command, simply implement the `Command` interface. The generic argument to the `Command` interface indicates the return type of the command:

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

Queries are state machine operations that *read* the system's state but *do not modify it*. For example, in a map state machine some queries might include `get`, `size`, and `isEmpty`. To implement a state machine query, implement the `Query` interface. The generic argument to the `Query` interface indicates the return type of the query:

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

### Implementing state machine operations

State machine operations are implemented as `public` methods on the state machine class which accept a single `Commit` parameter where the generic argument for the commit is the operation accepted by the method. Copycat automatically detects the command or query that applies to a given state machine methods based on the generic argument to the `Commit` parameter.

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

In each operation method, once the commit has been applied to the state machine, the `Commit` must be `close`d. This releases the `Commit` object back to a pool. In certain types of state machines, commits can be held open across method calls. This is explained in more detail in the [state machine][state-machine] documentation.

### Implementing snapshot support

State machine operations are replicated and written to a log on disk on each server in the cluster. As commands are submitted to the cluster over time, the disk capacity will eventually be consumed. Copycat must periodically remove unneeded commands from the replicated log to conserve disk space. This is known as log compaction.

State machines are responsible for ensuring that state is persisted so that Copycat can compact its logs. The simplest and most common approach to supporting log compaction is through snapshots. To support snapshots in a Copycat state machine, implement the `Snapshottable` interface.

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

### Starting a Copycat server

Once a state machine and its operations have been defined, we can start a cluster of `CopycatServer`s to replicate and query the state machine. Copycat uses the builder pattern for configuring and constructing servers. Each Copycat server must be initialized with a local `Address` and a list of remote `Address`es of all the other members of the cluster. This is known as the *cluster configuration*.

```java
Address address = new Address("123.456.789.0", 5000);

Collection<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000)
);

CopycatServer.Builder builder = CopycatServer.builder(address, members);
```

Each server must be configured with the same state machine, in this case our `MapStateMachine`:

```java
builder.withStateMachine(MapStateMachine::new);
```

Finally, the server must be provided a `Transport` through which it will communicate with other servers in the cluster and a `Storage` object through which it will store the cluster configuration and state changes.

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

The server builder methods can then be chained for a more concise representation of the server configuration:

```java
CopycatServer server = CopycatServer.builder(address, members)
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

One final task is necessary to complete the configuration of the server. We've created two state machine operations - `PutCommand` and `GetQuery` - which are `Serializable`. However, Copycat's serialization framework (Catalyst) does not allow arbitrary classes to be serialized and deserialized due to known security risks. By default, the Catalyst serialization framework requires specific classes to be whitelisted. Whitelisting can be disabled altogether on the server serializer:

```java
server.serializer().disableWhitelist();
```

But better yet, we can whitelist the state machine operations by registering them with the server serializer.

```java
client.serializer().register(PutCommand.class);
client.serializer().register(GetQuery.class);
```

This approach is slightly more efficient, but even more efficient means of serialization are described in the [Catalyst documentation][io-serialization].

Once the server has been built, start the server by calling `open`:

```java
CompletableFuture<CopycatServer> future = server.open();
future.join();
```

Remember that a majority of the cluster must be available for a server to be started. If the cluster configuration specifies three servers then two must be started and join each other for a leader to be elected and for the cluster to begin accepting state machine operations.

### Submitting operations via the client

Clients are built in a manner very similar to servers. To construct a client, create a `CopycatClient.Builder` by providing a list of initial servers to which to connect.

```java
Collection<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000)
);

CopycatClient.Builder builder = CopycatClient.builder(members);
```

The initial server list does not have to include all the servers in the cluster. If only a subset of server addresses is provided, once the client is able to connect to one of the known servers it will receive an updated list of servers automatically.

To configure the client to connect to the cluster, we must set the same `Transport` as was used in the cluster of servers:

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

Finally, we can build the client and `open` it to connect to the cluster.

```java
CopycatClient client = builder.build();
CompletableFuture<CopycatClient> future = client.open();
future.join();
```

Clients' communication with the cluster is completely transparent to the user. If a client's connection to a server fails, the client will automatically attempt to reconnect to remaining servers and keep its session alive. Users can control client fault-tolerance behavior through various strategies configurable in the client builder.

Once a client has been started, we can submit state machine commands and queries to the cluster using the `submit` methods:

```java
CompletableFuture<Object> future = client.submit(new PutCommand("foo", "Hello world!"));
Object result = future.get();
```

For synchronous operation of the Copycat API, the `Future` API provides blocking methods like `get` and `join`. However, all Copycat APIs are asynchronous and rely upon Java 8's `CompletableFuture` as a promises API. So, instead of blocking on a single operation, a client can submit multiple operations and either await the result or react to the result once it has been received:

```java
// Submit three PutCommands to the replicated state machine
CompletableFuture[] futures = new CompletableFuture[3];
futures[0] = client.submit(new PutCommand("foo", "Hello world!"));
futures[1] future = client.submit(new PutCommand("bar", "Hello world!"));
futures[2] future = client.submit(new PutCommand("baz", "Hello world!"));

// Print a message once all three commands have completed
CompletableFuture.allOf(futures).thenRun(() -> System.out.println("Commands completed!"));
```

Queries are submitted to the cluster in exactly the same way as commands, using the `submit` method:

```java
client.submit(new GetQuery("foo")).thenAccept(result -> {
  System.out.println("foo is: " + result);
});
```

When a `CompletableFuture` callback like the one above is called, it will be called on an internal Copycat thread once the result of the operation is received by the client. Operations submitted to the cluster from a single client are guaranteed to be committed in the order in which they were submitted, and `CompletableFuture` callbacks are guaranteed to be called in the order in which the operations were submitted and on the same Copycat thread.

{% include common-links.html %}