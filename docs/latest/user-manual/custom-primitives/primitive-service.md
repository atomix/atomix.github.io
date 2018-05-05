---
layout: user-manual
project: atomix
menu: user-manual
title: Creating the Primitive Service
---

Distributed primitives's state is managed in a replicated state machine. Primitive state machines are protocol agnostic, registering and accepting arbitrary state change operations. Additionally, state machines can publish events to clients.

## Service Proxy

The most convenient way to operate on a primitive service is to create a service interface that can be used as a proxy in primitive clients.

```java
public interface DistributedLockService {
  @Operation(value = "lock", type = OperationType.COMMAND)
  void lock();
  
  @Operation(value = "tryLock", type = OperationType.COMMAND)
  void tryLock(long timeout);

  @Operation(value = "unlock", type = OperationType.COMMAND)
  void unlock();
}
```

The service proxy interface must have methods annotated with the `@Operation` annotation. The annotation must specify a unique name for the operation and an operation type. The two types of operations are:
* `OperationType.COMMAND` - Indicates the method modifies the state of the primitive
* `OperationType.QUERY` - Indicates the method queries but _does not modify_ the state of the primitive

It's critical for correctness that operations that are marked `QUERY` _do not ever modify the state of the primitive service_.

## Client Proxy

Often, primitive services need to be able to communicate with client-side primitives, e.g. to send events or notify the client of changes. For this, primitives can also define a client-side proxy interface:

```java
public interface DistributedLockClient {
  @Event("locked")
  void locked(long index);
  
  @Event("failed")
  void failed();
}
```

Client proxy methods are annotated with the `@Event` method. We'll see in the next section how these two proxy interfaces fit in to the primitive service.

## Defining the Service

Once the proxy interfaces have been specified, you can construct the primitive service (or state machine). Primitive services are created by implementing the [`PrimitiveService`][PrimitiveService] interface or extending the [`AbstractPrimitiveService`][AbstractPrimitiveService] class. The primitive service should implement the primitive service interface:

```java
public class DefaultDistributedLockService extends AbstractPrimitiveService<DistributedLockClient, ServiceConfig> implements DistributedLockService {
  private Queue<SessionId> queue = new ArrayDeque<>();
  private SessionId lock;
    
  public DefaultDistributedLockService(ServiceConfig config) {
    super(DistributedLockClient.class, config);
  }
  
  @Override
  public void lock() {
    PrimitiveSession session = getCurrentSession();
    if (lock == null) {
      lock = session.sessionId();
      acceptOn(session, service -> service.locked(getCurrentIndex()));
    } else {
      queue.add(session.sessionId());
    }
  }
  
  @Override
  public void tryLock(long timeout)  {
    PrimitiveSession session = getCurrentSession();
    if (lock == null) {
      lock = session.sessionId();
      acceptOn(session, service -> service.locked(getCurrentIndex()));
    } else {
      queue.add(session.sessionId());
      if (timeout != -1) {
        getScheduler().schedule(Duration.ofMillis(timeout), () -> {
          queue.remove(session.sessionId());
          acceptOn(session, service -> service.failed());
        });
      }
    }
  }
  
  @Override
  public void unlock() {
    lock = queue.poll();
    if (lock != null) {
      acceptOn(lock, service -> service.locked(getCurrentIndex()));
    }
  }
}
```

Primitive services must be deterministic. The lock service above uses a client proxy to notify specific primitive clients of changes in the state of the service, and uses the service `Scheduler` to timeout lock attempts. The `Scheduler` is deterministic, ensuring all instances of the primitive service will see time progress at the same rate. It's critical that primitive services use the utilities provided to them rather than working outside the framework, which can lead to incorrect/inconsistent states.

## Listening for Disconnections

The lock service as currently designed can lead to a deadlock when a client acquires a lock and then crashes. Atomix provides service methods for listening for changes in clients' sessions, allowing the services to deterministically react to client disconnections.

```java
  @Override
  public void onExpire(PrimitiveSession session) {
    release(session.sessionId());
  }
  
  @Override
  public void onClose(PrimitiveSession session) {
    release(session.sessionId());
  }
  
  private void release(SessionId sessionId) {
    queue.removeIf(id -> id.equals(sessionId));
    if (lock != null && lock.equals(sessionId)) {
      unlock();
    }
  }
```

## Backing Up the State

Sometimes Atomix needs to backup the complete state of a primitive or copy the state of the primitive to another member of the cluster. To facilitate this, primitive services must provide a way to encode and decode their state. This is done in the `backup` and `restore` methods:

```java
  @Override
  public void backup(BackupOutput output) {
    output.writeObject(lock);
    output.writeObject(queue);
  }

  @Override
  public void restore(BackupInput input) {
    lock = input.readObject();
    queue = input.readObject();
  }
```

{% include common-links.html %}
