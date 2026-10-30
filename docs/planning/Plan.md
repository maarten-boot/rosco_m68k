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
| M7 | Build v2.42 (link map, vasm listing) for the static tests T-A3, T-A4, T-D7 | proposed |
| M8 | Check MAME (`../rosco-emulator`) has the rosco_classicv2 driver; run the P1 tests | proposed |
| M9 | Decide per finding: fix on a v2.42 maintenance branch, fix on develop, or upstream an issue | proposed |

## Crosscheck log
| Date | Spec ↔ Plan ↔ Code result |
|------|---------------------------|
| 2026-10-30 | R-1, R-2, R-4, R-6, R-7 covered by reviews/M3a–e and Findings.md. R-3 (InterfaceReference) partly covered: mismatches found in A-1, A-12, B-12, E-4, X-6, D-1, D-18; no full table of documented vs implemented calls yet. R-5 (hardware without driver) covered as a list (Findings P5), not exhaustive. R-8: 34 tests written, none run. Not audited (by design or limits): libm internals, fat_io_lib internals, E-Kermit core, Xosera register defs vs hardware version. No build run, so the A-3 impact is unconfirmed. 14 of 91 findings verified by the main session. |
