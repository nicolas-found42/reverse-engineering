/* Hand-written diagnostic reconstruction; names and table ABI are inferred.
 * See notes/evidence/fr2-compiler-probe/profile-units.json. */
struct fr2_parser_entry { int key; int value; };
extern struct fr2_parser_entry fr2_parser_table[];
extern const char fr2_parser_file[], fr2_parser_message[];
extern void report_error(const char *, int, const char *, ...) __attribute__((noreturn));
int fr2_parser_lookup(int key)
{
    struct fr2_parser_entry *entry = fr2_parser_table;
    do {
        if (entry->key == key)
            return entry->value;
        if (entry->key == 5)
            report_error(fr2_parser_file, 736, fr2_parser_message, key);
        ++entry;
    } while (1);
}
