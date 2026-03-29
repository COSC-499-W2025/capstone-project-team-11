#!/bin/sh
set -eu

NODE_MODULES_DIR="/app/frontend/node_modules"
SEEDED_NODE_MODULES_DIR="/opt/frontend-node-modules"

if [ ! -d "$NODE_MODULES_DIR" ] || [ -z "$(ls -A "$NODE_MODULES_DIR" 2>/dev/null)" ]; then
  mkdir -p "$NODE_MODULES_DIR"
  cp -a "$SEEDED_NODE_MODULES_DIR"/. "$NODE_MODULES_DIR"/
fi

exec npm start
