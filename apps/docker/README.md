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

### Building with mod-ah-bot

The same images also clone
[azerothcore/mod-ah-bot](https://github.com/azerothcore/mod-ah-bot.git)
during the build, so the module doesn't need to be checked out under
`modules/mod-ah-bot` on the host. Override the source with the
`DOCKER_AHBOT_REPO` / `DOCKER_AHBOT_REF` environment variables (e.g. in a
`.env` file) to build against a different fork or branch.

### Building with mod-bg-auto-queue

The same images also clone
[azerothcore/mod-bg-auto-queue](https://github.com/azerothcore/mod-bg-auto-queue.git)
during the build, so the module doesn't need to be checked out under
`modules/mod-bg-auto-queue` on the host. Override the source with the
`DOCKER_BGAUTOQUEUE_REPO` / `DOCKER_BGAUTOQUEUE_REF` environment variables
(e.g. in a `.env` file) to build against a different fork or branch.

### Runtime configuration

A few options are exposed as `docker-compose.yml` environment variables so
they can be set without editing conf files directly (e.g. in a `.env` file):

- `DOCKER_MIN_RANDOM_BOTS` / `DOCKER_MAX_RANDOM_BOTS` (default `500`): sets
  `AiPlayerbot.MinRandomBots` / `AiPlayerbot.MaxRandomBots` on the
  worldserver, overriding whatever is in `playerbots.conf`. AzerothCore maps
  any config key to an `AC_`-prefixed, upper-snake-case env var
  automatically, which is how this works under the hood.
- `DOCKER_REALM_IP` (default `127.0.0.1`): the address clients use to reach
  the world server. Unlike the option above, this isn't a config file value
  -- it's a row in `acore_auth.realmlist` -- so `ac-db-import` updates it
  directly after running the database import.

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
