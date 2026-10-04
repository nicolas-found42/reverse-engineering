void synthetic_vector_pointer_loop(s128 *arg0, s128 *arg1, s32 arg2) {
    s128 *var_4;
    s128 *var_5;
    s128 temp_2;
    s32 var_6;

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
