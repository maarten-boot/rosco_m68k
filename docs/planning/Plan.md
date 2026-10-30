# Plan — rosco_m68k firmware v2.42 review

## Milestones
| # | Milestone | Status |
|---|-----------|--------|
| M1 | Agree scope (Spec.md) | done 2026-10-30 |
| M2 | Read-only v2.42 checkout in scratchpad worktree | done 2026-10-30 |
| M3a | Review stage1/core firmware (bootstrap, serial/duart/mfp, trap14, char devices, cputype, warmboot, keyboard, decompress, main1) and compare with InterfaceReference.md | done 2026-10-30 → reviews/M3a-core-firmware.md |
| M3b | Review stage2 and blockdev (ATA, SD/SPI, loader, boot menu) | done 2026-10-30 → reviews/M3b-stage2-blockdev.md |
| M3c | Review kernel, video (9958, Xosera ANSI), easy68k and debug_stub | done 2026-10-30 → reviews/M3c-kernel-video-easy68k.md |
| M3d | Review user libraries (`code/software/libs/src`, libm at integration level only) | done 2026-10-30 → reviews/M3d-libs.md |
| M3e | Analyse v2.42 → develop diff and list relevant fixes | done 2026-10-30 → reviews/M3e-develop-diff.md |
| M4 | Consolidate findings into `Findings.md` (deduplicated, ranked by severity, develop-fixed flag) | done 2026-10-30 |
| M5 | Write MAME test cases in `Tests.md` for findings that need runtime confirmation | done 2026-10-30 (34 tests, 3 static) |
| M6 | Crosscheck Spec ↔ Plan ↔ findings | done 2026-10-30 (see log below) |
| M7 | Build v2.42 (link map, vasm listing) for the static tests T-A3, T-A4, T-D7 | done 2026-10-30 (ROM bit-identical to emulator v242; all 3 confirmed) |
| M8 | Check MAME (`../rosco-emulator`) has the r2 driver; run the P1 tests | partly done 2026-10-30: driver `rosco_m68k_0x0` with `-bios v242`; 12 findings confirmed (tests/). Still open: K-1, K-4, V-1, V-3, X-1, E-3, E-6, B-2, B-4, D-x library tests |
| M8b | Remaining runtime tests: kernel task exit (K-1), warm-boot IRQ chain (K-4), V9958/Xosera (check whether MAME models them), library tests | done 2026-10-30: 8 more confirmed, 3 partly, 1 not reproduced (D-5); MAME has no V9958/Xosera; no host Kermit |
| R3 | Full InterfaceReference ↔ code conformance table | done 2026-10-30 → reviews/R3-interface-table.md (6 new findings) |
| M9 | Decide per finding: fix on a v2.42 maintenance branch, fix on develop, or upstream an issue | done 2026-10-30 → FixStrategy.md (D1=C, D3=NO_KERNEL on 68010, D4=issue texts; D2 hardware open) |
| M10 | Implement batches 0–3 on `maint/2.42` (+ `fix/<ID>` ports off develop), re-running the matching tests after each batch | batches 0+1 done 2026-10-30 (9 commits, all regression tests PASS); batch 2 next |
| M11 | Draft upstream issue texts (one per confirmed finding, with repro from tests/) in docs/planning/issues/ | proposed |

## Crosscheck log
| Date | Spec ↔ Plan ↔ Code result |
|------|---------------------------|
| 2026-10-30 | R-1, R-2, R-4, R-6, R-7 covered by reviews/M3a–e and Findings.md. R-3 (InterfaceReference) partly covered: mismatches found in A-1, A-12, B-12, E-4, X-6, D-1, D-18; no full table of documented vs implemented calls yet. R-5 (hardware without driver) covered as a list (Findings P5), not exhaustive. R-8: 34 tests written, none run. Not audited (by design or limits): libm internals, fat_io_lib internals, E-Kermit core, Xosera register defs vs hardware version. No build run, so the A-3 impact is unconfirmed. 14 of 91 findings verified by the main session. |
| 2026-10-30 (2) | After M7/M8: Spec R-8 is now partly met (12 of 34 tests run, all 12 confirm the bug, 0 false positives so far). Spec scope corrected: debug_stub is in the default build. Findings.md and Tests.md match the code and the run results. Open: R-3 still has no full API table; M8b is not run yet. |
| 2026-10-30 (3) | After M8b: 22 findings confirmed at runtime or statically, 3 partly confirmed, 1 not reproduced (D-5). Untestable here: X-*, V-3, B-2, B-6, recorded in Tests.md. Spec R-8 is met as far as this emulator allows. Open: R-3 API table; M9. |
| 2026-10-30 (4) | Pending tests run: A-2, B-8, B-17, D-1, D-11 confirmed; A-9 latent; D-13 not testable. New finding B-19 (IDE/ATA EFPs built as stubs in the release) was confirmed and added to the Spec scope under R-1. Next: R-3. |
| 2026-10-30 (5) | R-3 is met: 117-row table; new findings E-8, B-20, B-21, E-9, D-19, D-20, A-22, and E-5 upgraded. All Spec requirements R-1…R-8 are now addressed. Open: M9 (fix strategy), plus untestable items (Xosera, V9958, Kermit, gdb, slow SD) that need hardware or tools. |
| 2026-10-30 (6) | maint/2.42 batches 0+1: code ↔ FixStrategy ↔ Tests consistent; every changed area has a passing regression test. Open: debug_stub 020 runtime check; batch 2. |
