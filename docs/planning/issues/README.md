# Draft upstream issues (M11)

_Drafted 2026-10-30 for the upstream rosco_m68k project; not filed. Each file is one issue: copy the title and body. Fix branches are on the fork `maarten-boot/rosco_m68k` (push them first if you reference them)._

Only findings still present on `develop` @ ec229f9 are included. Already fixed on develop, so no issue: B-7, A-3, A-5, A-8, A-10, A-11, A-13, B-17, B-19/B-21, X-10, S-2/D-16, D-9, D-15.

| # | Findings | Title | Status | Fix branch |
|---|----------|-------|--------|------------|
| 1 | A-1 | [TRAP 14 DEVICE_CTRL ignores the parameter in D2 and always writes $40 to the DUART CSR](01-A-1.md) | Confirmed in MAME | `fix/A-1` |
| 2 | A-12 | [Serial PRINT/PRINTLN (TRAP 14 fn 0/1) clobber D0 although documented to modify only A0](02-A-12.md) | Confirmed in MAME on v2.42 and on develop | `fix/A-12` |
| 3 | A-2, B-14 | [`__divsi3`/`__modsi3` in the firmware are unsigned, so signed division is wrong](03-A-2.md) | Confirmed in MAME | `fix/A-2-B-14` |
| 4 | A-4, A-9 | [Two stage1 assembler slips: `or.w #0700,SR` (decimal) and word-sized decompress return](04-A-4.md) | A-4 confirmed in the assembled ROM | `fix/A-4 and fix/A-9` |
| 5 | E-1, E-2, E-3, E-4, E-5, E-6, E-8 | [EASy68K TRAP 15 layer: crash on unknown task, A0 clobbered, several tasks return wrong results](05-E-1.md) | All confirmed in MAME on v2.42 | `fix/E-1-E-8, fix/E-2, fix/E-3, fix/E-4, fix/E-5, fix/E-6` |
| 6 | B-1, B-2, B-3 | [stage2 loaders do not bound kernel loads: oversized ROSCODE1.BIN causes a crash/reboot loop](06-B-1.md) | B-1 confirmed in MAME | `fix/B-1, fix/B-2, fix/B-3` |
| 7 | B-4 | [SD init reports success when CMD58 (read OCR) fails, leaving the card struct uninitialised](07-B-4.md) | Confirmed in MAME | `fix/B-4` |
| 8 | B-5 | [SD block write ignores the data-response token: rejected writes are reported as success](08-B-5.md) | Confirmed in MAME | `fix/B-5` |
| 9 | B-6 | [SD timeouts are poll counts, far shorter than the SD spec on the bit-banged SPI](09-B-6.md) | Confirmed in MAME | `fix/B-6` |
| 10 | B-8, B-9 | [ATA: LBA28 only (addresses ≥ 2^28 silently wrap) and writes are not completed/checked](10-B-8.md) | B-8 confirmed in MAME on a v2.42 build | `— (not yet)` |
| 11 | B-12, B-20, E-9 | [InterfaceReference.md does not match TRAP 13 / TRAP 15 behaviour](11-B-12.md) | Confirmed | `fix/B-12-B-20-E-4-E-5-E-9` |
| 12 | D-2, D-3, D-4 | [libs cstdlib: memcpy returns the wrong pointer, memmove/memcmp missing, strtol whitespace/endptr](12-D-2.md) | D-2 and D-4 | `fix/D-2-B-13, fix/D-3, fix/D-4` |
| 13 | D-6, D-11 | [libs: calloc size overflow, realloc(p,0) leak, readline breaks for buffers > 256 bytes](13-D-6.md) | Confirmed in MAME | `fix/D-6, fix/D-11` |
| 14 | D-8 | [libs printf: %e/%g/%lld disabled but arguments then misalign; %f > 1e9 restarts sprintf output](14-D-8.md) | Confirmed in MAME | `fix/D-8` |
| 15 | D-7 | [libs: libm.a contains every library's objects (incl. the float printf)](15-D-7.md) | Confirmed | `fix/D-7` |
| 16 | D-1, D-12 | [libs wrappers: e68PrintStrReadNumSigned passes the prompt in D1; vterm cursor left/right swapped](16-D-1.md) | Both confirmed in MAME | `fix/D-1, fix/D-12` |
| 17 | D-13, D-14 | [libs gdb stub: ring-buffer mask never set; DUART status read from absolute addresses](17-D-13.md) | By reading | `fix/D-13, fix/D-14` |
| 18 | D-17 | [libs sst_flash: no timeout, no interrupt masking and no verify (updateflash can hang or write a bad ROM)](18-D-17.md) | Confirmed in MAME | `fix/D-17 (2 commits)` |
| 19 | K-1, K-2, K-3, K-4 | [ROM kernel (WITH_KERNEL=true): task exit corrupts vector $10, irq_remove leaves IRQs masked, API pointer overwrites SDB magic, warm boot self-chains IRQs](19-K-1.md) | All four confirmed in MAME on v2.42 | `—` |
| 20 | V-1, V-3, X-1, X-2, X-3 | [Video consoles: V9958 CLRSCR writes through the caller's A0; Xosera ANSI erase/NEL bugs](20-V-1.md) | V-1 confirmed | `—` |
| 21 | U-1 | [develop: `make MAME=true` fails with -Werror=unused-label in stage2/main2.c](21-U-1.md) | Confirmed | `—` |
