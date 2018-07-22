---
layout: user-manual
project: atomix
menu: user-manual
title: Supplying a Primitive Builder
---

By convention, primitives are constructed using primitive builders. Each primitive implementation provides an abstract and concrete builder:

```java
public abstract class DistributedLockBuilder
    extends DistributedPrimitiveBuilder<DistributedLockBuilder, DistributedLockConfig, DistributedLock>
    implements ProxyCompatibleBuilder<DistributedLockBuilder> {
  protected DistributedLockBuilder(String name, DistributedLockConfig config, PrimitiveManagementService managementService) {
    super(DistributedLockType.instance(), name, config, managementService);
  }
}
```

The builder accepts a `PrimitiveConfig` type on which to operate. Using a separate configuration class allows primitives to be configured via JSON/YAML configuration files or via the REST API. The configuration class should be a Java bean for which properties are mapped to JSON object fields using Jackson.

The implementation of a primitive builder should use the configured [`PrimitiveProtocol`][PrimitiveProtocol] to construct a [`ProxyClient`][ProxyClient] instance and from it a proxy object implementing the primitive interface:

```java
public class DistributedLockProxyBuilder extends DistributedLockBuilder {
  public DistributedLockProxyBuilder(String name, DistributedLockConfig config, PrimitiveManagementService managementService) {
    super(name, config, managementService);
  }

  @Override
  @SuppressWarnings("unchecked")
  public CompletableFuture<DistributedLock> buildAsync() {
    return newProxy(AtomicLockService.class, new ServiceConfig())
        .thenCompose(proxy -> new AtomicLockProxy(proxy, managementService.getPrimitiveRegistry()).connect())
        .thenApply(lock -> new DelegatingAsyncDistributedLock(lock).sync());
  }
}
```

{% include common-links.html %}
