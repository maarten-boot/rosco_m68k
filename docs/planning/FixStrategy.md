# Fix strategy — rosco_m68k v2.42 findings (M9)

_2026-10-30. No fixes have been made yet._

## 0. Decisions (user, 2026-10-30)
| # | Decision |
|---|----------|
| D1 | **Option C:** branch `maint/2.42` (from tag v2.42) for the board; each new fix is also ported to `fix/<ID>` off `develop` |
| D2 | **No extra hardware** (no V9958, Xosera, IDE or keyboard); 4 MB RAM upgrade (5 MB total, assumed). V-*, X-*, B-8/B-9 and c8ec0ba are deferred for maint; they are still reported upstream |
| D3 | **CPU MC68010; build with `NO_KERNEL=true`.** Only `software/kernel_test` uses the ROM kernel API, so K-* is deferred |
| D4 | **Upstream: draft issue texts** (one per confirmed finding, with repro). The user files them; no PR branches are pushed by Claude |
| Use case | Standalone board running Kermit-loaded or SD-loaded (ROSCODE1.BIN) programs. **Later minix2 will use the ROM SD/bit-banged-SPI code (TRAP 13)**, so B-4, B-5, B-6, B-7, B-12 and B-20 move up |

Consequences:
- The 68000-only backport 44c9b5a is optional.
- 1468b51 (CPU detection) still matters for correct 68010 reporting.
- Kernel rows (K-*) move to "Defer"; T-K3 becomes the regression test showing the magic stays intact with NO_KERNEL=true.
- **For minix2 (TRAP 13 SD path):**
  - **Batch 2:** B-4 (CMD58 result), B-12 (SPI_INIT return convention, doc or code), B-20 (TRAP 13 A0 clobber: preserve A0 or document it).
  - **Batch 3, promoted:** B-5 (SD write response token) and B-6 (time-based SD timeouts). Minix writes to the card, unlike the read-only stage2 loader.

## 1. Strategic options
| Option | What | Pros | Cons |
|--------|------|------|------|
| A | Upgrade the board to `develop` (2.50.DEV) | gets ~11 fixes for free (B-7, A-3, A-5, A-8, A-10, A-11, A-13, B-19/B-21, X-10, S-2/D-16, D-9, D-15); ROM kernel off by default | untagged moving snapshot; full reflash, new toolchain and ROMFS; **most P1–P3 findings are still present** (B-1, B-8, E-*, A-1, A-2, V-*, X-*, D-*) |
| B | v2.42 maintenance branch only (`maint/2.42` from tag `v2.42`, released as e.g. 2.42.1) | small, controlled changes on the firmware you run; every fix verifiable with the existing MAME tests | fixes don't reach develop; diverges further |
| **C (recommended)** | **B for your board + each new fix also prepared for `develop`** | your board gets fixed now; the fixes are reusable upstream; the tests in `tests/` serve as regression tests on both lines | about twice the porting work (develop moved files to `stage1/`, and `common.c` changed) |

Chosen: **C** (D1).

## 2. Batches (proposed order for option B/C)
Effort: S = under 1 h, M = a few hours, L = a day or more. "Verify" = test ID in Tests.md, re-run after the fix. A test that now FAILs must PASS afterwards.

### Batch 0 — build configuration only (no code changes) — **done 2026-10-30** (29a2b69, d14d648)
| ID(s) | Action | Target | Effort | Verify |
|-------|--------|--------|--------|--------|
| B-19, B-21 | Add `DEFINES:=$(DEFINES) -DROSCO_M68K_ATA` to `blockdev/include.mk` (the 1-line part of develop's d375bc2) | maint | S | T-B19 |
| K-1…K-9 (incl. K-3 SDB magic) | Build with `NO_KERNEL=true`, as develop already does by default. Only if no program of yours uses the ROM kernel API at $400; the user libs ship no kernel lib (`-lkernel` is empty, D-18) | maint | S | T-K3 (magic intact), T-K4 |
| V-*, X-* | If the hardware is not fitted, build with `WITH_VDP=false` / `XOSERA_ANSI_CON=false` (only reduces exposure; the code is inactive without the hardware anyway) | maint | S | — |

D3 decided: NO_KERNEL=true on a 68010. D2 (fitted hardware) is still open.

### Batch 1 — backports from develop (small and already reviewed upstream) — **done 2026-10-30**, except 44c9b5a (68000 only, optional), c8ec0ba (keyboard, D2 open) and f54f73e (GALs)
| ID | Develop commit | Notes | Effort | Verify |
|----|----------------|-------|--------|--------|
| B-7 | 478bac2 | SPI read LED/OPCR registers | S | T-B7 |
| A-3 | e2cec65 (linker part only) | `.early_data` out of `.data`; use `_data_load_start` | S | T-A3 (map) |
| A-8 | 1468b51 (+ 662ca47 only if MAME 030 matters) | CPU type detection | S | banner / SDB_CPUINFO on 000/010/020 |
| A-5 | 849bc81 | NOP after INITMEMCOUNT (020+) | S | RAM size on rosco_m68k_020 |
| A-10 | heartbeat bit from 7dc8256 (extract the 2 lines only) | SYSFLAGS bit | S | static |
| S-2, D-16 | c899e46 | debug_stub frame formats, firmware and lib copy | S | crash on 020 → correct fault address |
| D-15 | 2b18fb2 | gdb stub `-(a7)` | S | assembles |
| — | 44c9b5a | BERR_CONT_ADDR in the Xosera probe (68000 boards) | S | boot rosco_m68k_000 |
| — | c8ec0ba | keyboard reset/mode (only if you use the keyboard) | S | hardware |
| A-13 | f54f73e | only together with the new r2 GALs; **skip unless the GALs change** | S | hardware |

### Batch 2 — new small fixes (not fixed anywhere yet) — **done on maint/2.42 2026-10-30**, except V-1/V-3 and X-* (hardware not fitted, D2), which are deferred for maint and kept for upstream issues. A-12 was fixed in code (serial PRINT preserves D0) rather than in the doc. B-12, B-20 and E-9 were fixed in the doc
| ID | Fix | Effort | Verify |
|----|-----|--------|--------|
| A-1 | DUART D_CTRL: take the parameter from D2 (as documented), not D1 | S | T-A1 |
| A-4 | `or.w #$0700,SR` in rev2.asm (and rev1.asm) | S | T-A4 |
| A-2/B-14 | real signed `__divsi3`/`__modsi3` (wrap unsigned divmod with sign handling); stage1 + stage2 | S | T-A2 |
| A-9 | `move.l D2,D0` in decompress.asm (latent, but a 1-char fix) | S | T-A9 |
| E-1 | pop the saved D0 before `rte` on an out-of-range task; compare D0.B, not D0.L | S | T-E1 |
| E-2 | print "0"; handle INT_MIN | S | T-E2 |
| E-3 | `move.b #0`/`#1` immediates in task 16 | S | T-E3 (read $411 after D1=1 → 1) |
| E-4 | task 8 reads `$40C` (SDB_UPTICKS) as a long into D1.L | S | T-E4 |
| E-5 | task 7 on r2.x: use CHECKINPUT (EFP) instead of the MFP-only code | S | new T-E5 |
| E-6 | add 1 to row/col in ANSI_MOVEXY (or document the 1-based contract) **[doc vs code: pick one]** | S | T-E6 |
| E-8 | save/restore A0 in the TRAP 15 dispatcher | S | new T-E8 |
| B-17 | refuse a 0-byte kernel; check the `fl_attach_media` result | S | T-B17 |
| B-1/B-2 | bound the BIN and Kermit loads to `STAGE2_LOAD` minus stack headroom (and the ELF p_filesz check, B-3) | M | T-B1, T-B2 |
| B-4 | return an error when CMD58 fails | S | T-B4 |
| B-20 | TRAP 13: preserve A0 in the dispatcher (or document that it is trashed) | S | new T-B20 |
| B-12 | SPI_INIT: make it return 0 = OK as documented, or fix the doc (code change breaks existing callers that test for 1, so it needs checking) | S | new T-B12 |
| V-1/V-3 | load the VDP base into A0 in CLRSCR; `moveq #0,D1` before `move.w CURPOS,D1` | S | T-V1 (V-3 needs hardware) |
| X-1/X-2/X-3 | guard start==end; fix the inclusive ranges; rows vs cols | S | hardware only (no Xosera in MAME) |
| D-1 | `move.l (12,A7),A1` | S | T-D1 |
| D-2 | `memcpy` returns `s1` | S | T-D2 |
| D-4 | skip all `isspace()` characters in `strtol` | S | T-D4 |
| D-6 | overflow check in `calloc`; `realloc(p,0)` frees | S | T-D6 |
| D-11 | `readline` index → `int` | S | T-D11 |
| D-12 | swap the 'C'/'D' codes in vterm | S | T-D12 |
| D-7 | libm `include.mk`: `find src/libm …` instead of `find .`; fix the `filter-out` pattern | S | T-D7 |
| D-13/D-14 | gdb: initialise the ring-buffer mask; `(A0)`-relative SRA/SRB; IMR | S | needs m68k gdb |

### Batch 3 — larger or design changes — **2026-10-30: B-5, B-6, D-8, D-3 done on maint/2.42.** D-17 is held (not testable in MAME; brick risk). B-8/B-9/K-* are deferred (no IDE; kernel off). B-16 is feature work
| ID | Fix | Effort | Note |
|----|-----|--------|------|
| B-8 | either reject LBA ≥ 2^28, or implement LBA48 (READ/WRITE EXT) using IDENTIFY words 83/100-103 | M | rejecting is the S-size safe interim fix |
| B-5/B-9 | check the SD data-response token; ATA: wait for BSY, check ERR/DF, CACHE FLUSH | M | **B-5 is high for minix2** (writes through TRAP 13) |
| B-6 | time-based SD timeouts using SDB_UPTICKS | M | **high for minix2**; needs a slow card on real hardware |
| D-8 | enable exponent / long long in `printf_config.h`; fix the `_ftoa` return | M | larger code size |
| D-3 | add memmove/memcmp (+ strstr etc.) to cstdlib | M | |
| D-17 | sst_flash: timeout, IRQ masking, verify | M | protects against bricking during updates |
| K-* | only if the ROM kernel is kept (see [D3]) | L | otherwise covered by Batch 0 |
| B-16 | exFAT / GPT | L | feature work, not a fix |

### Doc-only fixes (InterfaceReference.md and comments)
A-12 (PRINT trashes D0 on the serial console), B-12 (SPI_INIT returns 1 = OK), B-20 (TRAP 13 trashes A0), E-9 (task 9 ignores EFP_HALT), X-6 (`CSI 20h` without `?`), A-22 (r1.x pin/flag text), D-18 (machine.h names/magic comment, `-lkernel`).

### Defer / won't fix (unless a need comes up)
A-6/A-7 (040/060 only), A-14 (TX FIFO, performance), A-15 (dead r1 fallback), A-21 (fast CPUs), D-5 (not reproduced; keep T-D5 as a regression test), B-16 features, X-8/X-9 (minor SGR/scroll).

## 3. Workflow per fix (proposal)
1. Create the branch `maint/2.42` from tag `v2.42`. One commit per finding ID, with the message `Fix <ID>: …`.
2. After each batch, re-run the matching tests from `docs/planning/tests/`. The firmware ROM is rebuilt in docker and booted in MAME with `-rompath` (method in tests/README.md).
3. Option C: port each Batch 2/3 commit to a `fix/<ID>` branch off `develop`.
4. **[D4] Upstream:** whether and how to report or contribute to the upstream rosco_m68k project is your call. I prepare branches and texts; you push and open issues/PRs.
5. Flashing real hardware is done only by you. Claude never flashes and only produces the ROM image plus checksums.
