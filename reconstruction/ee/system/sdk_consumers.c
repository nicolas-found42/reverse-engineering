#include "sdk_consumers.h"

#ifdef __mips__
#define FR2_SECTION(name) __attribute__((section(name)))
#else
#define FR2_SECTION(name)
#endif

/* Local names, not recovered original declarations. Initialized words are
 * measured at 0024bad8, 0024f8e0 and 0024f8e4. No ownership credit is claimed.
 */
int fr2_mfile_sema FR2_SECTION(".data.fr2_mfile_sema") = 0;
int fr2_mfile_marker FR2_SECTION(".data.fr2_mfile_marker") = -1;
unsigned int fr2_mfile_count FR2_SECTION(".data.fr2_mfile_count") = 0;

#ifdef __mips__
_Static_assert(sizeof(SifDmaTransfer_t) == 16, "retail DMA descriptor size");
_Static_assert(sizeof(unsigned int) == 4, "retail counter width");
#endif

/* 0020c940: preserve both the nonzero counter result and tail-call result.
 * Unsigned subtraction expresses the observed wrapping 32-bit addiu.
 */
int FR2_SECTION(".text.fr2_mfile_release") fr2_mfile_release(void)
{
    unsigned int remaining = fr2_mfile_count - 1U;
    fr2_mfile_count = remaining;
    if (remaining == 0) {
        fr2_mfile_marker = -1;
        return SignalSema(fr2_mfile_sema);
    }
    return remaining <= 0x7fffffffU ? (int)remaining : -1 - (int)(~remaining);
}

/* 0011b780: a negative status ends polling; neither a successful DMA nor a
 * timeout is implied. Preserve the original absence of transaction retries.
 */
int FR2_SECTION(".text.fr2_dma_copy")
fr2_dma_copy(void *destination, void *source, int size)
{
    SifDmaTransfer_t transfer;
    int transaction;
    if (size <= 0)
        return 0;
    transfer.src = source;
    transfer.dest = destination;
    transfer.size = size;
    transfer.attr = 0;
    FlushCache(0);
    transaction = sceSifSetDma(&transfer, 1);
    while (sceSifDmaStat(transaction) >= 0) {}
    return size;
}
