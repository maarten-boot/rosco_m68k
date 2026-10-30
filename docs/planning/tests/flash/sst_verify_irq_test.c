#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <sst_flash.h>
#include <machine.h>

#define ROM_BASE   0x00e00000
#define EROM_BASE  (ROM_BASE)
#define OROM_BASE  (ROM_BASE + 1)
static volatile uint8_t *const rom = (volatile uint8_t *) ROM_BASE;
static uint32_t ofs(uint8_t sector, uint32_t i) { return (uint32_t)sector * SST_SECT_SIZE + i; }

void kmain(void) {
    printf("\r\n#V start\r\n");

    /* 1. verify: program 0x00, then 0xFF over it without erasing (flash can only clear bits) */
    uint8_t m = mcDisableInterrupts();
    bool e = sst_sector_erase(EROM_BASE, 125);
    bool w1 = sst_write_byte(EROM_BASE, ofs(125, 0), 0x00);
    bool w2 = sst_write_byte(EROM_BASE, ofs(125, 0), 0xFF);
    mcEnableInterrupts(m);
    printf("#V1 erase=%d write(00)=%d write(FF over 00)=%d cell=%02x (expect write(FF)=0 with verify)\r\n",
           e, w1, w2, rom[ofs(125, 0) * 2]);

    /* 2. interrupt safety: caller leaves interrupts ENABLED (100Hz tick runs from flash) */
    printf("#V2 erase+program sector 126 with interrupts enabled...\r\n");
    bool ok = sst_sector_erase(EROM_BASE, 126) && sst_sector_erase(OROM_BASE, 126);
    for (uint32_t i = 0; ok && i < 2048; i++) {
        ok = sst_write_byte(EROM_BASE, ofs(126, i), (uint8_t) i) && sst_write_byte(OROM_BASE, ofs(126, i), (uint8_t) ~i);
    }
    int bad = 0;
    for (uint32_t i = 0; i < 2048; i++) {
        if (rom[ofs(126, i) * 2] != (uint8_t) i || rom[ofs(126, i) * 2 + 1] != (uint8_t) ~i) bad++;
    }
    printf("#V2 ok=%d mismatches=%d\r\n#V end\r\n", ok, bad);
}
