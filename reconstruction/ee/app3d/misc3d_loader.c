#include "misc3d_loader.h"

/* Hand-written candidate for the measured misc3d loader.
 * Keep the initial unloaded sentinel and the returned d4 id in locals.
 * The layout exposes only the evidenced flag member at byte offset 56.
 * The final call targets a separate leaf whose ownership remains mixed.
 * Original declarations and runtime equivalence are not claimed.
 */
void fr2_misc3d_load(void)
{
    int resource;
    int loaded_d4;
    int unloaded_id = misc3d_db_id;
    void *object;
    struct object_layout { char prefix[56]; unsigned long long flags; };
    struct object_layout *flag_object;

    if (unloaded_id != -1)
        misc3d_loader_error(misc3d_source_file, 45, misc3d_error_loaded);

    object = 0;
    misc3d_db_id = misc3d_load_database(misc3d_database_name);
    resource = misc3d_find_resource(misc3d_db_id, misc3d_name_optional_first);
    if (resource != unloaded_id)
        object = misc3d_resource_object(resource);
    misc3d_set_first_object(object);

    misc3d_state_cc = misc3d_find_resource(misc3d_db_id, misc3d_name_cc);
    misc3d_state_c8 = misc3d_find_resource(misc3d_db_id, misc3d_name_c8);
    misc3d_state_d0 = misc3d_find_resource(misc3d_db_id, misc3d_name_d0);
    loaded_d4 = misc3d_state_d4 = misc3d_find_resource(misc3d_db_id, misc3d_name_d4);
    if (loaded_d4 == unloaded_id)
        misc3d_loader_error(misc3d_source_file, 104, misc3d_error_d4);

    object = misc3d_resource_object(loaded_d4);
    flag_object = object;
    flag_object->flags &= ~8ULL;
    flag_object->flags &= ~16ULL;
    flag_object->flags |= 32ULL;
    flag_object->flags &= ~64ULL;
    flag_object->flags |= 2ULL;
    misc3d_prepare_object(object);

    resource = misc3d_find_resource(misc3d_db_id, misc3d_name_required_a);
    if (resource != unloaded_id)
        misc3d_set_required_a(misc3d_resource_object(resource));
    else
        misc3d_loader_error(misc3d_source_file, 131, misc3d_error_required_a);

    resource = misc3d_find_resource(misc3d_db_id, misc3d_name_required_b);
    if (resource != -1)
        misc3d_set_required_b(misc3d_resource_object(resource));
    else
        misc3d_loader_error(misc3d_source_file, 144, misc3d_error_required_b);
    misc3d_finish_resources();

    resource = misc3d_find_resource(misc3d_db_id, misc3d_name_optional_last);
    if (resource != -1)
        fr2_misc3d_set_optional_object(misc3d_resource_object(resource));
}
