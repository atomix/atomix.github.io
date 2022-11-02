# Getting Started

## Writing your application

=== ":fontawesome-brands-golang:{ .xl .middle }"
    Add the Go SDK to your Go module:

    ```bash
    go get github.com/atomix/go-sdk
    ```

=== ":fontawesome-brands-java:{ .xl .middle }"
    Add the Java SDK to your Maven configuration:

    ```xml
    <dependency>
      <groupId>io.atomix</groupId>
      <artifactId>atomix-sdk</artifactId>
      <version>0.11.0</version>
    </dependency>
    ```

## Configuring the Helm repository

```shell
helm repo add atomix https://charts.atomix.io
```

## Installing the runtime controller

```shell
helm install -n kube-system atomix-runtime-controller atomix/atomix-runtime-controller --wait
```

## Installing storage controllers

```shell
helm install -n kube-system atomix-multi-raft-controller atomix/atomix-multi-raft-controller --wait
```

## Deploying a data store

```shell
kubectl create -f multi-raft-store.yaml
```

## Configuring the application

```shell
kubectl create -f my-application.yaml
```
