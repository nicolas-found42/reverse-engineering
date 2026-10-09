ENTRY(fr2_dma_copy)
SECTIONS {
    .text.fr2_dma_copy 0x0011b780 : { consumer.o(.text.fr2_dma_copy) }
    .text.SignalSema 0x001eab80 : { SignalSema.o(.text) }
    .text.FlushCache 0x001eade0 : { FlushCache.o(.text) }
    .text.sceSifDmaStat 0x001eaf00 : { sceSifDmaStat.o(.text) }
    .text.sceSifSetDma 0x001eaf20 : { sceSifSetDma.o(.text) }
    .text.fr2_mfile_release 0x0020c940 : { consumer.o(.text.fr2_mfile_release) }
    .data.fr2_mfile_sema 0x0024bad8 : { consumer.o(.data.fr2_mfile_sema) }
    .data.fr2_mfile_marker 0x0024f8e0 : { consumer.o(.data.fr2_mfile_marker) }
    .data.fr2_mfile_count 0x0024f8e4 : { consumer.o(.data.fr2_mfile_count) }
    .unassigned 0x00250000 : { *(.text) *(.data) *(.bss) *(COMMON) }
    ASSERT(SIZEOF(.unassigned) == 0, "unexpected executable or data inputs")
    /DISCARD/ : { *(.pdr) *(.mdebug*) *(.comment) *(.reginfo) *(.MIPS.abiflags) *(.eh_frame*) *(.gnu.attributes) }
}
