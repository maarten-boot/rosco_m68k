# Findings — rosco_m68k firmware v2.42 review

_Consolidated 2026-10-30 from the five area reports in `reviews/`. Static review only — nothing built or run._
_Target: r2.x board (68010), 1M HUGEROM, default build options (ROM kernel, V9958 and Xosera ANSI console included; firmware debug_stub excluded)._

## Legend
- **ID prefixes:** A = core/stage1, B = stage2/blockdev, K = kernel, E = EASy68K, V = V9958, X = Xosera ANSI, S = firmware debug_stub, D = user libraries. Full details, evidence and file:line are in `reviews/M3*.md`.
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
| 1 | K-3 ✔ | ROM kernel init writes its API pointer to **0x400 = SDB_MAGIC**, so the SDB magic is overwritten at every boot | no |
| 2 | K-1 ✔ | A ROM-kernel task that returns writes SP to **$10 (illegal-instruction vector)** | no |
| 3 | B-7 ✔ | Every SD buffer read writes **DUART OPCR** and leaves the red LED on | yes |
| 4 | A-3 ✔ | `.data` initialisers are copied from the wrong ROM offset (`.early_data` in front of `_data_start`). Impact depends on what lives in .data, so it needs a link map | yes |
| 5 | V-1 / V-3 | V9958 console: CLRSCR blits about 1.9 KB to the caller's A0; scrolling zeroes 80 bytes at an address built from a dirty D1 | no |
| 6 | X-1 | Xosera ANSI: ESC[K at the last column or ESC[1K at column 0 clears **all 64K VRAM** | no |
| 7 | K-4 | Kernel is re-initialised on every warm boot, chaining IRQ vectors to themselves → recursion on any autovector IRQ | no |
| 8 | K-2 ✔ | `irq_remove` leaves interrupts masked | no |

### P2 — crashes and wrong results through public APIs
| # | ID | Finding | Dev |
|---|----|---------|-----|
| 9 | E-1 ✔ | TRAP #15 task number > 20 → unbalanced stack, crash | no |
| 10 | E-2 | EASy68K prints nothing for 0 (tasks 3, 17, 20) | no |
| 11 | E-3 ✔ | EASy68K task 16 can never turn prompt/LF back on | no |
| 12 | A-1 ✔ | TRAP 14 DEVICE_CTRL always writes $40 to the baud register (uses D1 = 64, not D2) | no |
| 13 | A-2/B-14 | `__divsi3`/`__modsi3` are unsigned, so signed division is wrong for negative operands | no |
| 14 | D-1 ✔ | libs `e68PrintStrReadNumSigned` passes the string pointer in D1, but A1 is required | no |
| 15 | D-5 | shmall: freeing the last heap block reads past the heap end → heap corruption | no |
| 16 | D-8 | printf: `%f` > 1e9 resets the output index; `%lld` and `%e/%g` misalign arguments | no |
| 17 | D-2 | libs `memcpy` returns the end pointer | no |
| 18 | E-4 / E-6 | EASy68K task 8 returns the heartbeat counter; task 11 cursor is off by one | no |

### P3 — storage and loaders (data integrity)
| # | ID | Finding | Dev |
|---|----|---------|-----|
| 19 | B-4 ✔ | SD init reports OK when CMD58 fails, with an uninitialised card struct | no |
| 20 | B-5 / B-9 | SD and ATA writes don't check the result; no ATA cache flush | no |
| 21 | B-8 | ATA is LBA28 only: >128 GiB addresses wrap and **write to the wrong sector** | no |
| 22 | B-1 ✔ / B-2 | BIN loader and Kermit receive have no RAM bound (can overwrite stage2, stack and SDB) | no |
| 23 | B-6 | SD timeouts are probably shorter than the spec (slow cards fail) | no |
| 24 | D-17 | sst_flash: no wait timeout, no verify (risk while updating flash) | no |

### P4 — build and integration
| # | ID | Finding | Dev |
|---|----|---------|-----|
| 25 | D-7 ✔ | `libm.a` contains every lib object, including float printf, so `-lm` can override your printf choice | no |
| 26 | D-3 | no memmove/memcmp etc. → link errors when GCC emits them | no |
| 27 | A-20 | firmware Makefile: stage2 rebuild not triggered by source changes; no header deps | restructured |

### P5 — missing features (r2.x)
- **Storage:** no exFAT (out-of-box SDXC >32 GB), GPT, extended partitions, FAT12 or LBA48 (B-8, B-16).
- **EASy68K:** keyboard input ignored; task 7 is a stub on r2.x; many tasks unimplemented (E-5, E-7).
- **V9958 console:** no ANSI escape handling, no MOVEXY (V-5).
- **Xosera:** query replies and cursor blink are missing on the keyboard input path (X-10, fixed on develop).
- **Kernel:** no pending-signal latch (K-7); PMM gets no RAM (K-9g).
- **Firmware stubs:** SET_INTR, ENABLE/DISABLE_XMIT/RECV on r2.x; no crash dump without debug_stub (A-16, A-19).
- **Doc/API mismatches:** SPI_INIT return value (B-12); PRINT/PRINTLN trash D0 (A-12); CSI ?20h (X-6); machine.h macros and comments (A-16, D-18).

## Upgrade decision (from M3e)
- **Fixed on develop:** B-7, A-3, A-5, A-8, A-10, A-11, A-13, X-10, S-2/D-16, D-9, D-15, plus keyboard/LED/exit fixes. See `reviews/M3e-develop-diff.md`.
- **Not fixed on develop:** all of P1 except B-7 and A-3, and almost all of P2/P3. Upgrading alone does not resolve the main findings.
- **Cost of upgrading:** develop is untagged (2.50.DEV) and needs a full reflash, a new toolchain and a new ROMFS image; Xosera base moves to the VDB.
