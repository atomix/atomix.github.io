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
  <span class="twemoji">
    <svg xmlns="http://www.w3.org/2000/svg" onclick="showLanguageGo();return false;" viewBox="0 0 640 512"><!--! Font Awesome Free 6.2.0 by @fontawesome - 
https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2022 Fonticons, Inc.--><path d="M400.1 194.8c-10.9 2.8-19.9 4.3-29.1 7.6-7.3 1.9-14.7 3.9-23.2 6.1l-.6.1c-4.2 1.2-4.6 1.3-8.5-3.2-4.7-5.3-8.1-8.7-14.6-11.9-19.7-9.6-38.7-6.8-56.4 4.7-21.2 13.7-32.1 34-31.8 59.2.3 25 17.4 45.5 41.2 48.9 22 2.8 39.8-4.6 53.8-20.5 2.1-2.6 4-5.3 6.1-8.3.8-1 1.5-2.1 2.3-3.3h-60.1c-6.5 0-8.1-4-5.9-9.3 4-9.7 11.5-25.9 15.9-34 .9-1.8 3.1-5.8 6.9-5.8h101.1c4.5-13.4 11.8-26.9 21.6-39.7 22.7-29.9 49.3-45.5 87.2-52 31.8-5.6 61.7-2.5 88.9 15.9 24.6 16.8 39.8 39.6 43.9 69.5 5.3 42.1-6.9 76.3-36.7 105.6-19.7 20.9-44.9 34-73.9 39.9-5.6 1-11.1 1.5-16.5 2-2.9.2-5.7.5-8.5.8-28.3-.6-54.2-8.7-76-27.4-15.3-13.3-25.9-29.6-31.1-48.5-3.7 7.3-8 14.4-14 21.1-21.6 29.6-50.9 48-87.9 52.9-30.6 4.1-58.9-1.8-83.9-20.5-23-17.5-36.1-40.5-39.5-69.2-4.1-34 5.9-65.4 26.4-91.3 22.2-29 51.5-47.4 87.3-53.9 29.3-6.2 57.3-1.9 82.6 15.3 16.5 10.9 28.3 25.8 36.1 43.9 1.9 2.8.6 4.4-3.1 5.3zm-351.8 5.6c-1.25 0-1.56-.6-.94-1.6l6.55-8.4c.62-.9 2.18-1.5 3.43-1.5H168.6c1.2 0 1.5.9.9 1.8l-5.3 8.1c-.6 1-2.2 1.9-3.1 1.9l-112.8-.3zM1.246 229.1c-1.246 0-1.558-.7-.934-1.6l6.543-8.4c.624-.9 2.182-1.6 3.425-1.6H152.4c1.2 0 1.8 1 1.5 1.9l-2.5 7.5c-.3 1.2-1.5 1.9-2.8 1.9l-147.354.3zm74.474 26.8c-.62.9-.31 1.8.93 1.8l67.95.3c.9 0 2.2-.9 2.2-2.1l.6-7.5c0-1.3-.6-2.2-1.9-2.2H83.2c-1.25 0-2.49.9-3.12 1.9l-4.36 7.8zm501.48-18c-.2-2.6-.3-4.8-.7-7-5.6-30.8-34-48.3-63.6-41.4-29 6.5-47.7 24.9-54.5 54.2-5.6 24.3 6.2 48.9 28.6 58.9 17.2 7.5 34.3 6.6 50.8-1.9 24.6-13.6 38-32.7 39.6-59.5-.1-1.2-.1-2.3-.2-3.3z"/></svg>
  </span>
</a>
<a href="#" class="atx-spotlight__language" id="atx-spotlight__language-java" title="Java" tabIndex="-1">
  <span class="twemoji">
    <svg xmlns="http://www.w3.org/2000/svg" onclick="showLanguageJava();return false;" viewBox="0 0 384 512"><!--! Font 
Awesome Free 6.2.0 by @fontawesome - 
https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2022 Fonticons, Inc.--><path d="M277.74 312.9c9.8-6.7 23.4-12.5 23.4-12.5s-38.7 7-77.2 10.2c-47.1 3.9-97.7 4.7-123.1 1.3-60.1-8 33-30.1 33-30.1s-36.1-2.4-80.6 19c-52.5 25.4 130 37 224.5 12.1zm-85.4-32.1c-19-42.7-83.1-80.2 0-145.8C296 53.2 242.84 0 242.84 0c21.5 84.5-75.6 110.1-110.7 162.6-23.9 35.9 11.7 74.4 60.2 118.2zm114.6-176.2c.1 0-175.2 43.8-91.5 140.2 24.7 28.4-6.5 54-6.5 54s62.7-32.4 33.9-72.9c-26.9-37.8-47.5-56.6 64.1-121.3zm-6.1 270.5a12.19 12.19 0 0 1-2 2.6c128.3-33.7 81.1-118.9 19.8-97.3a17.33 17.33 0 0 0-8.2 6.3 70.45 70.45 0 0 1 11-3c31-6.5 75.5 41.5-20.6 91.4zM348 437.4s14.5 11.9-15.9 21.2c-57.9 17.5-240.8 22.8-291.6.7-18.3-7.9 16-19 26.8-21.3 11.2-2.4 17.7-2 17.7-2-20.3-14.3-131.3 28.1-56.4 40.2C232.84 509.4 401 461.3 348 437.4zM124.44 396c-78.7 22 47.9 67.4 148.1 24.5a185.89 185.89 0 0 1-28.2-13.8c-44.7 8.5-65.4 9.1-106 4.5-33.5-3.8-13.9-15.2-13.9-15.2zm179.8 97.2c-78.7 14.8-175.8 13.1-233.3 3.6 0-.1 11.8 9.7 72.4 13.6 92.2 5.9 233.8-3.3 237.1-46.9 0 0-6.4 16.5-76.2 29.7zM260.64 353c-59.2 11.4-93.5 11.1-136.8 6.6-33.5-3.5-11.6-19.7-11.6-19.7-86.8 28.8 48.2 61.4 169.5 25.9a60.37 60.37 0 0 1-21.1-12.8z"/></svg>
  </span>
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
