/* Inferred interfaces for the two bounded retail consumers. */
#ifndef FR2_SDK_CONSUMERS_H
#define FR2_SDK_CONSUMERS_H

#ifdef __mips__
#include <kernel.h>
#else
/* Host controls implement only the external kernel boundary. */
typedef struct {
    void *src;
    void *dest;
    int size;
    int attr;
} SifDmaTransfer_t;
extern void FlushCache(int operation);
extern int SignalSema(int sema_id);
extern int sceSifSetDma(SifDmaTransfer_t *transfer, int count);
extern int sceSifDmaStat(int transaction);
#endif

extern unsigned int fr2_mfile_count;
extern int fr2_mfile_marker;
extern int fr2_mfile_sema;
int fr2_mfile_release(void);
int fr2_dma_copy(void *destination, void *source, int size);
#endif
