---
layout: user-manual
project: atomix
menu: user-manual
title: Transactions
---

Atomix provides a number of distributed primitives for various use cases, and each primitive operation occurs atomically. But multiple operations are not performed atomically, and sometimes a single primitive or a single operation is not sufficient. Atomix provides support for transactions to allow users to execute multiple operations on multiple primitives replicated in multiple partition groups as a single atomic operation.

Transactions are implemented in a fault-tolerant [two phase commit](https://en.wikipedia.org/wiki/Two-phase_commit_protocol) protocol. When a transaction is created, Atomix records all the operations being performed within the transaction. When the transaction is committed, Atomix prepares the operations for each primitive used in the transaction and executes the first phase of the two-phase commit protocol against each partition for each primitive. If the prepare phase is successful, Atomix commits the changes. If the prepare phase fails, the changes are rolled back.

### Tolerating Failures During Transactions

Two-phase commit protocols suffer from a variety of deficiencies in terms of tolerating failures. The variant that most specifically applies to Atomix is coordinator failures. If a node crashes between preparing and committing a transaction, some primitive elements can remain locked forever. To avoid partially completed transactions hanging in the cluster, Atomix detects failures and elects a new coordinator to take over a crashed node's transactions. The elected coordinator then either commits or rolls back each transaction based on the progress it has made.

## Working with Transactions

Working with transactions is much like working with any other primitive in Atomix. To create a transaction, first create a [`TransactionBuilder`][TransactionBuilder]:

```java
Transaction transaction = atomix.transactionBuilder()
  .withIsolation(Isolation.REPEATABLE_READS)
  .build();
```

Transactions can be configured with different [isolation levels](https://en.wikipedia.org/wiki/Isolation_(database_systems)) which dictate how the client perceives concurrent changes to transactional primitives. The supported isolation levels are:
* `Isolation.READ_COMMITTED`
* `Isolation.REPEATABLE_READS`

Once a transaction has been created, start the transaction by calling `begin()`:

```java
Transaction transaction = atomix.transactionBuilder()
  .withIsolation(Isolation.REPEATABLE_READS)
  .build();

transaction.begin();
```

Within the context of the transaction, primitives can be created and operated on by building them _through_ the transaction instance.

```java
MultiRaftProtocol protocol = MultiRaftProtocol.builder()
  .withReadConsistency(ReadConsistency.LINEARIZABLE)
  .build();

TransactionalMap<String, String> map = transaction.mapBuilder("my-map")
  .withProtocol(protocol)
  .build();
```

The `Transactional*` primitives created within a transaction are backed by the same partitions in which a standard primnitive is replicated. In other words, changes in an `AtomicMap` named `foo` will be visible in a `TransactionalMap` named `foo` and configured with the same protocol and vice versa. Just as with standard primitives, transactional primitives, transactional primitives must be configured with a protocol indicating the protocol and partitions that back the primitive.

Once a transactional primitive has been created, operate on the primitive as normal:

```java
if (!map.containsKey("foo")) {
  map.put("foo", "bar");
}
```

{:.callout .callout-info}
The operations performed within a transaction will not be visible to other processes or other instances of the primitive until the transaction is committed.

You can create as many primitives as you want within a single transaction:

```java
TransactionalSet<String> set = transaction.setBuilder("my-set")
  .withProtocol(protocol)
  .build();

if (set.add("foo")) {
  set.remove("bar");
} else {
  set.remove("foo");
}
```

Once you've completed operating on the primitive, commit the transaction by calling `commit()`:

```java
if (transaction.commit() == CommitStatus.SUCCESS) {
  // Transaction succeeded!
}
```

{:.callout .callout-warning}
Transactions will fail if concurrent updates to the primitive(s) used in the transaction result in write conflicts. It's important that you monitor the `commit()` result to determine whether to retry a transaction.

{% include common-links.html %}
