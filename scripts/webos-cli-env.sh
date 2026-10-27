#!/usr/bin/env bash
set -euo pipefail

BOX_NAME="webos-cli-m003"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
CLI_HOME="${WEBOS_CLI_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/lg-webos-cli-home}"
if ! command -v distrobox >/dev/null && [[ -x "$HOME/.local/bin/distrobox" ]]; then
  PATH="$HOME/.local/bin:$PATH"
  export PATH
fi

[[ "$CLI_HOME" = /* ]] || { printf 'WEBOS_CLI_HOME must be an absolute path.\n' >&2; exit 2; }
CLI_HOME="$(realpath -m "$CLI_HOME")"
case "$CLI_HOME/" in
  "$PROJECT_ROOT/"*) printf 'WEBOS_CLI_HOME must be outside the repository.\n' >&2; exit 2 ;;
esac

usage() {
  cat <<'EOF'
Usage: scripts/webos-cli-env.sh create|install|shell|run <command> [args...]|remove

Creates a rootless Ubuntu Distrobox with a custom private HOME. The repository
is mounted read-only. The container remains integrated with the host and is
not a security boundary.
EOF
}

action="${1:-}"
case "$action" in
  create)
    command -v distrobox >/dev/null || { printf 'distrobox is required on the Bazzite host.\n' >&2; exit 2; }
    mkdir -p "$CLI_HOME"
    chmod 700 "$CLI_HOME"
    distrobox create --name "$BOX_NAME" --image docker.io/library/ubuntu:24.04 \
      --home "$CLI_HOME" --volume "$PROJECT_ROOT:/workspace/lg-webos-debloat:ro"
    ;;
  install)
    command -v distrobox >/dev/null || { printf 'distrobox is required on the Bazzite host.\n' >&2; exit 2; }
    distrobox enter "$BOX_NAME" -- bash /workspace/lg-webos-debloat/scripts/install_webos_cli.sh
    ;;
  shell)
    command -v distrobox >/dev/null || { printf 'distrobox is required on the Bazzite host.\n' >&2; exit 2; }
    distrobox enter "$BOX_NAME" -- bash -c 'umask 077; chmod 700 "$HOME"; if [[ -d "$HOME/.webos" ]]; then chmod -R go-rwx "$HOME/.webos"; fi; if [[ -d "$HOME/.ssh" ]]; then chmod -R go-rwx "$HOME/.ssh"; fi; source /workspace/lg-webos-debloat/scripts/webos-cli-path.sh; webos_cli_activate_path; exec bash --noprofile --norc -i'
    ;;
  run)
    command -v distrobox >/dev/null || { printf 'distrobox is required on the Bazzite host.\n' >&2; exit 2; }
    shift
    (($#)) || { printf 'A command is required: scripts/webos-cli-env.sh run <command> [args...]\n' >&2; exit 2; }
    distrobox enter "$BOX_NAME" -- bash -c 'umask 077; chmod 700 "$HOME"; if [[ -d "$HOME/.webos" ]]; then chmod -R go-rwx "$HOME/.webos"; fi; if [[ -d "$HOME/.ssh" ]]; then chmod -R go-rwx "$HOME/.ssh"; fi; source /workspace/lg-webos-debloat/scripts/webos-cli-path.sh; webos_cli_activate_path; exec "$@"' webos-cli-env "$@"
    ;;
  remove)
    command -v distrobox >/dev/null || { printf 'distrobox is required on the Bazzite host.\n' >&2; exit 2; }
    distrobox stop "$BOX_NAME" 2>/dev/null || true
    distrobox rm --force "$BOX_NAME"
    printf 'Container removed. Private home retained at %s; delete it separately after reviewing its contents.\n' "$CLI_HOME"
    ;;
  -h|--help|"") usage; [[ "$action" != "" ]] && exit 2 || exit 0 ;;
  *) usage >&2; exit 2 ;;
esac
