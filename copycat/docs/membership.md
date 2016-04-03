---
layout: docs
project: copycat
menu: docs
title: Cluster Membership
pitch: Raft architecture and implementation
first-section: membership
---

<h2 id="membership-changes">6 Membership Changes</h2>

The Raft consensus algorithm is designed explicitly with the goal of supporting cluster membership changes without downtime. However, because of the restrictions on commitment of state changes to a Raft cluster, configuration changes are nevertheless an expensive operation. When new servers join the cluster, their logs must be caught up to the leader before they can begin actively participating in the commitment of entries to the Raft log. This implicit overhead in replacing voting Raft members makes systems that dynamically replace failed Raft servers impractical. Nevertheless, we sought an approach that could quickly replace failed voting members. This section proposes an algorithm wherein Raft voting members can be quickly replaced by maintaining standby servers.

Membership changes in Raft are typically implemented via one of the two means described in the Raft literature. The original Raft paper proposed a two-step process wherein a combination of the old and new configuration was committed to the Raft log as an intermediate step. This so called joint consensus approach allowed for arbitrary configuration changes while preventing two majorities from forming during the configuration change. However, this approach was later replaced by a simpler single-server configuration change process. The single server configuration change approach allows only individual servers to be added to or removed from the cluster at any given time. This significantly simplifies the configuration change process as it does not require multiple stages.

But even with the advancements in configuration change processes in the Raft consensus algorithm, some challenges still remain in implementing configuration changes in practical systems. If not done carefully, the rapid addition of servers to a configuration can result in effective downtime for the cluster. For example, if three servers are added to a two node cluster, the cluster will essentially be blocked until at least one of the new servers catches up with the leader. Thus, practical systems must still implement multi-stage configuration change processes wherein new servers join in a non-voting state and are later promoted to full voting members once they've caught up to the leader.

The time it takes for a new server to join the cluster and catch up to the leader makes dynamically replacing failed servers impractical. Thus, we propose reducing the latency of catching up new servers by maintaining a hierarchical network of servers wherein standby servers are always available to become active voting members. The network contains three different types of servers — active, passive, and reserve members — each of which play some role in supporting rapid replacement of failed servers.

<h3 id="active-members">6.1 Active Members</h3>

Active members are full voting members which participate in all aspects of the Raft consensus algorithm. Active servers are always in one of the Raft states — follower, candidate, or leader — at any given time.

<h3 id="passive-members">6.2 Passive Members</h3>

When a new server is added to a Raft cluster, the server typically must be caught up to within some bound of the leader before it can become a full voting member of the cluster. Adding a new server without first warming up its log will result in some period of decreased availability. Still, even in implementations that avoid availability problems by catching up servers before they join, the process of catching up a new server is not insignificant. The leader must send its entire log to the joining server, and for systems that take snapshots, the snapshot must be installed on the new server as well. Thus, there is significant overhead in terms of time and load to dynamically replacing a failed server.

However, systems can maintain servers that are virtually kept in sync with the rest of the cluster at all times. We call these servers passive servers. The concept of passive servers essentially builds on the approach for catching up new servers as has previously been described in Raft literature. Passive servers are essentially kept in sync with the voting members of the cluster in order to facilitate fast replacement of voting members. When a voting member is partitioned, a passive member can be immediately promoted to active and the unavailable voting member will be removed.

Passive servers can also be useful in other contexts. For instance, our implementation optionally allows reads to be executed on passive servers with relaxed consistency requirements. Systems can still maintain sequential consistency on passive servers with the same mechanisms as those used for [querying followers](#processing-queries-on-followers).

<h3 id="reserve-members">6.3 Reserve Members</h3>

Thus far, we've described active voting members and the process of replacing them with passive members. This provides a mechanism for rapidly recovering the full cluster of voting members so long as a majority of the voting members is not lost at the same time. For large clusters, though, the overhead of maintaining passive servers can by itself become a drain on the cluster's resources. Each additional passive server imposes the overhead of replicating all committed log entries, and this is significant even if done by followers. Thus, to ease the load on large clusters, we introduce the reserve member type.

Reserve members serve as standbys to passive members. When an active server fails and a passive server is promoted, the leader can simultaneously promote a reserve server to passive. This ensures that as the cluster evolves and the pool of passive servers shrinks, new servers can take their place.

Reserve servers do not maintain state machines and need not known about committed entries. However, because reserve servers can be promoted to passive, they do need to have some mechanism for learning about configuration changes.

<h3 id="passive-replication">6.4 Passive Replication</h3>

The process of replicating to passive servers parallels that of the process of catching up new servers during configuration changes. However, the implication of catching up new servers is that practically speaking it doesn't place any additional load on the cluster. Once the server is caught up, it will become a full voting member so will continue to receive *AppendEntries* RPCs from the leader at normal intervals anyways. Thus, it makes sense for the leader to  include new servers in *AppendEntries* RPCs. Conversely, passive servers persist for significantly longer than the time it takes to catch up a new server and the replication of entries to passive servers represents additional load on the cluster. Additionally, little is gained from the leader replicating entries to passive servers directly. Thus, we propose moving responsibility for replicating entries to passive servers from the leader to followers.

Each follower is responsible for sending *AppendEntries* RPCs to a subset of passive servers at regular intervals. The algorithm for sending *AppendEntries* RPCs from followers to passive members is identical to that of the standard process for sending *AppendEntries* RPCs aside from a few relevant factors:

* Each follower sends *AppendEntries* RPCs only to a subset of passive servers
* Followers send only committed entries to passive servers

In order to spread the load across the cluster and prevent conflicts in passive replication, each follower is responsible for replicating entries to a subset of the available passive members. This seems to imply that followers must have some sense of the availability of both active and passive servers in the cluster so that they can determine the relationship between followers and passive members. However, because the algorithm is designed to promote passive servers when an active server is unavailable, followers need not have any mechanism for determining the state of active members.

<h3 id="promoting-passive-members">6.5 Promoting Passive Members</h3>

Any server can promote any other server. Passive servers are promoted by simply committing a single-server configuration change adding the passive server to the quorum. As with all configuration changes, the updated configuration is applied on each server as soon as it's written to the log to prevent so-called "split brain."

Because passive servers receive configuration changes as part of normal replication of entries via *AppendEntries* RPCs, passive servers that are promoted in a given configuration must be able to continue receiving entries. However, the failure of a follower can result in the halting of *AppendEntries* RPCs to a passive server. If that passive server is then promoted, it will never receive the configuration change and thus will never actually transition to the active member state. For this reason, leaders must take over responsibilities for sending *AppendEntries* RPCs to any server promoted from passive to active immediately after the configuration change is written to the leader's log. Indeed, this is the expected behavior as configuration changes are immediately applied when written to the log. However, note that if the follower responsible for sending *AppendEntries* RPCs to the promoted server for cold is alive, for some period of time both the leader and the follower will send *AppendEntries* RPCs to the server being promoted. This, however, should not pose safety issues as the *AppendEntries* protocol ensures entries will not be duplicated in the promoted server's logs.

<h3 id="demoting-active-members">6.6 Demoting Active Members</h3>

The ultimate goal of the dynamic configuration change process is to replace an unavailable voting member with an available voting member. However, in order to ensure a further loss of availability is not incurred, it's critical that the failed active server not be demoted until it has been fully replaced by the promotion of a passive server. This ensures that the quorum size is not decreased in the event of a failure to commit the initial configuration change promoting the passive server. Once the promotion of the passive server has been committed, the unavailable active server can be demoted from the quorum.

<h3 id="determining-availability">6.7 Determining Availability</h3>

The dynamic membership change algorithm as described thus far replaces unreachable active members with arbitrary passive members and passive members with reserve members. However, this algorithm does not account for cases where passive or reserve servers are themselves reachable. Thus, some extension needs to be made to provide a consistent view of the availability of each server in the cluster.

The basic Raft consensus algorithm provides leaders a clear view of all followers. Leaders are responsible for sending periodic *AppendEntries* RPCs to followers at regular intervals, and the responses, or lack thereof, to *AppendEntries* RPCs can be used to deduce the availability of followers. Leaders can use the availability of followers to determine when to promote a passive server to active and remove an unavailable follower. However, the passive member may itself be unavailable. Without accounting for availability, this can result in an infinite loop of promotion and demotion wherein two unavailable servers continuously replace one another as active servers.

In order to facilitate promoting available members and demoting unavailable members, we introduce modifications to the *AppendEntries* requests that leaders send to followers to additionally track availability. The leader periodically sends empty heartbeats to all servers - including passive and reserve servers - to determine their availability. If a server fails to respond to an empty `AppendRequest` for several rounds of heartbeats, the leader commits a configuration change setting the member's status to `UNAVAILABLE`. The leader continues to send empty `AppendRequest`s to unavailable members to attempt to determine when they become reachable again. Once an unavailable member responds successfully to an empty `AppendRequest`, the leader commits another configuration change to update that member's status to `AVAILABLE` again.

As is the case with [session expiration](#session-expiration), no-op entries committed at the beginning of a new leader's term effectively reset the timeout for all members. This ensures that members do not appear unavailable due to leadership changes.

{% include common-links.html %}
