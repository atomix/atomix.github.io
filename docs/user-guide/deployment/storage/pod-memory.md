<!--
SPDX-FileCopyrightText: 2022-present Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->

# PodMemoryStore

The `PodMemoryStore` is similar to `SharedMemoryStore`, but state is local to each pod. The `PodMemoryStore` holds
primitives in memory within the runtime proxy sidecar, effectively enabling containers to share memory within the pod
using primitives.

![PodMemoryStore](/images/pod-memory.png#only-light){: width="800" }
![PodMemoryStore](/images/pod-memory-dark.png#only-dark){: width="800" }

```yaml
apiVersion: podmemory.atomix.io/v1beta1
kind: PodMemoryStore
metadata:
  name: my-pod-memory-store
```
