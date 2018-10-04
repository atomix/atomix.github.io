---
layout: user-manual
project: atomix
menu: user-manual
title: Docker
---

The [Atomix agent][agent] ships in an official Atomix [Docker][Docker] image available from [Docker Hub][AtomixDocker].

To pull the Atomix Docker image, run `docker pull`:

```
docker pull atomix/atomix:3.0.6
```

Stable releases will be tagged with the stable release version. The `latest` tag is reserved for snapshots.

The image entrypoint is the `atomix-agent` script which ships with the Atomix distribution.

{% include common-links.html %}
