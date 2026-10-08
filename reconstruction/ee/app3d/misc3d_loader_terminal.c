/* Hand-written source candidate for the loader's remote terminal block.
 * The inferred callable boundary is a design seam; saved Ghidra ownership
 * includes these eight bytes in the loader's noncontiguous flow body.
 */
extern void *misc3d_optional_object;

#if !defined(__APPLE__)
void fr2_misc3d_set_optional_object(void *object)
    __attribute__((section(".text.fr2_misc3d_loader_terminal")));
#endif

void fr2_misc3d_set_optional_object(void *object)
{
    misc3d_optional_object = object;
}
