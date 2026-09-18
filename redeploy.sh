#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_HOST="duvendir@192.168.1.105"
CONTROL_PATH="$HOME/.ssh/controlmasters/%r@%h:%p"

mkdir -p "$HOME/.ssh/controlmasters"
ssh -MNf -o ControlMaster=auto -o ControlPersist=600 -o ControlPath="$CONTROL_PATH" "$REMOTE_HOST"

cleanup() {
    ssh -O exit -o ControlPath="$CONTROL_PATH" "$REMOTE_HOST" 2>/dev/null || true
}
trap cleanup EXIT

bash "$SCRIPT_DIR/deploy.sh"
