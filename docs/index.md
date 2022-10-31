---
template: home.html
title: Atomix
hide:
  - navigation
  - toc
---

## What you get...

<div class="grid cards features" markdown>

- :octicons-container-24:{ .lg .middle } __Shared data structures__

    ---

    Atomix isn't just a simple key-value store. The runtime API supports common data structures that can be used by 
    applications to store and share state. Lists, maps, sets, and purpose-built data structures are provided to 
    enable a variety of use cases.

- :octicons-sync-24:{ .lg .middle } __Distributed coordination primitives__

    ---

    Primitives for solving common distributed systems problems like leader election, distributed locking, scheduling,
    and more. Atomix distributed coordination primitives enable developers to implement distributed systems solutions 
    without distributed systems expertise.

- :octicons-code-square-24:{ .lg .middle } __Cross-language compatibility__

    ---

    The Atomix runtime is built on gRPC, enabling SDKs in a variety of different languages. Applications can be 
    written in your language of choice, and containers or services can share state across languages.

- :octicons-database-24:{ .lg .middle } __Storage abstraction layer__

    ---

    The Atomix runtime provides a unified API across numerous databases and protocols, decoupling application code from 
    data stores to enable applications to be developed independent of the underlying architecture.

- :octicons-plug-24:{ .lg .middle } __Pluggable data stores__

    ---

    Atomix provides both custom distributed systems protocols and database proxies. Data storage is driven by 
    configuration, so Atomix-enabled applications can choose their own data stores and even swap between data stores 
    without changing a single line of code.

- :octicons-cloud-24:{ .lg .middle } __Built for Kubernetes__

    ---

    Atomix is built from the ground up for Kubernetes. Data stores and applications are managed via custom 
    resources, providing seamless integration with Kubernetes tools like kubectl and Helm.

</div>

## Simple flexibility

<div class="grids steps" markdown>

## :fontawesome-solid-code: Choose your language

<div class="grid left-text" markdown>

Write some stuff about SDKs here

=== ":fontawesome-brands-golang: Go"

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

=== ":fontawesome-brands-java: Java"

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

## Build your application :fontawesome-solid-toolbox:

<div class="grid right-text" markdown>

=== "Counter"

    ```go
    // Build the counter
    counter, err := atomix.Counter("my-counter").Get(context.Background())
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

Write some stuff about primitives here

</div>

## :fontawesome-solid-database: Define your data stores

<div class="grid left-text" markdown>

Write some stuff about data stores here

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

## Wire it all together :fontawesome-solid-diagram-project:

<div class="grid right-text" markdown>

```yaml
apiVersion: atomix.io/v3beta3
kind: StorageProfile
metadata:
  name: my-application-profile
spec:
  bindings:
    - store:
        name: my-consensus-store
```

Write some stuff about storage profiles here

</div>

</div>
