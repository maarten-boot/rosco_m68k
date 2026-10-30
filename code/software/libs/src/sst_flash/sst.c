/*
 *------------------------------------------------------------
 *                                  ___ ___ _   
 *  ___ ___ ___ ___ ___       _____|  _| . | |_ 
 * |  _| . |_ -|  _| . |     |     | . | . | '_|
 * |_| |___|___|___|___|_____|_|_|_|___|___|_,_| 
 *                     |_____|         tech demo
 * ------------------------------------------------------------
 * Copyright (c)2021 Ross Bamford
 * See top-level LICENSE.md for licence information.
 *
 * SST39SF0x0 Flash EEPROM interface library
 * ------------------------------------------------------------
 */

#include "sst_flash.h"

#define SST_UNLOCK_A1       ((0x00005555<<1))
#define SST_UNLOCK_D1       0xAA
#define SST_UNLOCK_A2       ((0x00002AAA<<1))
#define SST_UNLOCK_D2       0x55

#define SST_SUBCMD_SECERASE 0x30
#define SST_SUBCMD_CHPERASE 0x10

static void write(uint32_t addr, uint8_t data) {
    volatile uint8_t *p = (uint8_t*)addr;
    *p = data;
}

// Upper bound on toggle-bit polls. Interrupts are masked while flashing
// (the handlers live in this ROM), so the tick counter cannot be used.
// SST39SF0x0 worst case is 100ms (chip erase). One poll takes ~5us at
// 10MHz (measured in MAME), so this gives up after ~5s there and still
// waits ~0.3s on a fast cached 68030. It only matters if the chip never
// finishes.
#define SST_MAX_POLLS   1000000UL

// Wait for an erase/program operation to finish (DQ6 stops toggling).
// Returns false if it is still toggling after SST_MAX_POLLS reads.
static bool wait(uint32_t addr) {
    volatile uint8_t *p = (uint8_t*)addr;

    uint8_t last = (*p) & 0x40;
    uint8_t this;

    for (uint32_t polls = 0; (this = ((*p) & 0x40)) != last; polls++) {
        if (polls >= SST_MAX_POLLS) {
            return false;
        }
        last = this;
    }

    return true;
}

static uint8_t flash_read(uint32_t addr) {
    volatile uint8_t *p = (uint8_t*)addr;
    return *p;
}

// While a flash chip is in ID mode or busy programming/erasing, reads from
// it return ID or status bits instead of data. The exception vectors and
// handlers live in the system ROM, so an interrupt in that window would
// execute garbage. Mask interrupts (IPL 7) for each whole command sequence,
// including the wait, and restore the caller's mask afterwards.
// (rosco_m68k programs run in supervisor mode, so SR is accessible.)
static inline uint16_t irq_disable(void) {
    uint16_t sr;
    __asm__ volatile ("move.w %%sr,%0\n\tori.w #0x0700,%%sr" : "=d" (sr) : : "memory", "cc");
    return sr;
}

static inline void irq_restore(uint16_t sr) {
    __asm__ volatile ("move.w %0,%%sr" : : "d" (sr) : "memory", "cc");
}

static void unlock(uint32_t rom_base) {
    write(rom_base | SST_UNLOCK_A1, SST_UNLOCK_D1);
    write(rom_base | SST_UNLOCK_A2, SST_UNLOCK_D2);
}

bool sst_command(uint32_t rom_base, SST_COMMAND command) {
    unlock(rom_base);

    write(rom_base | SST_UNLOCK_A1, command);

    // TODO Tida etc wait might be needed here. 
    // Guaranteed not needed on r1 @ 10MHz...
    
    return true;
}

bool sst_sector_erase(uint32_t rom_base, uint8_t sector) {
    uint16_t sr = irq_disable();
    bool ok = sst_command(rom_base, SST_CMD_ERASE);
    if (ok) {
        unlock(rom_base);
        write(rom_base | (sector << 13), SST_SUBCMD_SECERASE);
        ok = wait(rom_base);
    }
    irq_restore(sr);

    // Verify: every byte of an erased sector reads 0xFF
    uint32_t sector_base = (uint32_t) sector * SST_SECT_SIZE;
    for (uint32_t i = 0; ok && i < SST_SECT_SIZE; i++) {
        ok = flash_read(rom_base | ((sector_base + i) << 1)) == 0xFF;
    }

    return ok;
}

// TODO 
bool sst_chip_erase(uint32_t rom_base) {
    uint16_t sr = irq_disable();
    bool ok = sst_command(rom_base, SST_CMD_ERASE);
    if (ok) {
        unlock(rom_base);
        write(rom_base | SST_UNLOCK_A1, SST_SUBCMD_CHPERASE);
        ok = wait(rom_base);
    }
    irq_restore(sr);

    // Not verified here (the chip size depends on the device); use
    // sst_get_device_info() and read back if needed.
    return ok;
}

bool sst_write_byte(uint32_t rom_base, uint32_t byte_addr, uint8_t data) {
    uint16_t sr = irq_disable();
    bool ok = sst_command(rom_base, SST_CMD_BYTEPROG);
    if (ok) {
        write(rom_base | (byte_addr << 1), data);
        ok = wait(rom_base);
    }
    irq_restore(sr);

    // Verify: programming can only clear bits, so this also catches writes
    // to a byte that was not erased first
    return ok && flash_read(rom_base | (byte_addr << 1)) == data;
}

static uint8_t read_manufacturer_id(uint32_t rom_base) {
    volatile uint8_t *p = (uint8_t*)rom_base;
    return *p;
}

static uint8_t read_device_id(uint32_t rom_base) {
    volatile uint8_t *p = (uint8_t*)(rom_base | 2);
    return *p;
}

void sst_get_device_info(uint32_t rom_base, SSTDeviceId* sst) {
    uint16_t sr = irq_disable();
    sst_command(rom_base, SST_CMD_IDENTER);

    // Very limited as to what we can do here, with no ROM support...
    sst->manufacturer = read_manufacturer_id(rom_base);
    sst->device = read_device_id(rom_base);

    // ROM should be available again max 150ns after this is done
    sst_command(rom_base, SST_CMD_IDEXIT);
    irq_restore(sr);
}

const char* sst_get_manufacturer_name(SSTDeviceId *sst) {
    switch (sst->manufacturer) {
    case SST_MFR_SST:
        return "SST";
    default:
        return "???";
    }
}

const char* sst_get_device_name(SSTDeviceId *sst) {
    switch (sst->device) {
    case SST_DEV_010A:
        return "SST39SF010A";
    case SST_DEV_020A:
        return "SST39SF020A";
    case SST_DEV_040:
        return "SST39SF040 ";
    default:
        return " <Unknown> ";
    }
}

