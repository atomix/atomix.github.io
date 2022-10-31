<!--
SPDX-FileCopyrightText: 2022-present Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->

# Installation

## Prerequisites

* Kubernetes >= 1.18
* Helm 2.x

## Installing the runtime

The runtime is the collective controllers, components, and custom resources Atomix uses to configure and manage
Atomix-enabled applications in Kubernetes. To use Atomix in your Kubernetes applications, you first must deploy the
Atomix runtime. The runtime can be deployed via a Helm chart.

First, add the Atomix Helm charts repo to your Helm client:

```shell
helm repo add atomix https://charts.atomix.io
```

If you’ve already added the Atomix repo, ensure you have the latest charts in your Helm cache:

```shell
helm repo update
```

Once you’ve configured your Helm client, deploy the Atomix runtime by installing the atomix-runtime umbrella chart:

```shell
helm install -n kube-system atomix-runtime atomix/atomix-runtime
```

The `atomix-runtime` chart is an umbrella chart that includes controllers and CRDs for various storage types supported
by Atomix. It’s strongly recommended that you deploy the runtime in the `kube-system` namespace to prevent controllers
from being deleted when namespaces are deleted.

## Proxy injection

To enable Atomix runtime integration for your Kubernetes application, pods must be annotated with the
`proxy.atomix.io/inject` annotation.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: default
  annotations:
    proxy.atomix.io/inject: "true"
```

When annotated pods are deployed, the runtime controller will inject the Atomix sidecar proxy container into the pods.
The proxy is a mediation layer between the application and data stores, decoupling the application layer from the
storage layer to make the latter configurable without any modifications to the former.
