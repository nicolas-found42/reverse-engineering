OUTPUT_ARCH(mips)
SECTIONS
{
  .text.fr2_misc3d_get_database_id 0x001d1800 : { *(.text.fr2_misc3d_get_database_id) }
  .fr2_file 0x002831a8 : { *(.fr2_file) }
  .fr2_message 0x00283320 : { *(.fr2_message) }
  .sbss.fr2_misc3d_db_id 0x00290ac4 (NOLOAD) : { *(.scommon) *(COMMON) }
}
ASSERT(SIZEOF(.sbss.fr2_misc3d_db_id) == 4, "misc3d cell must occupy four bytes")
