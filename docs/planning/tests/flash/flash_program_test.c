#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <sst_flash.h>
#include <machine.h>

#define ROM_BASE   0x00e00000
#define EROM_BASE  (ROM_BASE)
#define OROM_BASE  (ROM_BASE + 1)
#define SECTOR     127                      /* last 4 KiB of each chip: unused by the firmware */
#define CHIP_OFS   ((uint32_t)SECTOR * SST_SECT_SIZE)

static volatile uint8_t *const rom = (volatile uint8_t *) ROM_BASE;
static volatile uint32_t *const upticks = (volatile uint32_t *) 0x40C;

static uint8_t pattern(uint32_t i, int odd) { return (uint8_t)(i * 7 + (odd ? 0x5A : 0x11)); }

static int verify(void) {
    int bad = 0;
    for (uint32_t i = 0; i < SST_SECT_SIZE; i++) {
        if (rom[(CHIP_OFS + i) * 2] != pattern(i, 0)) bad++;
        if (rom[(CHIP_OFS + i) * 2 + 1] != pattern(i, 1)) bad++;
    }
    return bad;
}

void kmain(void) {
    SSTDeviceId even, odd;
    printf("\r\n#FL start\r\n");
    uint8_t m = mcDisableInterrupts();
    sst_get_device_info(EROM_BASE, &even);
    sst_get_device_info(OROM_BASE, &odd);
    mcEnableInterrupts(m);
    printf("#FL even: mfr=%02x dev=%02x %s %s\r\n", even.manufacturer, even.device, sst_get_manufacturer_name(&even), sst_get_device_name(&even));
    printf("#FL odd : mfr=%02x dev=%02x %s %s\r\n", odd.manufacturer, odd.device, sst_get_manufacturer_name(&odd), sst_get_device_name(&odd));

    int before = verify();
    printf("#FL verify before programming: %d mismatches\r\n", before);
    if (before == 0) {
        printf("#FL pattern already present (persisted from an earlier run)\r\n#FL end\r\n");
        return;
    }

    uint32_t t0 = *upticks;
    m = mcDisableInterrupts();
    bool ok = sst_sector_erase(EROM_BASE, SECTOR) && sst_sector_erase(OROM_BASE, SECTOR);
    for (uint32_t i = 0; ok && i < SST_SECT_SIZE; i++) {
        ok = sst_write_byte(EROM_BASE, CHIP_OFS + i, pattern(i, 0))
          && sst_write_byte(OROM_BASE, CHIP_OFS + i, pattern(i, 1));
    }
    mcEnableInterrupts(m);
    uint32_t t1 = *upticks;
    printf("#FL erase+program ok=%d (%lu ticks)\r\n", ok, (unsigned long)(t1 - t0));
    printf("#FL verify after programming: %d mismatches\r\n", verify());
    printf("#FL firmware intact: ROM word at $E00400 = %02x%02x%02x%02x\r\n", rom[0x400], rom[0x401], rom[0x402], rom[0x403]);
    printf("#FL end\r\n");
}
