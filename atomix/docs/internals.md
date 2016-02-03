---
layout: docs
project: atomix
menu: docs
title: Resource internals
pitch: How resources are implemented
first-section: internals
---

Resources are implemented by multiplexing multiple Copycat [state machines][state-machines] onto a single Raft replicated log.

{% include common-links.html %}