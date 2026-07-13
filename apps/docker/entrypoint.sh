#!/usr/bin/env bash
set -euo pipefail

CONF_DIR="${CONF_DIR:-/azerothcore/env/dist/etc}"
LOGS_DIR="${LOGS_DIR:-/azerothcore/env/dist/logs}"

if ! touch "$CONF_DIR/.write-test" || ! touch "$LOGS_DIR/.write-test"; then
    cat <<EOF
===== WARNING =====
The current user doesn't have write permissions for
the configuration dir ($CONF_DIR) or logs dir ($LOGS_DIR).
It's likely that services will fail due to this.

This is usually caused by cloning the repository as root,
so the files are owned by root (uid 0).

To resolve this, you can set the ownership of the
configuration directory with the command on the host machine.
Note that if the files are owned as root, the ownership must
be changed as root (hence sudo).

$ sudo chown -R $(id -u):$(id -g) /path/to$CONF_DIR /path/to$LOGS_DIR

Alternatively, you can set the DOCKER_USER environment
variable (on the host machine) to "root", though this
isn't recommended.

$ DOCKER_USER=root docker-compose up -d
====================
EOF
fi

[[ -f "$CONF_DIR/.write-test" ]] && rm -f "$CONF_DIR/.write-test"
[[ -f "$LOGS_DIR/.write-test" ]] && rm -f "$LOGS_DIR/.write-test"

# Copy all default config files to env/dist/etc if they don't already exist
# -r == recursive
# -n == no clobber (don't overwrite)
# -v == be verbose
cp -rnv /azerothcore/env/ref/etc/* "$CONF_DIR"

CONF="$CONF_DIR/$ACORE_COMPONENT.conf"
CONF_DIST="$CONF_DIR/$ACORE_COMPONENT.conf.dist"

# Copy the "dist" file to the "conf" if the conf doesn't already exist
if [[ -f "$CONF_DIST" ]]; then
    cp -vn "$CONF_DIST" "$CONF"
else
    touch "$CONF"
fi

# Same for module configs (env/dist/etc/modules/*.conf.dist -> *.conf) --
# ConfigMgr::LoadModulesConfigs() looks for the non-".dist" filename, so
# without this every AiPlayerbot.*/etc. option silently falls back to its
# C++ default instead of what's in playerbots.conf.dist.
for MODULE_CONF_DIST in "$CONF_DIR/modules/"*.conf.dist; do
    [[ -f "$MODULE_CONF_DIST" ]] || continue
    cp -vn "$MODULE_CONF_DIST" "${MODULE_CONF_DIST%.dist}"
done

echo "Starting $ACORE_COMPONENT..."

# The realmlist address isn't a config file value -- it's a row in the
# acore_auth DB -- so it can't be overridden via an AC_* env var like other
# options. If REALM_IP is set, run db-import to completion and then point
# the realm at it, instead of exec'ing straight into dbimport.
if [[ "$ACORE_COMPONENT" == "dbimport" && -n "${REALM_IP:-}" ]]; then
    "$@"

    IFS=';' read -r DB_HOST DB_PORT DB_USER DB_PASS DB_NAME <<< "$AC_LOGIN_DATABASE_INFO"
    echo "Setting realmlist address to $REALM_IP"
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" \
        -e "UPDATE realmlist SET address = '$REALM_IP' WHERE id = 1;"

    exit 0
fi

exec "$@"
