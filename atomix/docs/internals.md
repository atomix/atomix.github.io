---
layout: docs
project: atomix
menu: docs
title: Resource Internals
first-section: internals
---

{:.no-margin-top}
Atomix resources are implemented by multiplexing multiple [Copycat][copycat] [state machines][state-machines] onto a single [Raft] replicated log. 

To learn more about how Copycat works in depth, see the [Copycat architecture][arch-intro] page.

{% include common-links.html %}