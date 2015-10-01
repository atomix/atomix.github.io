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
public class Value extends Resource {
  @Override
  protected Class<? extends StateMachine> stateMachine() {
    return ValueStateMachine.class;
  }
}
```

The `Resource` implementation must return a `StateMachine` class that will be configured to manage the resource's state.

```java
atomix.create(Value.class).thenAccept(value -> {
  System.out.println("Value resource created!");
});
```

When a resource is created via `Atomix.create(String, Class)`, the `StateMachine` class returned by the `Resource.stateMachine()` method will be constructed on each replica in the cluster. Once the state machine has been created on a majority of the replicas, the resource will be constructed and the returned `CompletableFuture` completed.

Resource state changes are submitted to the Atomix cluster as [Command][Command] or [Query][Query] implementations. See the documentation on Raft [commands](#commands) and [queries](#queries) for specific information regarding the use cases and limitations of each type.

To submit an operation to the Atomix cluster on behalf of the resource, expose a method that forwards a `Command` or `Query` to the cluster:

```java
public class Value<T> extends Resource {
  @Override
  protected Class<? extends StateMachine> stateMachine() {
    return ValueStateMachine.class;
  }

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
  private static class Get<T> implements Query<T> {
  }

  /**
   * Set command.
   */
  private static class Set<T> implements Command<T> {
    private Object value;

    private Set() {
    }

    private Set(Object value) {
      this.value = value;
    }
  }

  /**
   * Value state machine.
   */
  private static class ValueStateMachine extends StateMachine {
    private Object value;

    @Override
    protected void configure(StateMachineExecutor executor) {
      executor.register(Get.class, this::get);
    }

    /**
     * Gets the value.
     */
    private Object get(Commit<Get> commit) {
      return value;
    }

    /**
     * Sets the value.
     */
    private void set(Commit<Set> commit) {
      this.value = commit.operation().value;
    }
  }
}
```

{:.callout .callout-danger}
Important: See [Raft state machine documentation][state-machines] for details on cleaning commits from the log

{% include common-links.html %}