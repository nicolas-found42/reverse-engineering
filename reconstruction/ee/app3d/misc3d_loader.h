#ifndef FR2_MISC3D_LOADER_H
#define FR2_MISC3D_LOADER_H

/* Local inferred names and bounded low-word ABI; no original declarations. */
extern int misc3d_db_id;
extern int misc3d_state_c8, misc3d_state_cc, misc3d_state_d0, misc3d_state_d4;
extern void *misc3d_optional_object;
extern const char misc3d_source_file[], misc3d_database_name[];
extern const char misc3d_name_optional_first[], misc3d_name_cc[], misc3d_name_c8[];
extern const char misc3d_name_d0[], misc3d_name_d4[], misc3d_name_required_a[];
extern const char misc3d_name_required_b[], misc3d_name_optional_last[];
extern const char misc3d_error_loaded[], misc3d_error_d4[];
extern const char misc3d_error_required_a[], misc3d_error_required_b[];

int misc3d_load_database(const char *name);
int misc3d_find_resource(int database, const char *name);
void *misc3d_resource_object(int resource);
void misc3d_set_first_object(void *object);
void misc3d_prepare_object(void *object);
void misc3d_set_required_a(void *object);
void misc3d_set_required_b(void *object);
void misc3d_finish_resources(void);
void misc3d_loader_error(const char *file, int line, const char *message)
    __attribute__((noreturn));
void fr2_misc3d_set_optional_object(void *object);
void fr2_misc3d_load(void);

#endif
