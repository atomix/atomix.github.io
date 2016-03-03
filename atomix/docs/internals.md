---
layout: docs
project: atomix
menu: docs
title: Resource Internals
first-section: internals
---

{:.no-margin-top}
Resources are implemented by multiplexing multiple Copycat [state machines][state-machines] onto a single Raft replicated log. See the [Copycat internals][copycat-internals] page for more details.

{% include common-links.html %}