<!--
SPDX-FileCopyrightText: 2022-present Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->

# SharedMemoryStore

The SharedMemoryStore is an in-memory store for volatile state like a cache. State is shared across pods but may be lost
in the event the store pod crashes.

![SharedMemoryStore](/images/shared-memory.png#only-light){: width="800" }
![SharedMemoryStore](/images/shared-memory-dark.png#only-dark){: width="800" }

```yaml
apiVersion: sharedmemory.atomix.io/v1beta1
kind: SharedMemoryStore
metadata:
  name: my-shared-memory-store
```
