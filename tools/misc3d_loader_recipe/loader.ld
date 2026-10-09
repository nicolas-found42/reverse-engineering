OUTPUT_ARCH(mips)
SECTIONS
{
 .text.fr2_misc3d_loader_terminal 0x0012c218 : { *(.text.fr2_misc3d_loader_terminal) }
 .text.fr2_misc3d_loader_main 0x001d1408 : { *(.text) }
 /DISCARD/ : { *(.reginfo) *(.mdebug*) *(.comment) }
}
misc3d_db_id = 0x290ac4;
misc3d_state_c8 = 0x290ac8;
misc3d_state_cc = 0x290acc;
misc3d_state_d0 = 0x290ad0;
misc3d_state_d4 = 0x290ad4;
misc3d_source_file = 0x2831a8;
misc3d_database_name = 0x283208;
misc3d_name_optional_first = 0x290318;
misc3d_name_cc = 0x290320;
misc3d_name_c8 = 0x283218;
misc3d_name_d0 = 0x283228;
misc3d_name_d4 = 0x283238;
misc3d_name_required_a = 0x283280;
misc3d_name_required_b = 0x290328;
misc3d_name_optional_last = 0x283310;
misc3d_error_loaded = 0x2831c8;
misc3d_error_d4 = 0x283248;
misc3d_error_required_a = 0x283290;
misc3d_error_required_b = 0x2832d0;
misc3d_load_database = 0x11ed90;
misc3d_find_resource = 0x124f58;
misc3d_resource_object = 0x125068;
misc3d_set_first_object = 0x127728;
misc3d_prepare_object = 0x135748;
misc3d_set_required_a = 0x1e6128;
misc3d_set_required_b = 0x1e6130;
misc3d_finish_resources = 0x12b4c0;
misc3d_loader_error = 0x105888;
misc3d_optional_object = 0x28f23c;
_gp = 0x295d70;
