---
layout: docs
project: atomix
menu: docs
title: Fault Tolerance
---

{:.no-margin-top}
Because Atomix falls on the CP side of the CAP theorem, it favors consistency over availability, particularly under failure. In order to ensure consistency, Atomix's [consensus protocol][raft-framework] requires that a majority of the cluster be alive and operating normally to service reads and writes. This means:

* A cluster of `1` replica can tolerate `0` failures
* A cluster of `2` replicas can tolerate `0` failures
* A cluster of `3` replicas can tolerate `1` failure
* A cluster of `4` replicas can tolerate `1` failure
* A cluster of `5` replicas can tolerate `2` failures

Failures in Atomix are handled by Raft's [leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm. When the Atomix cluster starts, a leader is elected. Leaders are elected by a round of voting wherein servers vote for a candidate based on the [consistency of its log](#consistency-model).

In the event of a failure of the leader, the remaining servers in the cluster will begin a new election and a new leader will be elected. This means for a brief period (seconds) the cluster will be unavailable.

In the event of a partition, if the leader is on a quorum side of the partition, it will continue to operate normally. Alternatively, if the leader is on a non-quorum side of the partition, the leader will detect the partition (based on the fact that it can no longer contact a majority of the cluster) and step down, and the servers on the majority side of the partition will elect a new leader. Once the partition is resolved, nodes on the non-quorum side of the partition will join the quorum side and receive updates to their log from the remaining leader.

{% include common-links.html %}