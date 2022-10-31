---
template: home.html
title: Atomix
hide:
  - navigation
  - toc
---

## What you get

<div class="grid cards" markdown>

-   :octicons-container-24:{ .lg .middle } __Shared data structures__

    ---

    ...

    [:octicons-arrow-right-24: Getting started](#)

-   :octicons-sync-24:{ .lg .middle } __Distributed coordination primitives__

    ---

    ...

    [:octicons-arrow-right-24: Getting started](#)

-   :octicons-code-square-24:{ .lg .middle } __SDKs for multiple languages__

    ---

    ...

    [:octicons-arrow-right-24: Getting started](#)

-   :octicons-database-24:{ .lg .middle } __Storage abstraction layer__

    ---

    ...

    [:octicons-arrow-right-24: Getting started](#)

-   :octicons-plug-24:{ .lg .middle } __Pluggable data stores__

    ---

    ...

    [:octicons-arrow-right-24: Getting started](#)

-   :octicons-cloud-24:{ .lg .middle } __Built for Kubernetes__

    ---

    ...

    [:octicons-arrow-right-24: Getting started](#)

</div>

## How you get it

<div class="grids" markdown>

## :fontawesome-solid-code: Choose your language

<div class="grid left-text" markdown>

Write some stuff about SDKs here

=== ":fontawesome-brands-golang:"

    ```go
    // Get a string:string map
    m, err := atomix.Map[string, string]("my-map").
        Codec(generic.Scalar[string]()).
        Build(context.Background())
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

=== ":fontawesome-brands-java:"

    ```java
    // Create an Atomix client
    AtomixClient client = new AtomixClient();

    // Get the "foo" map
    Map<String, String> map = client.mapBuilder("foo").build();

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
        Build(context.Background())
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

## :fontawesome-solid-database: Configure your data store

<div class="grid left-text" markdown>

Write some stuff about data stores here

=== "Consensus"

    ```yaml
    apiVersion: consensus.atomix.io/v1beta1
    kind: ConsensusStore
    ```

=== "Etcd"

    ```yaml
    apiVersion: etcd.atomix.io/v1beta1
    kind: EtcdStore
    ```

=== "Gossip"

    ```yaml
    apiVersion: gossip.atomix.io/v1beta1
    kind: GossipStore
    ```

=== "PodMemory"

    ```yaml
    apiVersion: podmemory.atomix.io/v1beta1
    kind: PodMemoryStore
    ```

=== "Redis"

    ```yaml
    apiVersion: redis.atomix.io/v1beta1
    kind: RedisStore
    ```

=== "SharedMemory"

    ```yaml
    apiVersion: sharedmemory.atomix.io/v1beta1
    kind: SharedMemoryStore
    ```

</div>
</div>
