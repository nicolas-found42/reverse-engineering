OUTPUT_ARCH(mips)
SECTIONS
{
 .text.fr2_misc3d_reset 0x001d17a8 : { *(.text.fr2_misc3d_reset) }
 .text.fr2_misc3d_release 0x001d17c8 : { *(.text.fr2_misc3d_release) }
 .text.fr2_misc3d_get_database_id 0x001d1800 : { *(.text.fr2_misc3d_get_database_id) }
 .text.fr2_misc3d_get_state_cc 0x001d1840 : { *(.text.fr2_misc3d_get_state_cc) }
 .text.fr2_misc3d_get_state_d4 0x001d1880 : { *(.text.fr2_misc3d_get_state_d4) }
 .text.fr2_misc3d_get_state_d0 0x001d18c0 : { *(.text.fr2_misc3d_get_state_d0) }
 .fr2_file 0x002831a8 : { *(.fr2_file) }
 .fr2_message 0x00283320 : { *(.fr2_message) }
 .fr2_lifecycle_message 0x00283358 : { *(.fr2_lifecycle_message) }
 .sbss.fr2_misc3d_db_id 0x00290ac4 (NOLOAD) : { *db_id-prepared.o(.scommon) *db_id-prepared.o(COMMON) }
 .sbss.fr2_misc3d_state_c8 0x00290ac8 (NOLOAD) : { *state_c8-prepared.o(.scommon) *state_c8-prepared.o(COMMON) }
 .sbss.fr2_misc3d_state_cc 0x00290acc (NOLOAD) : { *state_cc-prepared.o(.scommon) *state_cc-prepared.o(COMMON) }
 .sbss.fr2_misc3d_state_d0 0x00290ad0 (NOLOAD) : { *state_d0-prepared.o(.scommon) *state_d0-prepared.o(COMMON) }
 .sbss.fr2_misc3d_state_d4 0x00290ad4 (NOLOAD) : { *state_d4-prepared.o(.scommon) *state_d4-prepared.o(COMMON) }
}
ASSERT(SIZEOF(.sbss.fr2_misc3d_db_id) == 4, "db_id cell must occupy four bytes")
ASSERT(SIZEOF(.sbss.fr2_misc3d_state_c8) == 4, "state_c8 cell must occupy four bytes")
ASSERT(SIZEOF(.sbss.fr2_misc3d_state_cc) == 4, "state_cc cell must occupy four bytes")
ASSERT(SIZEOF(.sbss.fr2_misc3d_state_d0) == 4, "state_d0 cell must occupy four bytes")
ASSERT(SIZEOF(.sbss.fr2_misc3d_state_d4) == 4, "state_d4 cell must occupy four bytes")
