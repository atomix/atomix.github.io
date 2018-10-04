---
layout: user-manual
project: atomix
menu: user-manual
title: Kubernetes
---

Atomix 3.0.6 introduced new features to support running Atomix on Kubernetes. The [Atomix k8s][AtomixK8s] project was introduced as well to provide official [Helm][Helm] charts for running Atomix on Kubernetes.

To run Atomix on Kubernetes, download and install Minikube and Helm. Once installed, add the Atomix repo to Helm:

```
helm repo add atomix https://atomix.io/charts
```

You can view the charts available via the Atomix repo by running `helm search`:

```
helm search atomix/
```

To install Atomix on your Kubernetes cluster, simply run `helm install atomix/atomix`:

```
helm install atomix/atomix
```

The Helm chart will create a [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/), with each pod running a single Atomix node. Using StatefulSets ensures Atomix nodes have a persistent identity for consensus.

{:.callout .callout-warning}
When running the Helm chart on Minikube, you must disable pod anti-affinity by including `--set podAntiAffinity.enabled=false`

By default, the Helm chart configured three Atomix pods running a Raft partition group. To override the number of replicas, set the `replicas` value:

```
helm install --set replicas=5 atomix/atomix
```

By default, the Atomix nodes will not be accessible from outside the cluster. However, you can enable ingress by setting the `ingress.enabled` value:

```
helm install --set ingress.enabled=true atomix/atomix
```

When ingress is enabled, a rule matching the path for each pod will be set up to redirect HTTP requests to the respective node. So, you can reach the Atomix HTTP API by making a request to the path with the same name as the pod, e.g.:

```
helm install --name test --set ingress.enabled=true --set podAntiAffinity.enabled=false atomix/atomix
curl https://$(minikube ip)/test-atomix-0/v1/cluster/nodes --insecure
```

By default, the cluster is configured with a Raft management group and a Raft partition group with `n` partitions where `n` is the number of `replicas`. To override the Atomix configuration, specify a configuration via the `config` value:

`my-values.yaml`
```
config: |
  managementGroup {
    type: raft
    partitionSize: 3
    partitions: 1
    members: ${atomix.members}
  }

  partitionGroups.data {
    type: primary-backup
    partitions: 31
  }

  primitives.myMap {
    cache.enabled: true
    protocol {
      type: multi-primary
      backups: 2
    }
  }
```

```
helm install --name test -f my-values.yaml atomix/atomix
```

{% include common-links.html %}
