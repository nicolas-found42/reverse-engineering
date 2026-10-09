/* Hand-written game-side consumer of the substitute kernel interface.
 * Calls the documented FlushCache(writeback) contract exactly as the pinned
 * retail call sites do (a0 = 0, jal, argument in the delay slot). The symbol
 * name is a local label, not a recovered original name.
 */
extern void FlushCache(int operation);

int fr2_consume_flushcache_writeback(void) {
    FlushCache(0);
    return 0;
}
