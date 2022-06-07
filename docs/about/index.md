<!--
SPDX-FileCopyrightText: 2022-present Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->

# About

Atomix was established in 2013 by [Jordan Halterman](https://github.com/kuujo) as a passion project. Originally 
built on one of the first implementations of the [Raft consensus algorithm](https://raft.github.io/), Atomix soon
found traction and was adopted by the [Open Networking Foundation (ONF)](https://opennetworking.org) where it matured and
evolved into a high-level  framework to enable network application developers to build scalable, fault-tolerant distributed
systems. Atomix primitives were used to manage state, coordinate cluster membership, and provide fault-tolerance for the
[ONOS](https://onosproject.org), a distributed software-defined network controller. In 2020, ONOS began to migrate to a
cloud native architecture, and Atomix followed suit. It was completely rewritten in Go and utilizing cloud native
tools like gRPC, Kubernetes, and Docker. Today, Atomix continues to be actively maintained and developed in support of
various ONF projects.
