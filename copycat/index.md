---
layout: project
project: copycat
---

<div class="feature intro">
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <p>
Copycat is a fault-tolerant state machine replication framework. Built on the Raft consensus algorithm, it handles replication and persistence and enforces strict ordering of inputs and outputs, allowing developers to focus on single-threaded application logic. Its event-driven model allows for efficient client communication with replicated state machines, from simple key-value stores to wait-free locks and leader elections. You supply the state machine and Copycat takes care of the rest, making it easy to build robust, safe distributed systems.
        </p>
      </div>
    </div>
  </div>
</div>

<!--Simple -->
<div class="feature gray-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Simple</h2>
        <p>
          Copycat's simple but powerful programming model allows single-threaded state machines to be transparently scaled across a cluster.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/icons/scalable.svg">
      </div>
    </div>
  </div>
</div>

<div class="feature white-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-5 col-sm-offset-1">
        <img class="svg" src="/assets/img/icons/reliable.svg">
      </div>
      <div class="col-sm-6 text-right">
        <h2>Sophisticated</h2>
        <p>
          Copycat is built on one of the most advanced implementations of the Raft consensus algorithm, supporting membership changes, incremental compaction, snapshots, session-based client communication, state machine events, and more.
        </p>
      </div>
    </div>
  </div>
</div>

<!--Scalable -->
<div class="feature gray-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Scalable</h2>
        <p>Copycat clusters are resilient to failure and can be scaled to virtually any size, and read capacity can be scaled independently of write capacity.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/icons/scalable.svg">
      </div>
    </div>
  </div>
</div>

<div class="feature white-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-5 col-sm-offset-1">
        <img class="svg" src="/assets/img/icons/reactive.svg">
      </div>
      <div class="col-sm-6 text-right">
        <h2>Reactive</h2>
        <p>
          Copycat's event framework allows for efficient, wait-free interaction with replicated state machines while maintaining the same fault-tolerance and consistency guarantees.
        </p>
      </div>
    </div>
  </div>
</div>

<!-- <div class="feature showcase-white">
  <div class="container">
    <div class="row">
<div class="col-sm-6" markdown="1">
```java
public class MapStateMachine extends StateMachine {
  private Map<Object, Commit<PutCommand>> map = new HashMap<>();

  private Object put(Commit<PutCommand> commit) {
    map.put(commit.operation().key(), commit);
  }

  private Object get(Commit<GetQuery> commit) {
    Commit<PutCommand> value = map.get(commit.operation().key());
    commit.close();
    return value != null ? value.operation().value() : null;
  }

  private Object remove(Commit<RemoveCommand> commit) {
    Commit<PutCommand> value = map.remove(commit.operation().key());
    commit.clean();
    if (value != null) {
      value.clean();
      return value.operation().value();
    }
    return null;
  }
}
```
</div>
      <div class="col-sm-6 text-right">
        <h2>Extensible</h2>
        <p>Copycat allows user-defined state machines to be plugged directly into the Raft algorithm, enabling your application logic to be automatically replicated and fully consistent.</p>
      </div>
    </div>
  </div>
</div> -->

<!--Learn more -->
<div class="feature get-started colored-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-12 text-center">
        <h2>Ready to learn more?</h2>
        <p>
          <a href="/{{ page.project }}/docs/getting-started" class="btn btn-default btn-lg doc-btn">Get Started</a>
        </p>
      </div>
    </div>
  </div>
</div>