#!/usr/bin/env bash
# Download a MOSS-Image bundle from ModelScope into models/<name>, resuming and
# retrying each file until its size and sha256 match the listing.
# Usage: scripts/fetch-modelscope.sh MOSS-Image-SFT|MOSS-Image-Base [skip-regex]
set -euo pipefail

name=${1:-MOSS-Image-SFT}
case "$name" in
  MOSS-Image-SFT|MOSS-Image-Base) ;;
  *) echo "Usage: $0 [MOSS-Image-SFT|MOSS-Image-Base] [skip-regex]" >&2; exit 2 ;;
esac
skip=${2:-'^$'}
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export DEST="$repo_dir/models/$name"
export BASE_URL="https://modelscope.cn/models/openmoss/$name/resolve/master"

fetch() {
  local path=$1 size=$2 sha=$3 out="$DEST/$1" part="$DEST/$1.part" attempt
  if [[ -f $out && $(stat -f%z "$out") == "$size" ]]; then
    [[ -z $sha || $(shasum -a 256 "$out" | cut -d' ' -f1) == "$sha" ]] && return 0
  fi
  mkdir -p "$(dirname "$out")"
  for attempt in $(seq 1 100); do
    if [[ ! -f $part || $(stat -f%z "$part") -lt $size ]]; then
      curl --noproxy '*' -sSL -C - --connect-timeout 20 --speed-limit 20000 --speed-time 60 \
        -o "$part" "$BASE_URL/$path" || { sleep 5; continue; }
    fi
    [[ $(stat -f%z "$part") == "$size" ]] || { sleep 5; continue; }
    if [[ -z $sha || $(shasum -a 256 "$part" | cut -d' ' -f1) == "$sha" ]]; then
      mv "$part" "$out"
      echo "ok $path"
      return 0
    fi
    echo "sha256 mismatch, restarting $path"
    rm -f "$part"
  done
  echo "FAILED $path"
  return 1
}
export -f fetch

curl --noproxy '*' -fsS --retry 10 --retry-all-errors \
  "https://modelscope.cn/api/v1/models/openmoss/$name/repo/files?Recursive=true" |
  python3 -c 'import json, sys
for f in json.load(sys.stdin)["Data"]["Files"]:
    if f["Type"] == "blob":
        print(f["Path"], f["Size"], f.get("Sha256") or "")' |
  grep -Ev "$skip" |
  sort -k2 -n |
  xargs -P 4 -L 1 bash -c 'fetch "$@"' _
