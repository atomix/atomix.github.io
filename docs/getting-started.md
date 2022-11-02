---
hide:
- navigation
---

# Getting Started

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
