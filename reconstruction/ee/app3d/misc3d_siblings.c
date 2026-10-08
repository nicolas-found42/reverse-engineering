/* Hand-written source for the bounded reset/release and sibling group.
 * Every identifier here is inferred. Helpers remain external dependencies.
 */
extern int misc3d_db_id;
extern int misc3d_state_c8;
extern int misc3d_state_cc;
extern int misc3d_state_d0;
extern int misc3d_state_d4;
extern void release_database(int);
extern int report_error(const char *, int, const char *);
extern const char misc3d_source_file[];
static const char not_loaded[] __attribute__((section(".fr2_lifecycle_message"))) =
    "Unable to get the misc shadow texture id, the car 3d database isn't loaded";

int fr2_misc3d_get_state_cc(void) __attribute__((section(".text.fr2_misc3d_get_state_cc")));
int fr2_misc3d_get_state_cc(void) {
    if (misc3d_db_id == -1) report_error(misc3d_source_file, 201, not_loaded);
    return misc3d_state_cc;
}
int fr2_misc3d_get_state_d4(void) __attribute__((section(".text.fr2_misc3d_get_state_d4")));
int fr2_misc3d_get_state_d4(void) {
    if (misc3d_db_id == -1) report_error(misc3d_source_file, 215, not_loaded);
    return misc3d_state_d4;
}
int fr2_misc3d_get_state_d0(void) __attribute__((section(".text.fr2_misc3d_get_state_d0")));
int fr2_misc3d_get_state_d0(void) {
    if (misc3d_db_id == -1) report_error(misc3d_source_file, 229, not_loaded);
    return misc3d_state_d0;
}
