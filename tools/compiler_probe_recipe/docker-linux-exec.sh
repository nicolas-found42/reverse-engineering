#!/bin/bash
set -eu

runtime_image='sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca'
host_root=$1
shift
executable=$1
shift
case "$executable" in
  "$host_root"/*) executable="/tools/${executable#"$host_root"/}" ;;
  mips-linux-gnu-*) executable="/tools/$executable" ;;
  *) echo "unrecognized compiler probe executable: $executable" >&2; exit 2 ;;
esac
args=()
for arg in "$@"; do
  case "$arg" in
    *"$host_root"*) arg=${arg//"$host_root"/\/tools} ;;
  esac
  args+=("$arg")
done
# Relative compiler inputs retain a stable basename in GCC's object metadata.
# Map a caller's cwd only when it is inside the one mounted tool root.
workdir=/
case "$PWD" in
  "$host_root") workdir=/tools ;;
  "$host_root"/*) workdir="/tools/${PWD#"$host_root"/}" ;;
esac
exec docker run --platform linux/amd64 --rm --workdir "$workdir" -v "$host_root:/tools" "$runtime_image" "$executable" "${args[@]}"
