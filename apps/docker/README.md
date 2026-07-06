# Docker

Full documentation is [on our wiki](https://www.azerothcore.org/wiki/install-with-docker#installation)

## Building

### Prerequisites

Ensure that you have docker, docker compose (v2), and the docker buildx command
installed.

It's all bundled with [Docker Desktop](https://docs.docker.com/get-docker/),
though if you're using Linux you can install them through your distribution's
package manage or by using the [documentation from docker](https://docs.docker.com/engine/install/)

### Building with mod-playerbots

The worldserver, authserver, db-import, and tools images clone
[KodeWorker/mod-playerbots](https://github.com/KodeWorker/mod-playerbots.git)
during the build, so the module doesn't need to be checked out under
`modules/mod-playerbots` on the host. Override the source with the
`DOCKER_PLAYERBOTS_REPO` / `DOCKER_PLAYERBOTS_REF` environment variables
(e.g. in a `.env` file) to build against a different fork or branch.

### Running the Build

1. Build containers with command

```console
$ docker compose build
```

    1. Note that the initial build will take a long time, though subsequent builds should be faster

2. Start containers with command

```console
$ docker compose up -d
# Skip the build step
$ docker compose up -d --build
```

    1. Note that this command may take a while the first time, for the database import

3. (on first install) You'll need to attach to the worldserver and create an Admin account

```console
$ docker compose attach ac-worldserver
AC> account create admin password 3 -1
```
