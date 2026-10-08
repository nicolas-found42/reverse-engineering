OUTPUT_ARCH(mips)
SECTIONS
{
  .text.fr2_misc3d_get_database_id 0x001d1800 : { *(.text.fr2_misc3d_get_database_id) }
  .fr2_file 0x002831a8 : { *(.fr2_file) }
  .fr2_message 0x00283320 : { *(.fr2_message) }
}
