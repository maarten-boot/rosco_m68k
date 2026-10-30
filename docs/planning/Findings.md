# Findings — rosco_m68k firmware v2.42 review

_Consolidated 2026-10-30 from the five area reports in `reviews/`. Static review only — nothing built or run._
_Target: r2.x board (68010), 1M HUGEROM, default build options. The ROM kernel, V9958 console, Xosera ANSI console **and the firmware debug_stub** are all included (`WITH_DEBUG_STUB?=true`; the earlier note saying debug_stub was excluded was wrong, corrected 2026-10-30)._

## Runtime verification (M7/M8, 2026-10-30)
- **Build:** v2.42 rebuilt from source in the `roscopeco/rosco_m68k` image. The ROM is bit-identical to the emulator's `-bios v242` (SHA1 6ff2a658…, CRC32 86950afb).
- **Confirmed (★) in MAME or from build artefacts:** K-3, K-2, B-7, B-1, A-1, A-3, A-4, A-12, E-1, E-2, E-4, D-7.
- **M8b (2026-10-30), also confirmed:** K-1, K-4, E-6, V-1 (ROM routine called directly), D-2, D-6, D-8, D-12.
- **M8b, partly confirmed:**
  - E-3: the code bug is real, but the symptom is masked because "on" stores $10 from the SSP vector.
  - B-4: init wrongly reports OK, but stage2 ignores the card and does not crash.
  - D-4: tab whitespace is not skipped, but `endptr` is correct for "abc".
- **M8b, not reproduced:** D-5 (heap free of the last block). It stays open at low confidence.
- **Not testable in this MAME build:** X-* (no Xosera), V-3 (no V9958), B-2 (no host Kermit), B-6 (slow SD cards).
- **Pending-test round (2026-10-30), confirmed:** A-2, B-8 (on an ATA-enabled test build), B-17, D-1, D-11.
- **Pending-test round, not reproduced:** A-9 is latent (needs a compressed stage2 of 64 KiB or more).
- **Pending-test round, not testable:** D-13 (no m68k gdb on the host).
- **NEW B-19 (found during M8, confirmed):** in the v2.42 release build, `ROSCO_M68K_ATA` is passed only to the C compiler (`EXTRA_CFLAGS` in `blockdev/include.mk`), never to vasm. So `blockdev/syscalls_asm.asm` assembles FW_ATA_INIT/READ/WRITE/IDENT as stubs (`moveq #1,d0` / `moveq #0,d0`). **IDE boot can never work, and TRAP 13 ATA calls always fail**, although the boot banner lists the drive. Fixed on develop by d375bc2 (`DEFINES+=-DROSCO_M68K_ATA`).
- **Totals:** 28 confirmed. Partly confirmed: E-3, B-4, D-4. Not reproduced: D-5, A-9. Not testable here: X-*, V-3, B-2, B-6, D-13.
- **B-1 is worse than reported:** the crash triggers warm boot, which reloads the same file, so the board is stuck in a **crash/reboot loop** until the SD card is removed.
- **A-3 refined:** the copy source `_code_end` points at the CODE section (ATA routine), not at the .data load address. In this build the only initialised .data variable is `ata.c:selected_drive`, which gets $20 instead of $FF. That is harmless today (the first drive select still happens) but latent.
- **K-3 timing:** the magic is overwritten at about 3.65 s of emulated boot, when the kernel initialises. Boot is slow mainly because of the IDE probe timeouts (B-10).
- **A-19 corrected:** crashes do produce a register dump, because debug_stub is in the default build. S-1 and S-2 apply to the user's ROM.

## Legend
- **ID prefixes:** A = core/stage1, B = stage2/blockdev, K = kernel, E = EASy68K, V = V9958, X = Xosera ANSI, S = firmware debug_stub, D = user libraries. Full details, evidence and file:line are in `reviews/M3*.md`.
- **★** = confirmed at runtime in MAME or from build artefacts (M7/M8).
- **✔** = verified against the v2.42 source by the main session (14 items). Other items are agent-reported with the stated confidence and still need verification (see Tests.md).
- **Dev** = fixed on `develop`? (yes / partial / no).

## Counts
| Area | Findings | High | Medium | Fixed on develop |
|------|----------|------|--------|------------------|
| A core/stage1 | 21 | 0 | 6 | 7 |
| B stage2/blockdev | 18 | 0 | 8 | 1 |
| K/E/V/X/S kernel, EASy68K, video, debug_stub | 34 | 6 | 19 | 2 |
| D user libs | 18 | 0 | 8 | 3 (+2 partial) |
| **Total** | **91** (≈88 unique) | **6** | **41** | |

Duplicates merged below: A-2 = B-14 (signed division); K-3 = part of D-18 (KERNEL_API 0x400); B-7 = develop 478bac2; S-2 ≈ D-16 (same bug in firmware and lib copies).

## Priority list (what matters most on your board)

### P1 — memory/hardware corruption in the default build
| # | ID | Finding | Dev |
|---|----|---------|-----|
| 1 | K-3 ✔★ | ROM kernel init writes its API pointer to **0x400 = SDB_MAGIC**, so the SDB magic is overwritten at every boot | no |
| 2 | K-1 ✔★ | A ROM-kernel task that returns writes SP to **$10 (illegal-instruction vector)** | no |
| 3 | B-7 ✔★ | Every SD buffer read writes **DUART OPCR** and leaves the red LED on | yes |
| 4 | A-3 ✔★ | `.data` initialisers are copied from the wrong ROM offset (`.early_data` in front of `_data_start`). Impact depends on what lives in .data, so it needs a link map | yes |
| 5 | V-1 ★ / V-3 | V9958 console: CLRSCR blits about 1.9 KB to the caller's A0; scrolling zeroes 80 bytes at an address built from a dirty D1 | no |
| 6 | X-1 | Xosera ANSI: ESC[K at the last column or ESC[1K at column 0 clears **all 64K VRAM** | no |
| 7 | K-4 ★ | Kernel is re-initialised on every warm boot, chaining IRQ vectors to themselves → recursion on any autovector IRQ | no |
| 8 | K-2 ✔★ | `irq_remove` leaves interrupts masked | no |

### P2 — crashes and wrong results through public APIs
| # | ID | Finding | Dev |
|---|----|---------|-----|
| 9 | E-1 ✔★ | TRAP #15 task number > 20 → unbalanced stack, crash | no |
| 10 | E-2 ★ | EASy68K prints nothing for 0 (tasks 3, 17, 20) | no |
| 11 | E-3 ✔ (symptom masked) | EASy68K task 16 can never turn prompt/LF back on | no |
| 12 | A-1 ✔★ | TRAP 14 DEVICE_CTRL always writes $40 to the baud register (uses D1 = 64, not D2) | no |
| 13 | A-2 ★/B-14 | `__divsi3`/`__modsi3` are unsigned, so signed division is wrong for negative operands | no |
| 14 | D-1 ✔★ | libs `e68PrintStrReadNumSigned` passes the string pointer in D1, but A1 is required | no |
| 15 | D-5 (not reproduced) | shmall: freeing the last heap block reads past the heap end → heap corruption | no |
| 16 | D-8 ★ | printf: `%f` > 1e9 resets the output index; `%lld` and `%e/%g` misalign arguments | no |
| 17 | D-2 ★ | libs `memcpy` returns the end pointer | no |
| 18 | E-4 ★ / E-6 ★ | EASy68K task 8 returns the heartbeat counter; task 11 cursor is off by one | no |

### P3 — storage and loaders (data integrity)
| # | ID | Finding | Dev |
|---|----|---------|-----|
| 18a | **B-19** ★ (new) | **IDE boot and TRAP 13 ATA calls are dead in the v2.42 release build**: the asm EFP entry points are built as stubs because the ATA define never reaches vasm | yes (d375bc2) |
| 19 | B-4 ✔ (partly ★, benign) | SD init reports OK when CMD58 fails, with an uninitialised card struct | no |
| 20 | B-5 / B-9 | SD and ATA writes don't check the result; no ATA cache flush | no |
| 21 | B-8 ★ | ATA is LBA28 only: >128 GiB addresses wrap and **write to the wrong sector** | no |
| 22 | B-1 ✔★ / B-2 | BIN loader and Kermit receive have no RAM bound (can overwrite stage2, stack and SDB) | no |
| 23 | B-6 | SD timeouts are probably shorter than the spec (slow cards fail) | no |
| 24 | D-17 | sst_flash: no wait timeout, no verify (risk while updating flash) | no |

### P4 — build and integration
| # | ID | Finding | Dev |
|---|----|---------|-----|
| 25 | D-7 ✔★ | `libm.a` contains every lib object, including float printf, so `-lm` can override your printf choice | no |
| 26 | D-3 | no memmove/memcmp etc. → link errors when GCC emits them | no |
| 27 | A-20 | firmware Makefile: stage2 rebuild not triggered by source changes; no header deps | restructured |

### P5 — missing features (r2.x)
- **Storage:** no exFAT (out-of-box SDXC >32 GB), GPT, extended partitions, FAT12 or LBA48 (B-8, B-16).
- **EASy68K:** keyboard input ignored; task 7 is a stub on r2.x; many tasks unimplemented (E-5, E-7).
- **V9958 console:** no ANSI escape handling, no MOVEXY (V-5).
- **Xosera:** query replies and cursor blink are missing on the keyboard input path (X-10, fixed on develop).
- **Kernel:** no pending-signal latch (K-7); PMM gets no RAM (K-9g).
- **Firmware stubs:** SET_INTR, ENABLE/DISABLE_XMIT/RECV on r2.x (A-16). The crash dump depends on debug_stub, which is included by default (A-19).
- **Doc/API mismatches:** SPI_INIT return value (B-12); PRINT/PRINTLN trash D0 (A-12 ★); CSI ?20h (X-6); machine.h macros and comments (A-16, D-18).

## Upgrade decision (from M3e)
- **Fixed on develop:** B-7, A-3, A-5, A-8, A-10, A-11, A-13, X-10, S-2/D-16, D-9, D-15, plus keyboard/LED/exit fixes. See `reviews/M3e-develop-diff.md`.
- **Not fixed on develop:** all of P1 except B-7 and A-3, and almost all of P2/P3. Upgrading alone does not resolve the main findings.
- **Cost of upgrading:** develop is untagged (2.50.DEV) and needs a full reflash, a new toolchain and a new ROMFS image; Xosera base moves to the VDB.

## R-3 interface conformance (2026-10-30)
Full table: `reviews/R3-interface-table.md`. It has 117 rows: 56 match, 11 match except for the A0 clobber, 32 partial, 10 mismatch, 8 stub (all ATA), 0 missing, and 14 undocumented items.

New findings from R-3 (✔ = checked in source by the main session):
| ID | Finding | Sev | Dev |
|----|---------|-----|-----|
| E-8 ✔ | TRAP #15 trashes A0 on every task (`move.l JUMPTABLE(PC,D0),A0`, never restored); the doc says all other registers are preserved | medium | no |
| B-20 | TRAP #13 trashes A0 on every function, including CHECK_* (FC 0, 5, 15); the doc lists only D0 | low | no |
| B-21 | CHECK_ATA_SUPPORT returns the success magic while all four ATA entries are stubs (makes B-19 silent) | high (with B-19) | yes (d375bc2) |
| E-5 ✔ (upgraded) | TRAP #15 task 7 always returns 0 on r2.x (the ROM contains only `move.b #0,D1`) | high | no |
| E-9 | TRAP #15 task 9 jumps to HALT directly; EFP_HALT is never used | low | no |
| D-19 | libs `e68GetTicks` leaves the upper word of the result undefined (combines with E-4) | low | no |
| D-20 | User libs have no wrappers for TRAP #13 SPI/ATA/CHECK_*; link scripts lack `_EFP_*` for $490/$494/$498 and a symbol for $40A | low | partial |
| A-22 | Doc text for SPI chip-select pins and SDB flag bits 14-10 ("MUST BE 1 for SPI/SD") describes r1.x/MFP behaviour; nothing in the r2.x build enforces them | doc | partial |

Refinements: A-12 (PRINT/PRINTLN trash D0) happens only on the serial console; the V9958 and Xosera consoles preserve D0. E-6 is a 0-based doc against 1-based ANSI addressing, not a loop bug.

## Corrections and new items (M10, 2026-10-30)
- **B-17 is already fixed on develop.** Its load.c refuses 0-byte kernels ("SEVERE: Loaded 0 bytes") and checks the `fl_attach_media()` result; the M3b report had said "unknown". No develop port is needed.
- **U-1 (new, develop only):** `make MAME=true` on develop fails with `main2.c:228: label 'have_kernel' defined but not used [-Werror=unused-label]`. Upstream issue candidate.
- **Develop ports:** 30 branches off develop: fix/A-1 fix/A-12 fix/A-2-B-14 fix/A-4 fix/A-9 fix/B-1 fix/B-12-B-20-E-4-E-5-E-9 fix/B-2 fix/B-3 fix/B-4 fix/B-5 fix/B-6 fix/D-1 fix/D-11 fix/D-12 fix/D-13 fix/D-14 fix/D-17 fix/D-2-B-13 fix/D-3 fix/D-4 fix/D-6 fix/D-7 fix/D-8 fix/E-1-E-8 fix/E-2 fix/E-3 fix/E-4 fix/E-5 fix/E-6 . B-6 is based on fix/B-5. The A-2 port touches only stage1/common.c, and the D-2 port only the libs (develop has no stage-local memcpy). B-1/B-3 use `FW_PRINT_C` (develop renamed mcPrint).

## Emulator findings (M12, rosco-emulator)
- **EMU-1 (fixed in 55c081e):** MAME `intelfsh` returned array data instead of the toggling erase status for reads more than 64K away from the erasing sector. For SST39SF0x0 the datasheet says DQ6 toggles at any address. Effect: flash tools polling the chip base saw an instant "done" and lost writes.
- **EMU-2 (fixed in bdcfddc):** the rosco_m68k driver ignored the CPU's RESET output, so the DUART was not reset by the RESET instruction. Effect: updateflash's reboot into new firmware hung in the CPU-speed calibration.
- **EMU-3 (by design, documented):** the ROM was previously read-only; it is now persistent flash NVRAM, seeded from `-bios` only when blank.
