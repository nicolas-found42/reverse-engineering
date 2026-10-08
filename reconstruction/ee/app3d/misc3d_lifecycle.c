/* Hand-written source for the bounded reset/release and sibling group.
 * Every identifier here is inferred. Helpers remain external dependencies.
 */
extern int misc3d_db_id;
extern int misc3d_state_c8;
extern int misc3d_state_cc;
extern int misc3d_state_d0;
extern int misc3d_state_d4;
extern void release_database(int);
void fr2_misc3d_reset(void) __attribute__((section(".text.fr2_misc3d_reset")));
void fr2_misc3d_reset(void) {
    misc3d_db_id = -1;
    misc3d_state_c8 = -1;
    misc3d_state_cc = -1;
    misc3d_state_d0 = -1;
    misc3d_state_d4 = -1;
}

void fr2_misc3d_release(void) __attribute__((section(".text.fr2_misc3d_release")));
void fr2_misc3d_release(void) {
    if (misc3d_db_id != -1) {
        release_database(misc3d_db_id);
        misc3d_db_id = -1;
    }
}
