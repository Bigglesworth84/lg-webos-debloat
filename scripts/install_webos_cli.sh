#!/usr/bin/env bash
set -euo pipefail
umask 077

NODE_VERSION="24.22.1"
CLI_VERSION="3.2.6"
NODE_ROOT="$HOME/.local/opt/node-v${NODE_VERSION}"
NPM_PREFIX="$HOME/.local/npm"
ARCHIVE="node-v${NODE_VERSION}-linux-x64.tar.xz"
case "$(uname -m)" in
  x86_64) ARCHIVE="node-v${NODE_VERSION}-linux-x64.tar.xz" ;;
  aarch64|arm64) ARCHIVE="node-v${NODE_VERSION}-linux-arm64.tar.xz" ;;
  *) printf 'Unsupported architecture: %s\n' "$(uname -m)" >&2; exit 2 ;;
esac

missing=()
for command in curl tar sha256sum grep awk xz; do
  command -v "$command" >/dev/null || missing+=("$command")
done
if ((${#missing[@]})); then
  command -v sudo >/dev/null || { printf 'Missing required container tools: %s\n' "${missing[*]}" >&2; exit 2; }
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl tar xz-utils coreutils grep gawk
fi

mkdir -p "$HOME/.local/opt" "$HOME/.local/npm" "$HOME/.ssh"
chmod 700 "$HOME" "$HOME/.local" "$HOME/.local/opt" "$HOME/.local/npm" "$HOME/.ssh"
if [[ ! -x "$NODE_ROOT/bin/node" ]]; then
  temp_dir="$(mktemp -d)"
  trap 'rm -rf "$temp_dir"' EXIT
  curl --fail --location --silent --show-error "https://nodejs.org/dist/v${NODE_VERSION}/${ARCHIVE}" -o "$temp_dir/$ARCHIVE"
  curl --fail --location --silent --show-error "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt" -o "$temp_dir/SHASUMS256.txt"
  expected="$(awk -v file="$ARCHIVE" '$2 == file { print $1 }' "$temp_dir/SHASUMS256.txt")"
  [[ "$expected" =~ ^[a-fA-F0-9]{64}$ ]] || { printf 'Missing official checksum for %s\n' "$ARCHIVE" >&2; exit 2; }
  printf '%s  %s\n' "$expected" "$temp_dir/$ARCHIVE" | sha256sum --check --status
  mkdir -m 700 "$NODE_ROOT"
  tar -xJf "$temp_dir/$ARCHIVE" --strip-components=1 -C "$NODE_ROOT"
  chmod -R go-rwx "$NODE_ROOT"
  rm -rf "$temp_dir"
  trap - EXIT
fi

export PATH="$NPM_PREFIX/bin:$NODE_ROOT/bin:$PATH"
export npm_config_prefix="$NPM_PREFIX"
"$NODE_ROOT/bin/npm" install --global --no-audit --no-fund \
  --allow-scripts=@webos-tools/cli,ssh2 "@webos-tools/cli@${CLI_VERSION}"
CLI_PACKAGE="$NPM_PREFIX/lib/node_modules/@webos-tools/cli"
if [[ -d "$CLI_PACKAGE" ]]; then
  chmod -R go-w "$CLI_PACKAGE"
fi
mkdir -p "$HOME/.webos/tv"
chmod 700 "$HOME/.webos" "$HOME/.webos/tv" "$HOME/.ssh"
if [[ -f "$HOME/.webos/tv/novacom-devices.json" ]]; then
  chmod 600 "$HOME/.webos/tv/novacom-devices.json"
fi
printf 'Node: '; node --version
printf 'npm: '; npm --version
printf 'webOS CLI: '; ares --version
printf 'CLI home: %s\n' "$HOME/.webos/tv"
printf 'Key directory: %s\n' "$HOME/.ssh"
