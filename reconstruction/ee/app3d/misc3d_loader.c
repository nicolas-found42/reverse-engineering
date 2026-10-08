#include "misc3d_loader.h"

/* Hand-written behavioral candidate from the measured loader call/dataflow.
 * The remote terminal block is represented by the final optional-object store.
 * No original source identity, byte match, or runtime equivalence is claimed.
 */
void fr2_misc3d_load(void)
{
    int resource;
    void *object = 0;
    unsigned long long *flags;

    if (misc3d_db_id != -1)
        misc3d_loader_error(misc3d_source_file, 45, misc3d_error_loaded);

    misc3d_db_id = misc3d_load_database(misc3d_database_name);
    resource = misc3d_find_resource(misc3d_db_id, misc3d_name_optional_first);
    if (resource != -1)
        object = misc3d_resource_object(resource);
    misc3d_set_first_object(object);

    misc3d_state_cc = misc3d_find_resource(misc3d_db_id, misc3d_name_cc);
    misc3d_state_c8 = misc3d_find_resource(misc3d_db_id, misc3d_name_c8);
    misc3d_state_d0 = misc3d_find_resource(misc3d_db_id, misc3d_name_d0);
    misc3d_state_d4 = misc3d_find_resource(misc3d_db_id, misc3d_name_d4);
    if (misc3d_state_d4 == -1)
        misc3d_loader_error(misc3d_source_file, 104, misc3d_error_d4);

    object = misc3d_resource_object(misc3d_state_d4);
    flags = (unsigned long long *)((char *)object + 56);
    *flags &= ~8ULL;
    *flags &= ~16ULL;
    *flags |= 32ULL;
    *flags &= ~64ULL;
    *flags |= 2ULL;
    misc3d_prepare_object(object);

    resource = misc3d_find_resource(misc3d_db_id, misc3d_name_required_a);
    if (resource == -1)
        misc3d_loader_error(misc3d_source_file, 131, misc3d_error_required_a);
    misc3d_set_required_a(misc3d_resource_object(resource));

    resource = misc3d_find_resource(misc3d_db_id, misc3d_name_required_b);
    if (resource == -1)
        misc3d_loader_error(misc3d_source_file, 144, misc3d_error_required_b);
    misc3d_set_required_b(misc3d_resource_object(resource));
    misc3d_finish_resources();

    resource = misc3d_find_resource(misc3d_db_id, misc3d_name_optional_last);
    if (resource != -1)
        fr2_misc3d_set_optional_object(misc3d_resource_object(resource));
}
