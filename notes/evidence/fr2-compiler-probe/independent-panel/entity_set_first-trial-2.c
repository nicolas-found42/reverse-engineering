/* Hand-written diagnostic reconstruction; field names and ABI are inferred.
 * See notes/evidence/fr2-compiler-probe/profile-units.json. */
struct fr2_entity { int unresolved; void **payload; };
extern const char fr2_set_first_file[];
extern void fr2_entity_error(struct fr2_entity *, int, const char *, int);
void fr2_entity_set_first(struct fr2_entity *entity, int kind, void *first)
{
    void **payload = entity->payload;
    if (kind == 22)
        payload[0] = first;
    else
        fr2_entity_error(entity, kind, fr2_set_first_file, 290);
}
