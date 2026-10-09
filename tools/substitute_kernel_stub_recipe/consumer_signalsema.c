/* Hand-written game-side consumer of the SignalSema substitute interface.
 * Calls the documented contract exactly as the pinned retail call sites do
 * (sema id in a0 sourced from game memory, jal to the stub). The symbol name
 * is a local label, not a recovered original name.
 */
extern int SignalSema(int sema_id);

static int fr2_sema_storage = 1;

int fr2_consume_signalsema_from_memory(void) {
    SignalSema(fr2_sema_storage);
    return 0;
}
