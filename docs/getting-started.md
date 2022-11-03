# Getting Started

## Writing an application

Atomix provides language-specific SDKs for building applications.

=== ":fontawesome-brands-golang:{ .xl .middle }"

    The [Go SDK](https://github.com/atomix/go-sdk) requires at least Go 1.19 for generics support.
    To add the SDK to your Go module:

    ```bash
    go get github.com/atomix/go-sdk@v0.10.0
    ```

    Distributed primitives are created using a builder pattern:

    ```go
    m, err := atomix.Map[string, string]("my-map").
        Codec(generic.Scalar[string]())
        Get(context.Background())
    if err != nil {
        log.Fatal(err)
    }
    ```

    Each distributed primitive must be assigned a `string` name, and state is shared across pods that
    reference primitives of the same name. For example, if `pod-1` creates a primitive named `foo`,
    and `pod-2` creates a primitive named `foo`, both primitives will point to the same logical state.

    !!! note
        
        The SDK is designed to run inside a Kubernetes pod where it connects to the Atomix runtime proxy 
        sidecar container on a fixed port and therefore does not need to be configured by the application.
        For advanced configuration and testing, see the [Go SDK](user-guide/development/go) documentation.

    Once you've created your desired primitive, use the interface to store and share state with other pods:

    ```go
    entry, err := m.Put(context.Background(), "foo", "bar")
    if err != nil {
        log.Fatal(err)
    }

    entry, err = m.Get(context.Background(), "foo")
    if err != nil {
        log.Fatal(err)
    }
    ```

    For detailed documentation on the primitives and APIs available in the Go SDK, see the
    [user guide](user-guide/development/go).

=== ":fontawesome-brands-java:{ .xl .middle }"
    The [Java SDK](https://github.com/atomix/java-sdk) is distributed through Maven Central.
    To add the SDK to your Maven dependencies:

    ```xml
    <dependency>
      <groupId>io.atomix</groupId>
      <artifactId>atomix-sdk</artifactId>
      <version>0.1.1</version>
    </dependency>
    ```

    A builder pattern is used to construct distributed primitives:

    ```java
    AtomicMap<String, String> map = AtomicMap.builder("my-map")
        .withSerializer(serializer)
        .build()
    ```

    Each primitive interface exposes empty

## Installing the runtime

Atomix extends the Kubernetes API with numerous [custom resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) 
and controllers to orchestrate stores and applications. Collectively, these components are referred to as the
Atomix runtime.

To install the runtime, it's recommended you use the `atomix-runtime` Helm chart, which can be found in the
Atomix Helm charts repo at `https://charts.atomix.io`:

```shell
> helm repo add atomix https://charts.atomix.io
```

Update the Helm repository cache to ensure you have the latest copy of the `atomix-runtime` chart:

```shell
> helm repo update
```

The runtime should be installed in the `kube-system` namespace, where other Kubernetes controllers are deployed,
to prevent controllers from being deleted:

```shell
> helm install -n kube-system atomix-runtime atomix/atomix-runtime --wait
```

The `atomix-runtime` chart deploys numerous controllers to the target namespace, each providing orchestration
for a different type of [data store](user-guide/deployment/data-stores/).

```shell
> kubectl get pods -n kube-system
NAME                                                       READY   STATUS    RESTARTS   AGE
atomix-runtime-consensus-controller-5f6cd7c8b5-qzzl8       1/1     Running   0          104s
atomix-runtime-controller-5fd8c86f99-h7tp4                 1/1     Running   0          104s
atomix-runtime-pod-memory-controller-857b8dc557-js7lf      1/1     Running   0          104s
atomix-runtime-shared-memory-controller-8565cd5f94-m7s9v   1/1     Running   0          104s
...
```

## Deploying a data store

To deploy an application, you must first deploy a [data store](user-guide/deployment/data-stores) to be used
by the application. The runtime provides a variety of data stores to choose from, but the simplest is the
[`SharedMemoryStore`](user-guide/deployment/data-stores/shared-memory):

```yaml title="data-store.yaml"
apiVersion: sharedmemory.atomix.io/v1beta1
kind: SharedMemoryStore
metadata:
  name: my-data-store
spec: {}
```

Once you've defined the store, deploy it using `kubectl`:

```shell
> kubectl create -f data-store.yaml
```

The `SharedMemoryStore` will deploy a single pod to hold primitive state in memory. To enable persistence and/or 
replication, [explore the data stores](user-guide/deployment/data-stores).

## Configuring the application

```yaml title="storage-profile.yaml"
apiVersion: atomix.io/v3beta3
kind: StorageProfile
metadata:
  name: my-application
spec:
  bindings:
    - store:
        name: my-data-store
```

```shell
> kubectl create -f storage-profile.yaml
```

```yaml title="application.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-application
spec:
  selector:
    matchLabels:
      name: my-application
  template:
    metadata:
      labels:
        name: my-application
      annotations:
        proxy.atomix.io/inject: "true"
        proxy.atomix.io/profile: "my-application"
    spec:
      ...
```

```shell
> kubectl create -f application.yaml
```
