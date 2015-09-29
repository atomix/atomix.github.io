---
layout: content
project: copycat
menu: getting-started
title: Getting Started
pitch: Copycat in two minutes
first-section: getting-started
---

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

State machine commands alter state machine state:

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

  @Override
  public int groupCode() {
    return key.hashCode();
  }
  
  @Override
  public boolean groupEquals(Command command) {
    return command instanceof PutCommand && ((PutCommand) command).key.equals(key);
  }

}
```

State machine queries must only read the state machine state:

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
    return PersistenceLevel.EPHEMERAL;
  }

  public Object key() {
    return key;
  }

  @Override
  public int groupCode() {
    return key.hashCode();
  }
  
  @Override
  public boolean groupEquals(Command command) {
    return command instanceof PutCommand && ((PutCommand) command).key.equals(key);
  }
  
}
```

### Implementing state machine operations

State machine operations are registered within a state machine using the `StateMachineExecutor`:

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

### Starting a Raft server

```java
Address address = new Address("123.456.789.0", 5000);

Collection<Address> members = Arrays.asList(
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000),
  new Address("123.456.789.0", 5000)
);

RaftServer server = RaftServer.builder(address, members)
  .withTransport(new NettyTransport())
  .withStateMachine(new MapStateMachine())
  .withStorage(new Storage("/path/to/logs", StorageLevel.DISK))
  .build();

server.open().join();
```

### Submitting operations via the Raft client

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

CopycatClient client = CopycatClient.builder()
  .withTransport(new NettyTransport())
  .withMembers(members)
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