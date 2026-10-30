# Plan — rosco_m68k firmware v2.42 review

## Milestones
| # | Milestone | Status |
|---|-----------|--------|
| M1 | Agree scope (Spec.md) | done 2026-10-30 |
| M2 | Read-only v2.42 checkout in scratchpad worktree | done 2026-10-30 |
| M3a | Review stage1/core firmware (bootstrap, serial/duart/mfp, trap14, char devices, cputype, warmboot, keyboard, decompress, main1) and compare with InterfaceReference.md | in progress |
| M3b | Review stage2 and blockdev (ATA, SD/SPI, loader, boot menu) | in progress |
| M3c | Review kernel, video (9958, Xosera ANSI), easy68k and debug_stub | in progress |
| M3d | Review user libraries (`code/software/libs/src`, libm at integration level only) | in progress |
| M3e | Analyse v2.42 → develop diff and list relevant fixes | in progress |
| M4 | Consolidate findings into `Findings.md` (deduplicated, ranked by severity, develop-fixed flag) | pending |
| M5 | Write MAME test cases in `Tests.md` for findings that need runtime confirmation | pending |
| M6 | Crosscheck Spec ↔ Plan ↔ findings | pending |

## Crosscheck log
| Date | Spec ↔ Plan ↔ Code result |
|------|---------------------------|
