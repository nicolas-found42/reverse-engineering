extern int misc3d_db_id;
extern int report_error(const char *, int, const char *);
static const char source_file[] __attribute__((section(".fr2_file"))) = "../fr2/source/app3d/misc3d.c";
static const char message[] __attribute__((section(".fr2_message"))) = "Unable to get the misc 3d database id, it isn't loaded";
int probe(void) {
    int value = misc3d_db_id;
    if (value != -1) return value;
    return report_error(source_file, 188, message);
}
