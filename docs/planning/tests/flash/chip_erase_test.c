/*
 * T-EMU5: chip-erase both flash chips from software, then halt.
 * After the erase no ROM code (TRAPs, tick handler) is usable, so
 * interrupts stay masked and the program stops the CPU.
 */
#include <stdio.h>
#include <stdbool.h>
#include <sst_flash.h>

#define ROM_BASE    0x00e00000

void kmain() {
    printf("#ER start\r\n");
    __asm__ volatile ("move.w #0x2700,%%sr" ::: "memory");
    volatile bool ok_even = sst_chip_erase(ROM_BASE);
    volatile bool ok_odd = sst_chip_erase(ROM_BASE + 1);
    (void)ok_even; (void)ok_odd;
    for (;;) __asm__ volatile ("stop #0x2700");
}
