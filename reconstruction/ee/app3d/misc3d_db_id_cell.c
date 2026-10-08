/* Local inferred name. Startup zeroes this cell; reset code writes -1 later.
 * Explicit NOBITS placement is verified by tools/misc3d_contract.py.
 */
int misc3d_db_id __attribute__((aligned(4)));
