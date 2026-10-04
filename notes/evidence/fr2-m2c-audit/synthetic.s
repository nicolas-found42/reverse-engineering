.set noat
.set noreorder
glabel synthetic_vector_pointer_loop
synthetic_vector_pointer_loop:
    addiu $6,$6,-1
.Lloopcheck:
    bltz $6,.Lend
    nop
.Lloop:
    lq $2,0($5)
    addiu $5,$5,0x10
    sq $2,0($4)
    addiu $6,$6,-1
    bgez $6,.Lloop
    addiu $4,$4,0x10
.Lend:
    jr $31
    nop
