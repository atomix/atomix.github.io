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

The image entrypoint is the `atomix-agent` script which ships with the Atomix distribution.To run the agent, run the Docker image with agent arguments:

```
docker run atomix/atomix:latest ...
```

It's recommended that the image is run with a custom configuration file. To provide a custom configuration file, mount a configuration file to the container and specify the configuration file path to the Atomix agent:

```
docker run -v /Users/me/atomix/config:/mnt/config atomix/atomix:latest -c /mnt/config/atomix.conf
```

To view additional configuration options, output the agent commands:

```
docker run atomix/atomix:latest --help
```

{% include common-links.html %}
