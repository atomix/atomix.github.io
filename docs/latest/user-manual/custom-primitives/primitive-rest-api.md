---
layout: user-manual
project: atomix
menu: user-manual
title: Supporting REST API Access
---

Primitives are designed to be accessed in a variety of ways. Even custom primitives can be operated on via the REST API provided by the Atomix agent.

To support REST API access for a custom primitive, override the `newResource` method of the [`PrimitiveType`][PrimitiveType] implementation:

```java
@Override
public PrimitiveResource newResource(DistributedLock primitive) {
  return new DistributedLockResource(primitive.async());
}
```

The lock resource must use JAX-RS annotations:

```java
public class DistributedLockResource implements PrimitiveResource {
  private static final Logger LOGGER = LoggerFactory.getLogger(DistributedLockResource.class);

  private final AsyncDistributedLock lock;

  public DistributedLockResource(AsyncDistributedLock lock) {
    this.lock = lock;
  }

  @POST
  @Path("/lock")
  @Produces(MediaType.APPLICATION_JSON)
  public void lock(@Suspended AsyncResponse response) {
    lock.lock().whenComplete((result, error) -> {
      if (error == null) {
        response.resume(Response.ok(result.value()).build());
      } else {
        LOGGER.warn("{}", error);
        response.resume(Response.serverError().build());
      }
    });
  }

  @POST
  @Path("/unlock")
  public void unlock(@Suspended AsyncResponse response) {
    lock.unlock().whenComplete((result, error) -> {
      if (error == null) {
        response.resume(Response.ok().build());
      } else {
        LOGGER.warn("{}", error);
        response.resume(Response.serverError().build());
      }
    });
  }
}
```

Note that all primitive resource methods must be annotated with a `@Path` since the primitive management API creates primitives by name using the resource path.

{% include common-links.html %}
