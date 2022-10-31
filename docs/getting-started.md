---
hide:
- navigation
---

# Getting Started

![Runtime](/images/runtime.png#only-light){: width="800" align=right }
![Runtime](/images/runtime-dark.png#only-dark){: width="800" align=right }

Atomix is a toolkit for building data-centric Kubernetes applications. Built around a gRPC API, Atomix applications
can be written in several languages, providing a common set of building blocks developed over the course of a decade,
and designed to solve a variety of common distributed systems problems. The Atomix runtime employs cloud-native
design principles to decouple your application's code from the data stores they use, enabling operators to swap
between a variety of databases and distributed systems protocols without changing a single line of code.

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
