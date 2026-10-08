#!/bin/bash
set -eu

fetch_locked() {
	local url="$1" destination="$2" commit="$3"
	if [ -d "$destination/.git" ]; then
		actual=$(git -C "$destination" rev-parse HEAD)
		if [ "$actual" != "$commit" ]; then
			echo "locked dependency drift: $destination is $actual, expected $commit" >&2
			exit 1
		fi
		if ! git -C "$destination" diff --quiet \
			|| ! git -C "$destination" diff --cached --quiet; then
			echo "locked dependency has tracked changes: $destination" >&2
			exit 1
		fi
		return
	fi
	git clone --no-checkout "$url" "$destination"
	git -C "$destination" checkout --detach "$commit"
}

fetch_locked https://github.com/lwip-tcpip/lwip.git \
	common/external_deps/lwip 77dcd25a72509eb83f72b033d219b1d40cd8eb95
fetch_locked https://github.com/fjtrujy/FatFs.git \
	common/external_deps/fatfs 18cc3d9e07473a6aa3d783a66224b243a7b4974c
