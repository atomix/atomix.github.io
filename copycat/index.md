---
layout: project
project: copycat
---

<div class="feature intro">
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <p>
Copycat enables you to turn simple application logic into a consistent, fault tolerant distributed system. Build a custom distributed key-value store, distributed lock, distributed queue, or message bus. You supply the state machine and Copycat takes care of the rest, making it easy to build robust, safe distributed systems.
        </p>
      </div>
    </div>
  </div>
</div>

<!-- Reliable -->
<div class="feature gray-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Reliable</h2>
        <p>
          Copycat provides reliable data consistency guarantees that are maintained even when machine or network failures occur.
        </p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/icons/reliable.svg">
      </div>
    </div>
  </div>
</div>

<div class="feature white-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-5 col-sm-offset-1">
        <img class="svg" src="/assets/img/icons/consensus.svg">
      </div>
      <div class="col-sm-6 text-right">
        <h2>Raft Consensus</h2>
        <p>
          Copycat features a sophisticated implementation of the Raft consensus algorithm with support for cluster membership changes, log compaction, and bi-directional client sessions.
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

<!--Scalable -->
<div class="feature gray-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Scalable</h2>
        <p>Copycat scales along with the rest of your system, providing high read throughput while maintaining strong write consistency.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/icons/scalable.svg">
      </div>
    </div>
  </div>
</div>

<!--Resilient -->
<div class="feature white-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-5 col-sm-offset-1">
        <img class="svg" src="/assets/img/icons/resilient.svg">
      </div>
      <div class="col-sm-6 text-right">
        <h2>Resilient</h2>
        <p>Copycat clusters are resilient to failure, automatically replacing cluster members as needed without any data loss.</p>
      </div>
    </div>
  </div>
</div>

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