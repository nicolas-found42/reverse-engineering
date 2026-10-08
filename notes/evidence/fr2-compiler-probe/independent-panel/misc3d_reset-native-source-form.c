/* Hand-written diagnostic reconstruction; inferred names and static store order.
 * See notes/evidence/fr2-compiler-probe/profile-units.json. */
extern int fr2_db_id, fr2_material_a, fr2_material_b, fr2_material_c, fr2_material_d;
void fr2_misc3d_reset(void)
{
    fr2_db_id = -1;
    fr2_material_a = -1;
    fr2_material_b = -1;
    fr2_material_c = -1;
    fr2_material_d = -1;
}
