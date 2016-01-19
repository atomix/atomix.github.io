---
layout: content
project: atomix
menu: user-manual
title: Custom Resources
pitch: Custom resources
first-section: custom-resources
---

The Atomix API is designed to facilitate operating on arbitrary user-defined resources. When a custom resource is created via `Atomix.create`, an associated state machine will be created on each Atomix replica, and operations submitted by the resource instance will be applied to the replicated state machine. In that sense, think of a `Resource` instance as a client-side object and a `StateMachine` instance as the server-side representation of that object.

To define a new resource, simply extend the base `Resource` class:

```java
@ResourceTypeInfo(id=1, stateMachine=ValueStateMachine.class)
public class Value extends Resource<Value> {
  public Value(CopycatClient client) {
    super(client);
  }
}
```

The resource class must be annotated with the `@ResourceTypeInfo` annotation. This annotation is used to aid replicas in constructing resource state machines. The resource type `id` is can be any positive integer but must be unique, and the `stateMachine` indicates the state machine class to instantiate on each replica.

Additionally, resources must be registered via the Java `ServiceLoader` by identifying the class in a `META-INF/services/io.atomix.resource.Resource` file:
```
com.mycompany.Value
```

Custom resources can be instantiated on any `Atomix` instance using the `get` method and passing the resource class:

```java
atomix.get(Value.class).thenAccept(value -> {
  System.out.println("Value resource created!");
});
```

When a resource is created for the first time, the resource `StateMachine` will be created on each replica in the cluster. In order for the resource to be successfully created all replicas must have the resource class on their classpath. Once a state machine has been created on a majority of the active replicas, the resource will be constructed and the returned `CompletableFuture` completed.

Resource state machines must extend the base `ResourceStateMachine` class:

```java
public class ValueStateMachine extends ResourceStateMachine {
}
```

Commands to the state machine are implemented as public methods of the state machine which take a single `Commit` argument where the generic argument is the type of the command to accept:

```java
public class ValueStateMachine extends ResourceStateMachine {
  private Object value;

  public void set(Commit<SetCommand> commit) {
    try {
      this.value = commit.operation().value();
    } finally {
      commit.close();
    }
  }

}
```

Resource state changes are submitted to the Atomix cluster as [Command][Command] or [Query][Query] implementations. See the documentation on Raft [commands](#commands) and [queries](#queries) for specific information regarding the use cases and limitations of each type.

To submit an operation to the Atomix cluster on behalf of the resource, expose a method that forwards a `Command` or `Query` to the cluster:

```java
@ResourceTypeInfo(id=1, stateMachine=ValueStateMachine.class)
public class Value<T> extends Resource {

  /**
   * Returns the value.
   */
  public CompletableFuture<T> get() {
    return submit(new Get<>());
  }

  /**
   * Sets the value.
   */
  public CompletableFuture<Void> set(T value) {
    return submit(new Set<>(value));
  }

  /**
   * Get query.
   */
  public static class Get<T> implements Query<T>, Serializable {
  }

  /**
   * Set command.
   */
  public static class Set<T> implements Command<T>, Serializable {
    private Object value;

    public Set() {
    }

    public Set(Object value) {
      this.value = value;
    }

    @Override
    public CompactionMode compaction() {
      return CompactionMode.SNAPSHOT;
    }
  }

  /**
   * Value state machine.
   */
  public static class ValueStateMachine extends ResourceStateMachine {
    private Object value;

    /**
     * Gets the value.
     */
    public Object get(Commit<Get> commit) {
      try {
        return value;
      } finally {
        commit.close();
      }
    }

    /**
     * Sets the value.
     */
    public void set(Commit<Set> commit) {
      this.value = commit.operation().value;
    }
  }
}
```

{:.callout .callout-danger}
Important: See [Raft state machine documentation][state-machines] for details on log compaction

{% include common-links.html %}