import os, sys, re
OUT = sys.argv[1]
FW = 'code/firmware/rosco_m68k_firmware/'
LB = 'code/software/libs/src/'
FORK = 'maarten-boot/rosco_m68k'
TESTS = 'docs/planning/tests/ (branch `planning/session-docs` on ' + FORK + ')'
HDR = """**Affects:** {affects}
**Found by:** code review of v2.42 plus runtime tests in MAME (`rosco_m68k_010`); details in {tests}
"""
issues = [
dict(n=1, ids='A-1', title='TRAP 14 DEVICE_CTRL ignores the parameter in D2 and always writes $40 to the DUART CSR',
 status='Confirmed in MAME (watchpoint on CSRA: requested $BB, written $40; console stops afterwards).',
 where=[FW+'stage1/duart.asm:404', FW+'stage1/duart.asm (D_CTRL_DUART_B, CSRB)', FW+'stage1/trap14.asm (dispatcher multiplies D1 by 4)'],
 body="""InterfaceReference.md (DEVICE_CTRL, function 16), the handler's own header comment and the libs' `mcDeviceCtrl` all pass the command parameter in **D2.L**, but `D_CTRL_DUART_A/B` write **D1** to CSRA/CSRB. At that point D1 is no longer the caller's value: the TRAP 14 dispatcher has already turned the function code into `16*4 = 64`, so every "set baud rate" request writes `$40` to the clock-select register.""",
 repro="`tests/t_a1.asm`: GET_DEVICE 0, then TRAP 14 fn 16 with D0=0, D2=$BB; watch writes to CSRA ($F00003) with `mame/run_api.dbg`-style watchpoint.",
 fix="`move.b D2,DUART_CSRA(A0)` / `move.b D2,DUART_CSRB(A0)` (and fix the comment).", branch='fix/A-1'),
dict(n=2, ids='A-12', title='Serial PRINT/PRINTLN (TRAP 14 fn 0/1) clobber D0 although documented to modify only A0',
 status='Confirmed in MAME on v2.42 and on develop ($DEADBEEF comes back as $DEADBE00).',
 where=[FW+'stage1/duart.asm:214 (EARLY_PRINT_DUART)'],
 body="""The default DUART console uses D0 as its character register and only saves A1. InterfaceReference.md says PRINT/PRINTLN modify only A0. The V9958 and Xosera consoles already comply.""",
 repro="`tests/t_easy_m.asm` (first line of output: `#A12 D0 after PRINT=`).",
 fix="Save/restore D0 with A1 (`movem.l D0/A1,-(A7)` … `movem.l (A7)+,D0/A1`).", branch='fix/A-12'),
dict(n=3, ids='A-2, B-14', title='`__divsi3`/`__modsi3` in the firmware are unsigned, so signed division is wrong',
 status='Confirmed in MAME by calling the ROM helpers: −7/2 = $7FFFFFFC, −7%2 = 1, 7/−2 = 0.',
 where=[FW+'stage1/common.c:29'],
 body="""On 68000/68010 GCC calls the libgcc helpers for `int` `/` and `%`. The firmware provides its own `__divsi3`/`__modsi3`, but they take `uint32_t` and call the unsigned `divmod`, so any negative operand gives a wrong result (no current firmware path is known to divide negative numbers, so this is latent but a trap for future code).""",
 repro="`tests/t_div_m.asm` (adjust DIVSI3/MODSI3 to the addresses in the build's map).",
 fix="Compute magnitudes unsigned and apply C sign rules (truncate toward zero, remainder follows the dividend); see branch.", branch='fix/A-2-B-14'),
dict(n=4, ids='A-4, A-9', title='Two stage1 assembler slips: `or.w #0700,SR` (decimal) and word-sized decompress return',
 status='A-4 confirmed in the assembled ROM (`oriw #$02BC,%sr`). A-9 confirmed by reading; latent with the current stage2 size.',
 where=[FW+'stage1/rev2.asm:107 (and two more in rev2.asm, three in rev1.asm)', FW+'stage1/decompress.asm:10'],
 body="""- **A-4:** the bus-error/address-error/illegal-instruction LED handlers use `or.w #0700,SR`. vasm reads `0700` as decimal 700 = `$02BC`, which does not mask interrupts to level 7 (and sets stray CCR bits). Everywhere else uses `$0700`.
- **A-9:** `decompress_stage2` returns `move D2,D0` (word). The upper word of D0 still holds the input length, so a failed decode of a compressed stage2 ≥ 64 KiB would look like success to `main1.c`.""",
 repro="A-4: `objdump -d` of the ROM around the handlers. A-9: flip a byte in the zipped stage2 (still detected today because the image is < 64 KiB).",
 fix="`#$0700`; `move.l D2,D0`.", branch='fix/A-4 and fix/A-9'),
dict(n=5, ids='E-1, E-2, E-3, E-4, E-5, E-6, E-8', title='EASy68K TRAP 15 layer: crash on unknown task, A0 clobbered, several tasks return wrong results',
 status='All confirmed in MAME on v2.42; E-1, E-2, E-4, E-8 re-confirmed on develop (smoke test).',
 where=[FW+'stage1/easy68k/syscalls_asm.asm:28 (dispatcher)', FW+'stage1/easy68k/syscalls_asm.asm:242 (task 7)', FW+'stage1/easy68k/syscalls_asm.asm:259 (task 8)', FW+'stage1/easy68k/syscalls_asm.asm:330 (task 16)', FW+'stage1/easy68k/syscalls.c:34', FW+'stage1/ansicon.asm:16'],
 body="""- [ ] **E-1** An out-of-range task number (e.g. 21) takes `.DONE: rte` with the saved D0 still on the stack → `rte` pops garbage → bus error. Also the range check uses D0.L although EASy68K defines the task in D0.B.
- [ ] **E-8** The dispatcher loads the jump target into A0 and never restores it; EASy68K tasks are documented to preserve other registers.
- [ ] **E-2** Signed number output (tasks 3, 17, 20) prints nothing for 0 (`while (value > 0)`), and only "-" for INT32_MIN.
- [ ] **E-3** Task 16 uses `move.b 0,PROMPT_ON` / `move.b 1,…` (absolute addresses, not immediates); it only works because byte 1 of the reset SSP happens to be non-zero.
- [ ] **E-4** Task 8 returns the word at $408 (heartbeat down-counter 49..0) instead of the 32-bit SDB_UPTICKS at $40C; upper half of D1 is left stale.
- [ ] **E-5** Task 7 (input pending) has only an MFP (r1) implementation; on r2.x it always returns 0 (`TODO else for r2X`).
- [ ] **E-6** Task 11 / ANSI_MOVEXY sends 0-based row/col straight into `ESC[row;colH`, which is 1-based → off by one.""",
 repro="`tests/t_easy_m.asm`, `tests/t_misc_m.asm`, `tests/t_e5.asm` + `mame/harness_e5.py`.",
 fix="One commit per item on the branches below.", branch='fix/E-1-E-8, fix/E-2, fix/E-3, fix/E-4, fix/E-5, fix/E-6'),
dict(n=6, ids='B-1, B-2, B-3', title='stage2 loaders do not bound kernel loads: oversized ROSCODE1.BIN causes a crash/reboot loop',
 status='B-1 confirmed in MAME (768000-byte BIN → bus error at PC=$0F0206 → warm boot reloads the file → endless loop). B-2/B-3 by reading.',
 where=[FW+'stage2/load/load.c:66 (load_kernel_bin)', FW+'stage2/load/load.c:155 (ELF segment check)', FW+'stage2/kermit/kermit_support.c:92 (writefile)'],
 body="""- **B-1** `load_kernel_bin` reads blocks to the load address with no upper limit. Anything past ~704 KiB overwrites the running stage2 (and stack/SDB). Because the crash warm-boots and the card is still inserted, the board loops until the card is removed. The ELF path already has `load_range_allowed()`.
- **B-2** Kermit `writefile()` memcpy's every data packet with no limit either.
- **B-3** The ELF loader range-checks `p_memsz` but reads `p_filesz` bytes; with `p_filesz > p_memsz` it writes past the checked range and `memset(…, p_memsz - p_filesz)` underflows.""",
 repro="FAT32 SD image (MBR, partition at LBA 2048) with a 768000-byte ROSCODE1.BIN; boot in MAME with `-hard1`.",
 fix="Check each BIN block with `load_range_allowed()`; refuse Kermit packets that would cross STAGE2_LOAD; reject `p_filesz > p_memsz`.", branch='fix/B-1, fix/B-2, fix/B-3'),
dict(n=7, ids='B-4', title='SD init reports success when CMD58 (read OCR) fails, leaving the card struct uninitialised',
 status='Confirmed in MAME with fault injection (forcing the CMD58 result non-zero).',
 where=[FW+'stage1/blockdev/bbsd.c:68'],
 body="""In `BBSD_initialize`, the V2 path does `if (raw_sd_command(58, 0)) goto finally;` while `result` is still `BBSD_INIT_OK`. `sd->initialized`/`sd->type` are never set, but callers (stage2, TRAP 13 SD_INIT users) are told the card is usable.""",
 repro="`mame/b4_cmd58_inject.dbg` (set the address of the `tst.b d0` after CMD58 from the build's disassembly).",
 fix="Return a new status `BBSD_INIT_CMD58_FAILED` (`SD_INIT_CMD58_FAILED` in sdfat.h, ordinal 4).", branch='fix/B-4'),
dict(n=8, ids='B-5', title='SD block write ignores the data-response token: rejected writes are reported as success',
 status='Confirmed in MAME: injecting a write-error token ($0D) still returned success before the fix; normal writes verified by read-back.',
 where=[FW+'stage1/blockdev/bbsd.c:281 (BBSD_write_block)'],
 body="""After the data block, the code only waits for MISO to return to $FF. A rejected block (CRC/write-error token) has no busy phase, so the next byte is $FF and the write "succeeds". `WRITE_RESPONSE_OK` is defined in bbsd.h but unused. This matters for anything writing through TRAP 13 (e.g. an OS using the ROM SD driver).""",
 repro="`tests/t_sdw.asm` (TRAP 13 init/write/read-back) and `mame/sdw_bad.dbg` (token injection).",
 fix="Read the token, require `(token & 0x1F) == 0x05`, then wait for the busy phase to end.", branch='fix/B-5'),
dict(n=9, ids='B-6', title='SD timeouts are poll counts, far shorter than the SD spec on the bit-banged SPI',
 status='Confirmed in MAME: a card held busy is abandoned after the old poll count; with the fix, after ~540 ms (time-based). Slow real cards not tested.',
 where=[FW+'stage1/blockdev/include/bbsd.h:55 (and the other *_RETRIES/*_TIMEOUT)'],
 body="""E.g. 2500 polls for write busy vs. up to 250 ms (500 ms SDXC), 200 polls for read access vs. 100 ms, 400 ACMD41 tries vs. 1 s. Slow cards then fail writes/init.""",
 repro="`tests/t_sdw_t.asm` + `mame/sdt_busy.dbg` (forces the card busy forever and measures ticks).",
 fix="Measure waits with SDB_UPTICKS (read 200 ms, write/busy 500 ms, init 1 s) with large poll caps as fallback when interrupts are masked; forced reset/idle commands keep the short wait so a no-card boot is not slowed (checked: same boot time). Based on fix/B-5.", branch='fix/B-6'),
dict(n=10, ids='B-8, B-9', title='ATA: LBA28 only (addresses ≥ 2^28 silently wrap) and writes are not completed/checked',
 status='B-8 confirmed in MAME on a v2.42 build with the ATA EFPs enabled (partition at LBA 2^28+2048 read the decoy at LBA 2048). B-9 by reading. No fix branch yet.',
 where=[FW+'stage1/blockdev/ata.c:216 (read)', FW+'stage1/blockdev/ata.c:250 (write)'],
 body="""- **B-8** LBA bits above 27 are dropped; only READ/WRITE PIO (0x20/0x30) are used, IDENTIFY capacity is not consulted. On disks > 128 GiB a partition beyond the limit reads – and **writes** – the wrong sectors.
- **B-9** `ata_write_one` does not wait for BSY to clear, check ERR/DF, or issue CACHE FLUSH; write errors are reported as success.""",
 repro="Sparse ~129 GiB raw `.hd` image as `-hard2` with a FAT32 partition at LBA 2^28+2048 and a different FAT32 volume at LBA 2048 (recipe in tests/README.md).",
 fix="Interim: reject LBA ≥ 2^28. Proper: READ/WRITE SECTORS EXT using IDENTIFY words 83/100-103; poll status after writes and FLUSH CACHE.", branch='— (not yet)'),
dict(n=11, ids='B-12, B-20, E-9', title='InterfaceReference.md does not match TRAP 13 / TRAP 15 behaviour',
 status='Confirmed by reading and in the R-3 conformance table.',
 where=[FW+'InterfaceReference.md:326 (SPI_INIT)', FW+'stage1/blockdev/syscalls_asm.asm:43'],
 body="""- **B-12** SPI_INIT is documented as "0 = OK", but it returns 1 (true) on success (and SPI_ASSERT_CS/DEASSERT_CS use "0 = failed").
- **B-20** CHECK_SD / CHECK_SPI / CHECK_ATA_SUPPORT (FC 0, 5, 15) also trash A0, like every TRAP 13 function, but only D0 is listed.
- **E-9** TRAP 15 task 9 halts directly and never uses EFP_HALT.
Doc-only fix proposed so existing callers keep working (also updates the task 7/8 text for the E-5/E-4 fixes).""",
 repro="—", fix="See branch.", branch='fix/B-12-B-20-E-4-E-5-E-9'),
dict(n=12, ids='D-2, D-3, D-4', title='libs cstdlib: memcpy returns the wrong pointer, memmove/memcmp missing, strtol whitespace/endptr',
 status='D-2 and D-4 (whitespace) confirmed in MAME; D-3 by link inspection.',
 where=[LB+'cstdlib/string.c:41', LB+'cstdlib/stdlib.c:73'],
 body="""- **D-2** `memcpy` returns `dest + n` instead of `dest`; `strncpy` returns memcpy's result and inherits it.
- **D-3** no `memmove`/`memcmp`, which GCC may emit for struct copies/compares even with `-ffreestanding` → link errors.
- **D-4** `strtol` skips only `' '` (so `"\\t42"` → 0, also via atoi/atol); with no digits, `*endptr` must equal `nptr`.""",
 repro="`tests/libtest/` (C program linked against the libs).", fix="See branches.", branch='fix/D-2-B-13, fix/D-3, fix/D-4'),
dict(n=13, ids='D-6, D-11', title='libs: calloc size overflow, realloc(p,0) leak, readline breaks for buffers > 256 bytes',
 status='Confirmed in MAME (calloc(0x10000,0x10001) returned a block; readline with 280 chars into a 300-byte buffer returned 24 and overwrote the start).',
 where=[LB+'shmall/rosco_m68k.cpp:176', LB+'machine/basicio.c:24'],
 body="""- **D-6** `calloc` multiplies without an overflow check; `realloc(ptr, 0)` allocates a new block and never frees `ptr`.
- **D-11** `readline` uses a `uint8_t` index, which wraps at 256; when the buffer fills it returns `buf_size` instead of the stored length.""",
 repro="`tests/libtest/`, `tests/inputtest/` + `mame/input_harness.py` (types into the console over a socket).", fix="See branches.", branch='fix/D-6, fix/D-11'),
dict(n=14, ids='D-8', title='libs printf: %e/%g/%lld disabled but arguments then misalign; %f > 1e9 restarts sprintf output',
 status='Confirmed in MAME: `"%lld|%d"` → `"|0"`, `"%e|%d"` → `"e|1073217536"`, `sprintf(b,"ab%fcd",1e10)` → n=2, b="cd".',
 where=[LB+'printf/include/printf_config.h:19', LB+'printf/printf.c:362'],
 body="""With exponential and long-long support disabled, `%e/%g` are skipped without consuming their argument and `%lld` consumes only a `long`, so every following argument is wrong. For |value| > PRINTF_MAX_FLOAT, `_ftoa` returns 0 – the output *index* – so sprintf restarts at the beginning of the buffer. Enabling exponential output also exposes two upstream `_etoa` issues: 0.0 prints as `0.000000e-308`, and 1e10 as `10.000000e+09`.""",
 repro="`tests/libtest/` (D-8 lines).", fix="Enable both features (+3 KiB softfloat, +1 KiB nofloat), return `idx`, special-case zero and renormalise after rounding in `_etoa`.", branch='fix/D-8'),
dict(n=15, ids='D-7', title='libs: libm.a contains every library\'s objects (incl. the float printf)',
 status='Confirmed: `m68k-elf-ar t libm.a` listed 313 members incl. printf.o, sdfat, vterm, heap, sst_flash, kinit.',
 where=[LB+'libm/include.mk:1'],
 body="""`SOURCES=$(shell find . -name "*.c")` runs from `libs/`, not from the libm directory. Programs linking `-lm` can silently pick up the float `printf_` from libm.a instead of libprintf/libprintf-softfloat. (Related, not changed: `$(filter-out **/printf-*.o, …)` in libs/Makefile is a no-op because filter-out uses `%`; fixing it would drop printf from librosco_m68k.a, so that needs a maintainer decision.)""",
 repro="`m68k-elf-ar t src/libm/libm.a`.", fix="Search only the libm directory (288 math objects); all example programs still build.", branch='fix/D-7'),
dict(n=16, ids='D-1, D-12', title='libs wrappers: e68PrintStrReadNumSigned passes the prompt in D1; vterm cursor left/right swapped',
 status='Both confirmed in MAME.',
 where=[LB+'easy68k/easy68k.S:288', LB+'vterm/vterm.c:74'],
 body="""- **D-1** TRAP 15 task 18 takes the prompt in A1; the wrapper loads it into D1, so whatever A1 points at is printed.
- **D-12** `vt_move_cursor_left` sends `CSI n C` (forward) and `_right` sends `CSI n D`; the four cursor functions also build up to 11 bytes in a 10-byte calloc.""",
 repro="`tests/inputtest/` (D-1), `tests/libtest/` (D-12).", fix="See branches.", branch='fix/D-1, fix/D-12'),
dict(n=17, ids='D-13, D-14', title='libs gdb stub: ring-buffer mask never set; DUART status read from absolute addresses',
 status='By reading; not runtime-tested (no m68k gdb available). Fixes compile.',
 where=[LB+'gdb/gdb-support.c:51', LB+'gdb/interrupt.asm:125 (and the SRB read)'],
 body="""- **D-13** `uart_b.mask` stays 0 (bss), so `duart_buffer_char` always writes `data[0]`: input received while the target runs is lost.
- **D-14** `move.b DUART_SRA,D0` reads absolute address $2 (a reset-vector byte) instead of `DUART_SRA(A0)`; same for SRB. Also noted, not changed: the shared `.error` path resets UART A's overrun even for UART B.""",
 repro="—", fix="Set `mask = sizeof(data) - 1`; use `(A0)`-relative reads.", branch='fix/D-13, fix/D-14'),
dict(n=18, ids='D-17', title='libs sst_flash: no timeout, no interrupt masking and no verify (updateflash can hang or write a bad ROM)',
 status='Confirmed in MAME with the flash-ROM model (rosco-emulator branch feature/sst-flash): programming 0xFF over 0x00 reported success; erase/program with interrupts enabled crashed ("Illegal instruction" from the tick handler). Fixed versions pass, incl. a full updateflash 2.42 -> 2.42.1.',
 where=[LB+'sst_flash/sst.c:31 (wait)', LB+'sst_flash/sst.c (sst_sector_erase, sst_write_byte, sst_get_device_info)'],
 body="""- `wait()` polls DQ6 with no limit, so a missing/protected/failing chip hangs the caller forever (with interrupts masked, in updateflash).
- Nothing masks interrupts inside the library, although the vectors and handlers live in the ROM being programmed: while the chip is busy it returns status bits, so an interrupt executes garbage. updateflash masks itself, other callers may not.
- No verification: a byte that does not program (e.g. its sector was not erased – flash can only clear bits) or a sector that does not erase is reported as success, so a bad ROM image can be written without any error.""",
 repro="`tests/flash/sst_verify_irq_test.c` and `tests/flash/updateflash_harness.py` on the flash-ROM emulator; `tests/sst_timeout_test.c` + `mame/sst_stuck.dbg` for the timeout.",
 fix="Bound the wait (1,000,000 polls ≈ 5 s at 10 MHz); run each command sequence at IPL 7 and restore the caller's mask; read back each programmed byte and check erased sectors are all 0xFF. sst_chip_erase is masked but not verified (device-size dependent).", branch='fix/D-17 (2 commits)'),
dict(n=19, ids='K-1, K-2, K-3, K-4', affects='release v2.42 (ROM kernel built by default) and `develop` @ ec229f9 when built with `WITH_KERNEL=true`', title='ROM kernel (WITH_KERNEL=true): task exit corrupts vector $10, irq_remove leaves IRQs masked, API pointer overwrites SDB magic, warm boot self-chains IRQs',
 status='All four confirmed in MAME on v2.42 (where the kernel is built by default). develop builds without the kernel by default but the code is unchanged. No fix branch.',
 where=[FW+'kernel/sched.c:74', FW+'kernel/kmachine.asm:296', FW+'kernel/include/kernelapi.h:27', FW+'kernel/kmachine.asm:123'],
 body="""- **K-1** `task_done` sets `current_task_var = NULL`, then `task_yield`→`suspend` stores SP at `NULL + TASK_STACK` = **$10** (illegal-instruction vector). Seen: $00E05654 → $00072FAE.
- **K-2** `irq_remove` does `bra list_node_delete`, skipping `enable_interrupts`: SR stays at IPL 7 and the nesting count leaks (seen: SR=$2704, count=1).
- **K-3** `KERNEL_API_ADDRESS` is $400 = SDB_MAGIC, so kernel init overwrites the SDB magic (seen: $400 = $00001DF8 after boot).
- **K-4** Kernel init runs again on every warm boot; the second `irq_init` stores the already-installed handler as `old_irqN`, so each autovector handler chains to itself (seen: old_irq3 = irq_3).
Also by reading: slab allocator issues (K-5, K-6).""",
 repro="`tests/t_k1.asm`, `tests/t_k2.asm`, `tests/t_k4.asm` + `mame/k4_irq_chain.dbg`, `mame/k3_sdb_magic.dbg` (v2.42 default build).", fix="Not proposed; v2.42.1 on the fork simply defaults to NO_KERNEL=true like develop.", branch='—'),
dict(n=20, ids='V-1, V-3, X-1, X-2, X-3', title='Video consoles: V9958 CLRSCR writes through the caller\'s A0; Xosera ANSI erase/NEL bugs',
 status='V-1 confirmed by calling the ROM routine in MAME (RAM at the caller\'s A0 overwritten). V-3 and X-* by reading only (MAME has no V9958/Xosera model). No fix branch.',
 where=[FW+'stage1/video9958/vdpcon.asm:255', FW+'stage1/videoXoseraANSI/xosera_ansiterm_m68k.c:338', FW+'stage1/videoXoseraANSI/xosera_ansiterm_m68k.c:977'],
 body="""- **V-1** `V9958_CON_CLRSCR` calls `BUFFERFLIP` with the *caller's* A0 instead of the VDP port base → ~1.9 KB written to arbitrary memory.
- **V-3** the scroll path does `adda.l D1,A1` after only `move.w CURPOS,D1` → 80-byte clear at an address built from the caller's upper D1.
- **X-1** `xansi_clear(start == end)` computes `count = end - start - 1` = $FFFF → clears all 64K words of VRAM (ESC[K at the last column, ESC[1K at column 0).
- **X-2** EL/ED ranges are off by one (last column / cursor cell not erased).
- **X-3** ESC E (NEL) compares `td->y` with `cols` instead of `rows`.""",
 repro="V-1: call the CLRSCR routine with A0=$2000 over a $AA pattern (`tests/t_misc.asm`, v2.42 address).", fix="Not proposed (no hardware to test on).", branch='—'),
dict(n=21, ids='U-1', affects='`develop` @ ec229f9 only (not v2.42)', title='develop: `make MAME=true` fails with -Werror=unused-label in stage2/main2.c',
 status='Confirmed by building develop @ ec229f9 with the roscopeco/rosco_m68k image (m68k-elf-rosco-gcc 13.3.1).',
 where=[FW+'stage2/main2.c:228'],
 body="""```
main2.c:228:1: error: label 'have_kernel' defined but not used [-Werror=unused-label]
```
In the MAME configuration the SD/IDE loaders that jump to `have_kernel` are compiled out, so the label is unused.""",
 repro="`make MAME=true BOARD_ROM_SIZE=256KB all` in code/firmware/rosco_m68k_firmware.", fix="Guard the label with the same `#if` as its users, or mark it `__attribute__((unused))`.", branch='—'),
]
idx = ['# Draft upstream issues (M11)', '',
 f'_Drafted 2026-10-30 for the upstream rosco_m68k project; not filed. Each file is one issue: copy the title and body. Fix branches are on the fork `{FORK}` (push them first if you reference them)._', '',
 'Only findings still present on `develop` @ ec229f9 are included. Already fixed on develop, so no issue: B-7, A-3, A-5, A-8, A-10, A-11, A-13, B-17, B-19/B-21, X-10, S-2/D-16, D-9, D-15.', '',
 '| # | Findings | Title | Status | Fix branch |', '|---|----------|-------|--------|------------|']
for i in issues:
    fn = f"{i['n']:02d}-{i['ids'].split(',')[0].strip()}.md"
    where = '\n'.join(f'- `{w}`' for w in i['where'])
    txt = f"""# {i['title']}

{HDR.format(tests=TESTS, affects=i.get('affects', 'release v2.42 and `develop` @ ec229f9 (r2.x, default build)'))}**Status:** {i['status']}
**Review IDs:** {i['ids']}

## Description
{i['body']}

## Where (develop @ ec229f9)
{where}

## How to reproduce
{i['repro']}

## Proposed fix
{i['fix']}
Branch: `{i['branch']}` on {FORK}
"""
    open(os.path.join(OUT, fn), 'w').write(txt)
    short = re.split(r'[:;(]| by | with ', i['status'])[0].strip().rstrip('.')
    idx.append(f"| {i['n']} | {i['ids']} | [{i['title']}]({fn}) | {short} | `{i['branch']}` |")
open(os.path.join(OUT, 'README.md'), 'w').write('\n'.join(idx) + '\n')
print(len(issues), 'issues written')
