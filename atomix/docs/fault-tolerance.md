---
layout: docs
project: atomix
menu: docs
title: Fault Tolerance
---

{:.no-margin-top}
Since Atomix falls on the CP side of the [CAP theorem][CAP], it favors consistency over availability, particularly under failure. In order to ensure consistency, Atomix's [consensus protocol][raft] requires that a majority quorum of the cluster be alive and operating normally in order to service reads and writes. This means:

* A cluster of `1` replica can tolerate `0` failures
* A cluster of `2` replicas can tolerate `0` failures
* A cluster of `3` replicas can tolerate `1` failure
* A cluster of `4` replicas can tolerate `1` failure
* A cluster of `5` replicas can tolerate `2` failures

Failures in Atomix are handled by Raft's [leader election](https://en.wikipedia.org/wiki/Leader_election) algorithm. When the Atomix cluster starts, a leader is elected. Leaders are elected by a round of voting wherein servers vote for a candidate based on the [consistency of its log][consistency-model].

The general rule of thumb for Atomix is that nothing happens without a leader and electing a leader requires that a majority quorum to be able to communicate with each other. These constraints ensure that data remains [consistent][consistency-model] when failures do occur.

## Node Failures

In the event that any node is no longer responsive to heartbeats from the leader as the result of a failure or a network partition, the node will be marked as inactive and may be replaced by a passive or standby node. Any client sessions that were active on the node will automatically migrate to other nodes in the cluster.

## Leader Failures

In the event of a failure of the leader, the remaining servers in the cluster will begin a new election and a new leader will be elected. This means that for a brief period (seconds) the cluster will be unavailable.

## Network Partitions

In the event of a network partition, if the leader is on a quorum side of the partition, it will continue to operate normally. If the leader is on a non-quorum side of the partition, the leader will detect the partition (based on the fact that it can no longer contact a majority of the cluster), step down, and the servers on a quorum side of the partition (if any) will elect a new leader. Once the partition is resolved, nodes on the non-quorum side of the partition will join the quorum side and receive updates to their log from the remaining leader.

In the event of a multi-way partition (generally rare) where a quorum cannot be achieved on any side of the partition, the cluster will cease to process operations until the partition is resolved in order to prevent inconsistent writes from occurring.

{% include common-links.html %}