---
template: home.html
title: Atomix
hide:
  - navigation
  - toc
---

## Built on the cloud, for the cloud.

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

- :octicons-cloud-24:{ .lg .middle } __Kubernetes-native architecture__

    ---

    Atomix is built from the ground up for Kubernetes. Data stores and applications are managed via custom 
    resources, providing seamless integration with Kubernetes tools like kubectl and Helm.

</div>

## Simple flexibility.

<div class="grids steps" markdown>

<div class="grid grid-left" markdown>

<div class="step" markdown>
## :fontawesome-solid-language: Choose your language

Application development starts with the SDKs. Atomix is built on top of Protobuf and gRPC, enabling SDKs for a 
variety of different languages. SDKs adhere to the patterns and idioms of the associated language to present APIs 
that are natural for developers to adopt in their language of choice.

[:octicons-arrow-right-24: Learn more](/user-guide/development/)
</div>

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

<div class="grid grid-right" markdown>

<div class="step" markdown>
## :fontawesome-solid-code: Code your application

Atoms are the building blocks of distributed systems. Choose from a variety of different data structures to store
application state or share state across pod or services. Distributed coordination primitives enable safe interaction
with other nodes and services within the Kubernetes cluster. Use the atoms that are right for your use case.

[:octicons-arrow-right-24: Learn more](/user-guide/development/atoms/)
</div>

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

</div>

<div class="grid grid-left" markdown>

<div class="step" markdown>
## :fontawesome-solid-database: Deploy your data stores

The Atomix runtime API acts as an abstraction layer for data stores, decoupling your application's code from specific 
databases and protocols, and enabling developers to choose the tools they like without concern for vendor lock-in.

[:octicons-arrow-right-24: Learn more](/user-guide/deployment/data-stores/)
</div>

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

<div class="grid grid-right" markdown>

<div class="step" markdown>
## :fontawesome-solid-diagram-project: Wire everything together

Atomix is designed around the same principles of cloud-native architecture that are familiar to Kubernetes 
developers. Storage is defined for each application via the `StorageProfile` custom resource. A tag-based routing
system enables applications to use multiple data stores while allowing application developers and their users to
optimize applications and the atoms within them without having to change a single line of code.

[:octicons-arrow-right-24: Learn more](/user-guide/deployment/storage-profiles)
</div>

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

</div>
