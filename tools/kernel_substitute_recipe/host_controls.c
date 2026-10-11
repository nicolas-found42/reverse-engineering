/* Controls at the external kernel boundary, never a guest hardware oracle. */
#include "../../reconstruction/ee/system/sdk_consumers.h"
#include <assert.h>
#include <limits.h>

static int events, polls, busy_polls, transaction_id, expected_size, expected_sema;
static char source, destination;

void FlushCache(int operation)
{
    assert(events == 0 && operation == 0);
    events = 1;
}
int sceSifSetDma(SifDmaTransfer_t *transfer, int count)
{
    assert(events == 1 && count == 1);
    assert(transfer->src == &source && transfer->dest == &destination);
    assert(transfer->size == expected_size && transfer->attr == 0);
    events = 2;
    return transaction_id;
}
int sceSifDmaStat(int transaction)
{
    assert(events == 2 && transaction == transaction_id);
    return polls++ < busy_polls ? 0 : -1;
}
int SignalSema(int sema_id)
{
    assert(events == 0 && sema_id == expected_sema);
    assert(fr2_mfile_count == 0 && fr2_mfile_marker == -1);
    events = 1;
    return -37;
}

int main(void)
{
    int sizes[] = {INT_MIN, -1, 0, 1, 16, 32768, INT_MAX};
    int ids[] = {-1, 0, 17};
    unsigned int counters[] = {0U, 1U, 2U, 0x80000000U, 0x80000001U, 0xffffffffU};
    int results[] = {-1, -37, 1, INT_MAX, INT_MIN, -2};
    for (unsigned int i = 0; i < sizeof(sizes)/sizeof(sizes[0]); ++i) {
        for (unsigned int j = 0; j < sizeof(ids)/sizeof(ids[0]); ++j) {
            for (busy_polls = 0; busy_polls <= 3; ++busy_polls) {
                events = polls = 0;
                transaction_id = ids[j];
                expected_size = sizes[i];
                assert(fr2_dma_copy(&destination, &source, sizes[i]) == (sizes[i] > 0 ? sizes[i] : 0));
                assert(events == (sizes[i] > 0 ? 2 : 0));
                assert(polls == (sizes[i] > 0 ? busy_polls + 1 : 0));
            }
        }
    }
    for (unsigned int i = 0; i < sizeof(counters)/sizeof(counters[0]); ++i) {
        events = 0;
        fr2_mfile_count = counters[i];
        fr2_mfile_marker = 123;
        fr2_mfile_sema = expected_sema = -9;
        assert(fr2_mfile_release() == results[i]);
        assert(events == (i == 1 ? 1 : 0));
        assert(fr2_mfile_marker == (i == 1 ? -1 : 123));
    }
    return 0;
}
