OUTPUT_ARCH(mips)
SECTIONS
{
  .text.probe 0x001d1800 : { *(.text.probe) }
  .fr2_file 0x002831a8 : { *(.fr2_file) }
  .fr2_message 0x00283320 : { *(.fr2_message) }
}
