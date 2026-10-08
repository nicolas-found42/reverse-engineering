OUTPUT_ARCH(mips)
ENTRY(fixture_entry)
SECTIONS
{
  .text.gnu_fixture 0x00100000 : { *(.text.gnu_fixture) }
  .gnu_fixture_data 0x00108004 : { *(.gnu_fixture_data) }
  .gnu_fixture_bss 0x00108008 (NOLOAD) : { *(.gnu_fixture_bss) }
}
ASSERT(SIZEOF(.text.gnu_fixture) == 20, "GNU fixture text must be five words")
ASSERT(SIZEOF(.gnu_fixture_data) == 4, "GNU fixture data must occupy four bytes")
ASSERT(SIZEOF(.gnu_fixture_bss) == 4, "GNU fixture bss must occupy four bytes")
