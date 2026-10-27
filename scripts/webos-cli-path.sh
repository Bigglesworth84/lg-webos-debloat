#!/usr/bin/env bash
# Source this file and call webos_cli_activate_path in the CLI Distrobox.

webos_cli_activate_path() {
  local node_bin="$HOME/.local/opt/node-v24.22.1/bin"
  local npm_bin="$HOME/.local/npm/bin"
  local required

  for required in "$node_bin/node" "$npm_bin/ares" "$npm_bin/ares-setup-device"; do
    if [[ ! -x "$required" ]]; then
      printf 'Pinned webOS CLI environment is incomplete: missing executable %s. Run scripts/webos-cli-env.sh install.\n' "$required" >&2
      return 2
    fi
  done

  local -a entries=("$npm_bin" "$node_bin")
  local -a current_entries=()
  local -a unique_entries=()
  local entry
  local existing
  local found
  local next_path=""
  IFS=: read -r -a current_entries <<< "${PATH:-}"

  for entry in "${entries[@]}" "${current_entries[@]}"; do
    [[ -n "$entry" ]] || continue
    found=0
    for existing in "${unique_entries[@]}"; do
      if [[ "$entry" == "$existing" ]]; then
        found=1
        break
      fi
    done
    ((found)) && continue
    unique_entries+=("$entry")
    if [[ -n "$next_path" ]]; then
      next_path+=":"
    fi
    next_path+="$entry"
  done

  export PATH="$next_path"
}
