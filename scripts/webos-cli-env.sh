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
Usage: scripts/webos-cli-env.sh create|install|shell|run <command> [args...]|capture <operation> <alias> <approved-argv...>|remove

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
    distrobox enter "$BOX_NAME" -- bash -c 'umask 077; chmod 700 "$HOME"; if [[ -d "$HOME/.webos" ]]; then chmod -R go-rwx "$HOME/.webos"; fi; if [[ -d "$HOME/.ssh" ]]; then chmod -R go-rwx "$HOME/.ssh"; fi; source "$1" || exit $?; webos_cli_activate_path || exit $?; exec bash --noprofile --norc -i' webos-cli-env /workspace/lg-webos-debloat/scripts/webos-cli-path.sh
    ;;
  run)
    command -v distrobox >/dev/null || { printf 'distrobox is required on the Bazzite host.\n' >&2; exit 2; }
    shift
    (($#)) || { printf 'A command is required: scripts/webos-cli-env.sh run <command> [args...]\n' >&2; exit 2; }
    distrobox enter "$BOX_NAME" -- bash -c 'umask 077; chmod 700 "$HOME"; if [[ -d "$HOME/.webos" ]]; then chmod -R go-rwx "$HOME/.webos"; fi; if [[ -d "$HOME/.ssh" ]]; then chmod -R go-rwx "$HOME/.ssh"; fi; source "$1" || exit $?; webos_cli_activate_path || exit $?; shift; exec "$@"' webos-cli-env /workspace/lg-webos-debloat/scripts/webos-cli-path.sh "$@"
    ;;
  capture)
    (($# == 7)) || { printf 'Capture requires one operation, one alias, and one approved command vector.\n' >&2; exit 2; }
    shift
    operation="$1"
    alias="$2"
    shift 2
    [[ "$alias" =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$ ]] || { printf 'Invalid device alias.\n' >&2; exit 2; }
    case "$operation" in
      metadata) expected=(ares-device --system-info --device "$alias") ;;
      applications) expected=(ares-install --device "$alias" --list) ;;
      applications-full) expected=(ares-install --device "$alias" --listfull) ;;
      *) printf 'Unsupported capture operation.\n' >&2; exit 2 ;;
    esac
    for index in "${!expected[@]}"; do
      [[ "${1:-}" == "${expected[$index]}" ]] || { printf 'Command vector does not match approved operation.\n' >&2; exit 2; }
      shift
    done
    (($# == 0)) || { printf 'Unexpected capture arguments.\n' >&2; exit 2; }
    distrobox enter "$BOX_NAME" -- bash -c 'umask 077; chmod 700 "$HOME"; if [[ -d "$HOME/.webos" ]]; then chmod -R go-rwx "$HOME/.webos"; fi; if [[ -d "$HOME/.ssh" ]]; then chmod -R go-rwx "$HOME/.ssh"; fi; source "$1" || exit $?; webos_cli_activate_path || exit $?; shift; for required_cli in ares-device ares-install; do if [[ ! -x "$HOME/.local/npm/bin/$required_cli" ]]; then printf "Pinned webOS CLI is missing %s.\n" "$required_cli" >&2; exit 2; fi; done; command_name="$1"; shift; exec "$HOME/.local/npm/bin/$command_name" "$@"' webos-cli-capture /workspace/lg-webos-debloat/scripts/webos-cli-path.sh "${expected[@]}"
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
