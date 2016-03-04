---
layout: docs
project: atomix
menu: docs
title: Threading Model
---

{:.no-margin-top}
Atomix is designed to be used in an asynchronous manner that provides easily understood guarantees for users. All usage of asynchronous APIs such as [CompletableFuture] are carefully orchestrated to ensure that various callbacks are executed in a deterministic manner. To that end, Atomix provides the following guarantees:

* Callbacks for any given object are guaranteed to always be executed on the same thread.
* `CompletableFuture`s are guaranteed to be completed in the same order in which they were created.

### Asynchronous API Usage

Atomix's API makes heavy use of Java 8's [CompletableFuture][CompletableFuture] for asynchronous completion of method calls. The asynchronous API allows users to execute multiple operations concurrently instead of blocking on each operation in sequence. For information on the usage of `CompletableFuture` see the [documentation][CompletableFuture].

### Synchronous API Usage

Atomix makes heavy use of Java 8's [CompletableFuture][CompletableFuture] in part because it allows users to easily block on asynchronous method calls. To block and wait for a `CompletableFuture` result instead of registering an asynchronous callback, simply use the `get()` or `join()` methods.

```java
// Get the "foo" key from a map
CompletableFuture<String> future = map.get("foo");

// Block to wait for the result
String result = future.get();
```

{% include common-links.html %}