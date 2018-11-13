---
layout: user-manual
project: atomix
menu: user-manual
title: Starting the Agent
---

The Atomix agent is a standalone Atomix server node, often used in client-server architectures.

## Installation

To run the agent, first download the Atomix distribution, which can be found on the [downloads] page:

```
curl -o atomix-dist-3.0.7.tar.gz -XGET https://oss.sonatype.org/content/repositories/releases/io/atomix/atomix-dist/3.0.7/atomix-dist-3.0.7.tar.gz
```

Once the distribution has been downloaded, unpack the distribution into the desired directory:

```
tar -xvf atomix-dist-3.0.7.tar.gz
```

The Atomix distribution is laid out as follows:

* `/bin` - scripts for running Atomix
* `/conf` - default configuration files with documentation
* `/examples` - example configuration files
* `/lib` - core dependencies and extensions
* `/log` - Atomix system logs

The default configuration for the agent can be found at `/conf/atomix.conf`. To run the Atomix agent, modify `atomix.conf` and use the `atomix-agent` script to run the agent:

```
./bin/atomix-agent
```

{:.callout .callout-warning}
`atomix.conf` must be setup before running the agent.

## Configuration

The agent instance can be configured by modifying `atomix.conf`. For available configuration options, see the [configuration reference][reference].

Additionally, the agent supports various command line arguments to allow limited overrides of configuration options:

* `--member` `-m` - The local member identifier
* `--address` `-a` - The local member address
* `--host` - The local host identifier, used for host-aware partitioning schemes
* `--rack` - The local rack identifier, used for rack-aware partitioning schemes
* `--zone` - The local zone identifier, used for zone-aware partitioning schemes
* `--config` `-c` - A list of user-provided configuration files in either JSON or HOCON format
* `--log-config` - A user-provided `logback.xml` logging configuration
* `--log-dir` - The directory to which to write system logs; not applicable of `--log-config` is specified
* `--log-level` - The highest log level for all logs
* `--file-log-level` - The log level filter for file logs
* `--console-log-level` - The log level filter for console logs
* `--data-dir` - The directory to which to write system state, e.g. Raft logs and snapshots
* `--bootstrap` - A list of bootstrap nodes to configure a `bootstrap` node discovery provider
* `--multicast` - Enables multicast for the instance
* `--multicast-group` - The group to use for multicast
* `--multicast-port` - The port to use for multicast
* `--http-host` - The HTTP host to which to bind. Defaults to `0.0.0.0`
* `--http-port` - The HTTP port to which to bind. Defaults to `5678`

{% include common-links.html %}
