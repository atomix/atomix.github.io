---
template: home.html
title: Atomix
hide:
  - navigation
  - toc
---

<!-- Section header -->
<header class="md-typeset">
  <h1 id="how-does-it-work">
    How does it work?
    <a href="#how-does-it-work" class="headerlink" title="Permanent link">¶</a>
  </h1>
</header>

<!-- Section content -->
<div class="atx-spotlight" markdown>

<!-- Choose a language -->
<figure class="atx-spotlight__feature" markdown>
<figcaption class="md-typeset" markdown>
## :fontawesome-solid-language: Choose a language

The Atomix runtime API is built on gRPC, enabling SDKs for developing Kubernetes applications using a variety of
different languages. The SDK for each language adheres to the patterns and idioms of that language, presenting APIs
that are natural for developers to adopt in their language of choice.

<span class="language-select" markdown>Select a language :octicons-arrow-right-24:</span>
</figcaption>
<a href="#" class="atx-spotlight__language atx-spotlight__language-selected" id="atx-spotlight__language-golang" 
title="Go" tabIndex="-1">
  <img
    src="images/golang.svg"
    alt="Built-in search"
    onclick="showLanguageGo();return false;"
  />
</a>
<a href="#" class="atx-spotlight__language" id="atx-spotlight__language-java" title="Java" tabIndex="-1">
  <img
    src="images/java.svg"
    alt="Java"
    onclick="showLanguageJava();return false;"
  />
</a>
</figure>

<!-- Write your application -->
<figure class="atx-spotlight__feature" markdown>
<figcaption class="md-typeset" markdown>
## :fontawesome-solid-code: Write your application

Atoms are the building blocks of distributed systems. Choose from a variety of different data structures to store
application state or share state across pod or services. Distributed coordination primitives enable safe interaction
with other nodes and services within the Kubernetes cluster. Use the atoms that are right for your use case.

[:octicons-arrow-right-24: Learn more](/user-guide/development/atoms/)
</figcaption>
<div class="atx-spotlight__code md-typeset" id="atx-spotlight__code-golang" markdown>
=== "Counter"

    ```go
    // Build the counter
    counter, err := atomix.Counter("my-counter").
        Get(context.Background())
    if err != nil {
        ...
    }

    // Increment the counter
    count, err = counter.Increment(context.Background())
    if err != nil {
        ...
    }

    // Get the counter value
    value, err = counter.Get(context.Background())
    if err != nil {
        ...
    }
    ```

=== "LeaderElection"

    ```go
    // Build the leader election
    election, err := atomix.LeaderElection("my-counter").
        Get(context.Background())
    if err != nil {
        ...
    }

    // Get the current leadership term
    term, err := election.GetTerm(context.Background())
    if err != nil {
        ...
    }

    // Enter the election
    term, err = election.Enter(context.Background())
    if err != nil {
        ...
    }
    ```

=== "List"

    ```go
    // Get a string list
    l, err := atomix.List[string]("my-list").
        Codec(generic.Scalar[string]()).
        Get(context.Background())
    if err != nil {
        ...
    }

    // Append a value to the list
    err = l.Append(context.Background(), "Hello world!")
    if err != nil {
        ...
    }

    // Iterate through the items in the list
    items, err := l.Items(context.Background())
    if err != nil {
        ...
    }
    for {
        item, err := items.Next()
        if err == io.EOF {
            break
        }
        ...
    }
    ```

=== "Lock"

    ```go
    // Build the lock
    l, err := atomix.Lock("my-lock").
        Get(context.Background())
    if err != nil {
        ...
    }

    // Acquire the lock
    if err := l.Lock(context.Background()); err != nil {
        ...
    }

    // Do stuff...

    // Release the lock
    if err := l.Unlock(context.Background()); err != nil {
        ...
    }
    ```

=== "Map"

    ```go
    // Get a string:string map
    m, err := atomix.Map[string, string]("my-map").
        Codec(generic.Scalar[string]()).
        Get(context.Background())
    if err != nil {
        ...
    }

    // Write to the map
    _, err = m.Put(context.Background(), "foo", "bar")
    if err != nil {
        ...
    }

    // Read from the map
    entry, err := m.Get(context.Background(), "foo")
    if err != nil {
        ...
    }
    ```

=== "MultiMap"

    ```go
    // Get a string:string multimap
    m, err := atomix.MultiMap[string, string]("my-multimap").
        Codec(generic.Scalar[string]()).
        Get(context.Background())
    if err != nil {
        ...
    }

    // Write to the multimap
    _, err = m.Put(context.Background(), "foo", "bar")
    if err != nil {
        ...
    }

    // Write to the multimap
    _, err = m.Put(context.Background(), "foo", "baz")
    if err != nil {
        ...
    }

    // Read from the multimap
    values, err := m.Get(context.Background(), "foo")
    if err != nil {
        ...
    }
    ```

=== "Set"

    ```go
    // Get a string set
    l, err := atomix.Set[string]("my-set").
        Codec(generic.Scalar[string]()).
        Get(context.Background())
    if err != nil {
        ...
    }

    // Add a value to the set
    err = l.Add(context.Background(), "Hello world!")
    if err != nil {
        ...
    }

    // Check if the set contains the added value
    if ok, err := l.Contains(context.Background()); err != nil {
        ...
    } else if ok {
        ...
    }
    ```

=== "Value"

    ```go
    // Get a string value
    v, err := atomix.Value[string]("my-value").
        Codec(generic.Scalar[string]()).
        Get(context.Background())
    if err != nil {
        ...
    }

    // Set the value
    err = v.Set(context.Background(), "Hello world!")
    if err != nil {
        ...
    }

    // Get the value
    value, err := v.Get(context.Background())
    if err != nil {
        ...
    }
    ```
</div>
<div class="atx-spotlight__code md-typeset" id="atx-spotlight__code-java" markdown>
=== "Counter"

    ```java
    // Get the "foo" counter
    AtomicCounter counter = AtomicCounter.builder()
        .withName("foo")
        .build();

    // Increment the counter
    long value = counter.incrementAndGet();

    // Get the counter value
    value = counter.get();
    ```

=== "Map"

    ```java
    // Get the "foo" map
    Map<String, String> map = AtomicMap.builder()
        .withName("foo")
        .withSerializer(mySerializer)
        .build();

    // Write to the map
    map.put("foo", "bar");

    // Read from the map
    Entry<string, string> entry = map.get("foo");
    ```
</div>
</figure>

<!-- Deploy data stores -->
<figure class="atx-spotlight__feature" markdown>
<figcaption class="md-typeset" markdown>
## :fontawesome-solid-database: Deploy data stores

The Atomix runtime API acts as an abstraction layer for data stores, decoupling your application's code from specific
databases and protocols, and enabling developers to choose the tools they like without concern for vendor lock-in.

[:octicons-arrow-right-24: Learn more](/user-guide/deployment/data-stores/)
</figcaption>
<div class="atx-spotlight__code md-typeset" markdown>
=== "Consensus"

    ```yaml
    apiVersion: consensus.atomix.io/v1beta1
    kind: ConsensusStore
    metadata:
      name: my-consensus-store
    spec:
      replicas: 3
      groups: 30
    ```

=== "Etcd"

    Coming soon!

=== "Gossip"

    Coming soon!

=== "PodMemory"

    ```yaml
    apiVersion: podmemory.atomix.io/v1beta1
    kind: PodMemoryStore
    ```

=== "Redis"

    Coming soon!

=== "SharedMemory"

    ```yaml
    apiVersion: sharedmemory.atomix.io/v1beta1
    kind: SharedMemoryStore
    ```
</div>
</figure>

<!-- Wire everything together -->
<figure class="atx-spotlight__feature" markdown>
<figcaption class="md-typeset" markdown>
## :fontawesome-solid-diagram-project: Wire everything together

Atomix is designed around the same principles of cloud-native architecture that are familiar to Kubernetes
developers. Storage is defined for each application via the `StorageProfile` custom resource. A tag-based routing
system enables applications to use multiple data stores while allowing application developers and their users to
optimize applications and the atoms within them without having to change a single line of code.

[:octicons-arrow-right-24: Learn more](/user-guide/deployment/storage-profiles)
</figcaption>
<div class="atx-spotlight__code md-typeset" markdown>
```yaml
apiVersion: atomix.io/v3beta3
kind: StorageProfile
metadata:
  name: my-application-profile
spec:
  bindings:
    - store:
        name: consensus-store
      tags:
        - my-app
        - persistent
    - store:
        name: cache-store
      tags:
        - my-app
        - volatile
```
</div>
</figure>
</div>
