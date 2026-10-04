void synthetic_vector_pointer_loop(u8 *arg0, u8 *arg1, s32 arg2) {
    s128 temp_2;
    s32 var_6;
    u8 *var_4;
    u8 *var_5;

    var_4 = arg0;
    var_5 = arg1;
    var_6 = arg2 - 1;
    if (var_6 >= 0) {
        do {
            temp_2 = *var_5;
            var_5 += 0x10;
            *var_4 = temp_2;
            var_6 -= 1;
            var_4 += 0x10;
        } while (var_6 >= 0);
    }
}
