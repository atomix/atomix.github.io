---
layout: docs
project: copycat
menu: docs
title: Copycat Log
pitch: Raft architecture and implementation
first-section: log-architecture
---

<h2 id="the-copycat-log">7 The Copycat Log</h2>

At the core of the Raft consensus algorithm is the log. As commands are submitted to the cluster, entries representing state changes are written to an ordered log on disk. Logs provide the mechanism through which persistence and consistency is achieved in Raft.

But logs pose particular challenges in managing disk consumption. As commands are written to the logs on each server, entries in the log consume an ever increasing amount of disk space. Eventually, logs on each server will run out of disk space.

Typical implementations of the Raft consensus algorithm use a snapshot-based approach to compacting server logs. But in search of more consistent performance and because of the unique needs of Copycat's session event algorithms, we opted to implement an incremental log compaction algorithm that facilitates a variety of methodologies for managing on-disk state within state machines.

<h3 id="log-structure">7.1 Structure of the Log</h3>

Copycat logs are broken into segments. Each segment of a log is backed by a single file on disk (or block of memory) and represents a sequence of entries in the log. Once a segment becomes full - either determined by its size or the number of entries - the log rolls over to a new segment. Each segment has a 64-byte header that describes the segment's starting index, timestamp, version, and other information relevant to log compaction and recovery.

{: class="text-center"}
{% include lightbox.html href="/assets/img/docs/log_structure.png" desc="Log structure" %}
*This illustration depicts the structure of the log. The log is broken into segments with each segment holding a count- or size-based range of entries. Segmenting the log allows sections of the log to be compacted independently.*

Each entry in the log is written with a 16-bit unsigned length, a 32-bit unsigned `offset`, and an optional 64-bit `term`. Because Raft guarantees that terms in the log are monotonically increasing, the term is written only to the first entry in a segment for a given term, and all later entries inherit the term. When an entry with a new term is appended, that entry is written with the new term and subsequent entries inherit the term.

<h3 id="log-indexes">7.2 Log Indexes</h3>

Copycat reads entries from its log from a dense in-memory index of all entries in each segment. An index is associated with each segment and thus each file on disk, and each entry in the index points to the position of a specific offset in the segment. Offsets are zero-based sequence numbers used to represent the offset of an index relative to the *starting* index within a segment. For instance, if the index of an entry at offset `0` in a segment is `10` then offset `9` is index `20`. Making offsets relative to the starting index of a segment allows Copycat to use more compact 32-bit unsigned integers to represent indexes in the log.

Indexes are built as entries are written to the log. Offsets are written to the index in sorted order, and when the log is truncated, so too are the indexes associated with the relevant segments. When a log is recovered from disk, each segment rebuilds its in-memory index internally by reading the segment and repopulating the index.

Because the index is used to index offsets in the log, and because offsets and log indices are always monotonically increasing, entries will always be appended to the index in sorted order. Additionally, for a leader appending new entries to its log, no offset will ever be skipped in a segment. Thus, index lookups on uncompacted segments are performed in O(1) time by simply reading the relative position for the given offset from the index.

But once a segment has been [compacted](#log-compaction), or if a server is being caught up by a leader whose log has been compacted, some entries may be missing from a segment. Copycat's log compaction algorithm rewrites segments with arbitrary entries removed, and existing entries retain their indexes after a segment is compacted. When a segment is rewritten, the segment's index skips compacted entries rather than indexing them to conserve memory. As such, a binary search algorithm must be used to do index lookups for segments with skipped entries. This is determined simply by tracking whether any offsets have been skipped in the index. We feel binary search is an acceptable trade-off for compacted segments considering the [access patterns of the Raft algorithm](#optimizing-log-indexes). In the majority of cases, servers read and write their logs before they're ever compacted, and only when server is recovering from its log or a leader is catching up a joining server does binary search become a necessity.

<h3 id="optimizing-log-indexes">7.3 Optimizing Indexes for Raft Log Access Patterns</h3>

Copycat's log is optimized to perform well under the most common conditions of the Raft consensus algorithm. Under normal operation, followers append entries to their log and read entries from the head of the log, and leaders tend to read sequentially through the log to send entries to each follower. Log segments can only be compacted once all entries in a segment have been committed, so if all servers are operating primarily on uncommitted entries then servers ultimately only read uncompacted segments. In these cases, constant lookup time for segment index lookups significantly improves performance.

Segment read performance suffers most significantly when a lookup requires binary search to locate an entry. Binary search of a segment's index is necessary once a segment has been compacted and entries have been removed. Fortunately, even in the case of reading a compacted segment, read performance can be significantly improved via the segment index by again taking advantage of Raft's log access patterns. In particular, if a server is reading from a compacted segment of the log it's normally either replaying the log to itself or to another server (if the server is the leader). Because entries always maintain their position and index in the log and offset within a segment even after compaction, iterating entries in compacted segments of the log still only requires a single binary search. Once the starting position of a scan of the log is located, the index stores the position and offset of the last entry read from the index. On subsequent index lookups, the index first checks the next offset in the segment and only performs a binary search if the segment is not being read sequentially.

{% include common-links.html %}
