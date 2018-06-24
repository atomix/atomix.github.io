---
layout: user-manual
project: atomix
menu: user-manual
title: What is Atomix?
---

Atomix is a tool for solving common distributed systems problems in a variety of different ways. It is unopinionated about the problems it solves, instead providing primitives with which to solve problems. Some examples of the primitives it provides are:
* Distributed data structures (maps, sets, trees, etc)
* Distributed communication (direct, publish-subscribe, etc)
* Distributed coordination (locks, leader elections, semaphores, etc)
* Group membership

Each of these primitives can be accessed in a variety of different ways, including:
* Asynchronous APIs
* Synchronous APIs
* REST API

Similarly, they can be configured either in code or in configuration files:
* Java builders
* HOCON configurations
* JSON configurations

This flexibility allows architects to build extremely diverse systems.

### ONOS Use Case

The [ONOS project](http://onosproject.org) for which Atomix is primarily developed is an excellent use case in using the features of Atomix outlined above. At its core, ONOS uses Atomix group membership and messaging for cluster management and communication. Additionally, stores in ONOS rely heavily on Atomix primitives for state replication and coordination. Using Atomix allows ONOS engineers to choose the ideal primitive for the use case of each individual store. For example, some stores may use synchronous primitives for simplicity, while others may use asynchronous (non-blocking) primitives for concurrency. Some stores use Atomix primitives to build higher-level custom replication protocols. The unopinionated nature of Atomix allows engineers to use the best tool for the job, and the ability to encapsulate most of the complexity of distributed systems in Atomix primitives has reduced the barrier to entry for new ONOS contributors.

{% include common-links.html %}
