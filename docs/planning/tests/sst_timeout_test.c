#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <sst_flash.h>
#include <machine.h>

/* RAM stands in for the flash: writes are harmless, and a MAME read
 * watchpoint can make DQ6 toggle forever to simulate a stuck chip. */
#define FAKE_ROM 0x80000

void kmain(void) {
    volatile uint32_t *upticks = (volatile uint32_t *) 0x40C;
    printf("\r\n#SST start\r\n");
    uint32_t t0 = *upticks;
    bool ok = sst_write_byte(FAKE_ROM, 0, 0x5A);
    uint32_t t1 = *upticks;
    printf("#SST write_byte=%d ticks=%lu\r\n", ok, (unsigned long)(t1 - t0));
    t0 = *upticks;
    ok = sst_sector_erase(FAKE_ROM, 0);
    t1 = *upticks;
    printf("#SST sector_erase=%d ticks=%lu\r\n#SST end\r\n", ok, (unsigned long)(t1 - t0));
}
