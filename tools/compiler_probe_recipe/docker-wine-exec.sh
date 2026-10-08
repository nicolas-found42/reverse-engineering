#!/bin/bash
set -eu

runtime_image='sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba'
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
exec docker run --platform linux/amd64 --rm -e WINEDEBUG=-all -v "$host_root:/tools" \
  "$runtime_image" wine "$executable" "${args[@]}"
