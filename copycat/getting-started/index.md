---
layout: content
project: copycat
menu: getting-started
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
  <version>1.0.0-beta2</version>
</dependency>
```

To use the Raft client library, add the `copycat-client` jar to your classpath:

```
<dependency>
  <groupId>io.atomix.copycat</groupId>
  <artifactId>copycat-client</artifactId>
  <version>1.0.0-beta2</version>
</dependency>
```

In addition to client and server libraries, typically you must include a `transport` via which clients and servers can communicate with each other:

```
<dependency>
  <groupId>io.atomix.catalyst</groupId>
  </artifactId>catalyst-netty</artifactId>
  <version>1.0.0-rc4</version>
</dependency>
```

## CopycatClient

The [CopycatClient] provides an interface for submitting commands and queries to a cluster of Raft servers.

To create a client, you must supply the client [Builder][builders] with a set of `Address`es to connect to.

```java
List<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5555),
  new Address("123.456.789.1", 5555),
  new Address("123.456.789.2", 5555)
);
```

The provided `Address`es do not have to be representative of the full Copycat cluster, but they do have to provide at least one correct server to which the client can connect. In other words, the client must be able to communicate with at least one `CopycatServer` that is the leader or that can communicate with the leader. A majority of the cluster must be able to communicate with each other in order for the client to register a new [Session].

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

### Creating a state machine

To create a state machine, extend the base `StateMachine` class:

```java
public class MapStateMachine extends StateMachine {
  @Override
  protected void configure(StateMachineExecutor executor) {
  
  }
}
```

### Defining state machine operations

Commands alter state machine state:

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

Queries must only read the state machine state:

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

Certain types of commands can be considered *tombstones* - commands which result in the absence of state - such as a map remove command:

```java
public class RemoveCommand implements Command<Object> {
  private final Object key;

  public RemoveCommand(Object key) {
    this.key = key;
  }

  @Override
  public PersistenceLevel persistence() {
    return PersistenceLevel.PERSISTENT;
  }

  public Object key() {
    return key;
  }
}
```

### Implementing state machine operations

State machine operations are registered via the `StateMachineExecutor` in the `configure` method:

```java
public class MapStateMachine extends StateMachine {
  private final Map<Object, Commit<PutCommand>> map = new HashMap<>();

  @Override
  protected void configure(StateMachineExecutor executor) {
    executor.register(PutCommand.class, this::put);
    executor.register(GetQuery.class, this::get);
    executor.register(RemoveCommand.class, this::remove);
  }

  private Object put(Commit<PutCommand> commit) {
    // Store the full commit object in the map to ensure we can properly clean it from the commit log once we're done.
    map.put(commit.operation().key(), commit);
  }

  private Object get(Commit<GetQuery> commit) {
    try {
      // Get the commit value and return the operation value if available.
      Commit<PutCommand> value = map.get(commit.operation().key());
      return value != null ? value.operation().value() : null;
    } finally {
      // Close the query commit once complete to release it back to the internal commit pool.
      // Failing to do so will result in warning messages.
      commit.close();
    }
  }

  private Object remove(Commit<RemoveCommand> commit) {
    try {
      // Remove the commit with the given key.
      Commit<PutCommand> value = map.remove(commit.operation().key());

      // If a commit with the given key existed, get the result and then clean the commit from the log.
      if (value != null) {
        Object result = value.operation().value();
        value.clean();
        return result;
      }
      return null;
    } finally {
      // Finally, clean the remove commit.
      commit.clean();
    }
  }
}
```

### Starting a Copycat server

```java
Address address = new Address("123.456.789.0", 5000);

Collection<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000)
);

CopycatServer server = CopycatServer.builder(address, members)
  .withTransport(new NettyTransport())
  .withStateMachine(new MapStateMachine())
  .withStorage(new Storage("/path/to/logs", StorageLevel.DISK))
  .build();

server.open().join();
```

### Submitting operations via the client

{::options parse_block_html="true" /}
<div class="tab-content">
<div class="tab-pane active sync">
```java
Collection<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000)
);

CopycatClient client = CopycatClient.builder(members)
  .withTransport(new NettyTransport())
  .build();

client.open().join();

client.submit(new PutCommand("foo", "Hello world!")).get();

assert client.submit(new GetQuery("foo")).get().equals("Hello world!"));
```
</div>

{::options parse_block_html="true" /}
<div class="tab-pane async">
```java
Collection<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000)
);

CopycatClient client = CopycatClient.builder(members)
  .withTransport(new NettyTransport())
  .build();

client.open().thenRun(() -> {
  client.submit(new PutCommand("foo", "Hello world!")).thenRun(() -> {
    client.submit(new GetQuery("foo")).thenAccept(result -> {
      assert result.equals("Hello world!");
    });
  });
});
```
</div>
</div>

{% include common-links.html %}