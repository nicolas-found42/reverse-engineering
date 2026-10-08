#import <AppKit/AppKit.h>
#import <CoreGraphics/CoreGraphics.h>
#include <unistd.h>
#include <stdio.h>
#include <mach/mach_time.h>
int main(int argc, char **argv) {
    mach_timebase_info_data_t clock;
    mach_timebase_info(&clock);
    int watched = argc > 1 ? atoi(argv[1]) : -1;
    for (int i=0; i<400; i++) {
        @autoreleasepool {
            NSArray *windows = CFBridgingRelease(CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID));
            int owned=0;
            for (NSDictionary *w in windows) if ([w[(NSString *)kCGWindowOwnerPID] intValue] == watched) owned++;
            NSRunningApplication *front = [[NSWorkspace sharedWorkspace] frontmostApplication];
            uint64_t timestamp_ns = mach_absolute_time() * clock.numer / clock.denom;
            printf("%llu %d %d %d\n", (unsigned long long)timestamp_ns, i, front.processIdentifier, owned);
            fflush(stdout);
        }
        usleep(50000);
    }
    return 0;
}
