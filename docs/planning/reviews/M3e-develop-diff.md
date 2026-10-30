# M3e — changes on develop since v2.42 that affect r2.x / 1M

_Source: review agent, 2026-10-30. Static diff reading only; "(inferred)" = symptom deduced from code, not observed._

## Context
- v2.42 = single-image firmware (1M ROM @ 0xE00000, no ROMFS, no boot menu).
- develop = two-stage firmware (stage1 ROM + stage2 @ 0xC0000), littlefs ROMFS @ ROM+0x30000, Xosera splash/boot menu. Banner "2.50.DEV", **no release tag** → moving snapshot.
- Upgrading = full ROM reflash, not a patch.

## Fixes you are missing (ranked)
| # | Commit | Area | Symptom on v2.42 | Applies when |
|---|--------|------|------------------|--------------|
| 1 | 44c9b5a | Xosera probe bus-error continuation (BERR_CONT_ADDR) | possible hang/crash at boot (inferred) | 68000 CPU |
| 2 | 478bac2 | `spi_read_buffer` red LED writes wrong DUART regs | LED stays lit after SD read; stray DUART register write (inferred) | r2.x + SD |
| 3 | 1468b51 | CPU type detection (stale D0, unimpl-integer vector) | wrong CPU model/speed in SDB_CPUINFO & banner (inferred) | all |
| 4 | c899e46 | debug trap handler writes below SP; 020+ fault address | crash dump corrupted by interrupt; wrong fault addr on 020+ | all (+ lib rebuild) |
| 5 | c8ec0ba | keyboard reset/mode on detect | keyboard not detected / wrong mode after warm boot (inferred) | commercial keyboard |
| 6 | eee509e/575a6fd | DUART LED/SD code ignores SYSFLAGS | LEDs blink even when program disabled them | programs clearing SYSFLAGS |
| 7 | a1961a0 | exit()/abort() via EFP_PROG_EXIT, runs dtors | improper cleanup on exit (inferred) | user programs (rebuild) |
| 8 | 44574b3/5162251/cdacb0e | XANSI hooks INPUTCHAR/CHECKINPUT; cursor | missing cursor, keyboard not usable via Xosera console | Xosera fitted |
| 9 | 2b18fb2 | gdb stub `(a7)-` typo | gdb stub broken | GDB users |
| 10 | 374009a | dummy PRINT/PRINTLN don't advance A0; INITDEVS size | API contract violation | minor |
| 11 | 849bc81 | NOP between memsize write/read | memory sizing on 020+ | 020+ only |

Quality-of-life: 2f00678 (wait for key after crash dump), 19c79d9/1ecc922 (skip splash, `k` → kermit), 44fb181 (020+ caches).

Not relevant to r2.x/1M on real HW: 662ca47 (MAME 030), a1a8d0e (MFP/r1), 441044a (MAME/non-HUGEROM), c404e38 & e2cec65 (regressions introduced after v2.42).

## Breaking / compatibility when upgrading
- Full reflash: new layout, ROMFS image must match (#478 moved ROMFS 0x26000→0x30000, 720K→640K; don't reuse older ROMFS images).
- Toolchain: needs `m68k-elf-rosco-*`, submodules, mklittlefs (#454, 7dc8256).
- Xosera base moved SDB $410 → VDB $117C (a8dd940); $410 still written as a "temporary" shim. Old Easy68k flag bytes at $410–$413 now reserved.
- GPIO lib + demos removed (60c5649).
- f54f73e: new r2 GALs keep flash mapped low until firmware exits boot mode → **v2.42 firmware on new GALs would not leave boot mode (inferred). Reflash firmware before/with any GAL update.**
- Rebuild user programs to pick up lib fixes (exit, debug_stub, gdb, INPUTCHAR EFPs).

## Risk notes on develop
- f14e03c merged with "WIP" title; churn around VDB extern (a8dd940/cfe26c8/69165c3).
- 7dc8256 is a 4000+ line squash; two post-reorg regressions already found (e2cec65, c404e38) → newer paths (splash, XoseRAM autodetect, boot menu) less tested.
- Tools/branches may still assume ROMFS @0x26000 or 360/720 names.
