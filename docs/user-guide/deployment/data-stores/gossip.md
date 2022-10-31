<!--
SPDX-FileCopyrightText: 2022-present Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->

# GossipStore

The gossip store is an eventually consistent storage type that replicates primitive using a gossip protocol. To use the
gossip protocol, create a GossipStore:

```yaml
apiVersion: gossip.atomix.io/v1beta1
kind: GossipStore
metadata:
  name: my-gossip-store
```

By default, the gossip will occur between pods that are bound to the gossip protocol via their StorageProfile. If all
pods go down, the state will be lost. To store the state in a centralized gossip store, set the number of replicas > 0:

```yaml
apiVersion: gossip.atomix.io/v1beta1
kind: GossipStore
metadata:
  name: my-gossip-store
spec:
  replicas: 3
```
