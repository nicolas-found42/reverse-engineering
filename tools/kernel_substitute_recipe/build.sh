#!/bin/sh
set -eu
tar -xzf /toolchain/ps2dev-ubuntu-24.04-arm.tar.gz -C /opt
tool=/opt/ps2dev/ee/bin/mips64r5900el-ps2-elf
cd /out
"$tool-gcc" --version > compiler-version.txt
"$tool-gcc" -std=c11 -D_EE -O2 -G0 -mabi=n32 -fno-pic -mno-abicalls \
    -ffreestanding -fno-builtin -fno-asynchronous-unwind-tables \
    -Wall -Wextra -Werror -Isdk/common/include -Isdk/ee/kernel/include \
    -c sdk_consumers.c -o consumer.o
for name in SignalSema FlushCache sceSifDmaStat sceSifSetDma; do
    "$tool-gcc" -G0 -mabi=n32 -fno-pic -mno-abicalls \
        -Isdk/ee/kernel/include -DF_"$name" \
        -c sdk/ee/kernel/src/kernel.S -o "$name.o"
done
"$tool-ld" -T consumer.ld --no-undefined --orphan-handling=error \
    -Map=consumer.map -o consumer.elf \
    consumer.o SignalSema.o FlushCache.o sceSifDmaStat.o sceSifSetDma.o
"$tool-objdump" -dr consumer.elf > linked-disassembly.txt
"$tool-nm" -u consumer.elf > undefined.txt
sha256sum "$tool-gcc" "$tool-as" "$tool-ld" > tools.sha256
dpkg-query -W libmpc3 libmpfr6 libgmp10 > runtime-packages.txt
mkdir runtime-notices
for name in libmpc3 libmpfr6 libgmp10; do
    cp /usr/share/doc/"$name"/copyright runtime-notices/"$name".copyright
done
