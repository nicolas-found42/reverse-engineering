# Authored public R5900/EABI fixture; contains no game code.
.set noreorder
.section .text.gnu_fixture,"ax",@progbits
.globl fixture_entry
fixture_entry:
    lui $8, %hi(fixture_data)
    addiu $8, $8, %lo(fixture_data)
    paddw $2, $4, $5
    jr $31
    nop
.section .gnu_fixture_data,"aw",@progbits
.align 2
fixture_data:
    .word 0x11223344
.section .gnu_fixture_bss,"aw",@nobits
.align 2
    .space 4
