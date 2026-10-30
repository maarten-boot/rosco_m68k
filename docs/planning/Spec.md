# Spec — rosco_m68k firmware v2.42 review

_Status: agreed scope 2026-10-30._

## 1. Scope
- **Target:** firmware release tag `v2.42` (commit 5ef43f8, 2024-01-07), the version flashed on the user's hardware.
- **Board:** rosco_m68k Classic r2.x (`REVISION1X=false`).
- **ROM build:** 1M HUGEROM.
- **Code under review:**
  - firmware: `code/firmware/rosco_m68k_firmware/**` at v2.42
  - libraries: `code/software/libs/src/**` at v2.42. Third-party `libm` is checked only for integration and build issues, not line by line.
- **Comparison baseline:** `develop` (ec229f9), used to identify fixes made after v2.42.
- **Method:** static review, then (from M7 on, as agreed 2026-10-30) a rebuild of v2.42 from source plus runtime confirmation in the MAME emulator at `../rosco-emulator` (`rosco_m68k_010 -bios v242`). The quick emulator is **not** used for timing-sensitive checks. Test-only firmware variants (e.g. the ATA-define build for B-8) live only in the scratchpad and are never flashed or committed.

## 2. Requirements
| ID | Requirement | Source (log date) |
|----|-------------|-------------------|
| R-1 | Find correctness errors (bugs, crashes, register/ABI misuse, hardware access errors) in the v2.42 firmware. | 2026-10-30 — **met**: reviews/M3a–c, Findings.md (A/B/K/E/V/X/S + B-19…B-21, A-22, E-8/E-9); runtime-confirmed items marked ★ |
| R-2 | Find correctness errors in the v2.42 user libraries. | 2026-10-30 — **met**: reviews/M3d, Findings.md D-1…D-20 |
| R-3 | "Missing": list the functions documented in `InterfaceReference.md` that are not implemented, or are implemented differently. | 2026-10-30 — **met** by `reviews/R3-interface-table.md` (117 rows) |
| R-4 | "Missing": list the TODO/FIXME/stub/unimplemented paths. | 2026-10-30 — **met**: Findings P5 + A-16, B-18, E-7, K-7 (TODO/stub lists) |
| R-5 | "Missing": list r2.x hardware features that have no driver or only partial support. | 2026-10-30 — **met** for r2.x as reviewed (Findings P5); the user's board has no extra hardware fitted |
| R-6 | List the fixes on `develop` after v2.42 that affect an r2.x 1M board, so the user can decide whether to upgrade. | 2026-10-30 — **met**: reviews/M3e-develop-diff.md |
| R-7 | For each finding, record the file:line at v2.42, the severity, the evidence, and whether `develop` already fixes it. | 2026-10-30 — **met**: reviews/M3*.md tables (file:line, severity, evidence, develop status) |
| R-8 | Record findings that need runtime confirmation as MAME test cases in `Tests.md`. | 2026-10-30 — **met**: Tests.md (0 pending; T-EMU4…6 run and PASS 2026-10-30). Not testable here: X-*, V-3, B-6 (slow cards), D-13/D-14 (no m68k gdb) |
| R-9 | For each finding, propose a fix target (backport from develop / new fix / build flag / doc / defer) with effort and the test that verifies it. The user decides strategy, hardware scope, kernel use and upstreaming. | 2026-10-30 — `FixStrategy.md`; decisions D1–D4 taken; maint/2.42 + fix/* branches done; upstream issue drafts in `issues/` |
| R-10 | (added 2026-10-30, M9/M10) Implement the chosen fixes as a maintenance release `maint/2.42` → tag `v2.42.1`: one commit per finding, the matching test re-run after each batch, line endings preserved. | 2026-10-30 — **met**: 42 commits; v2.42.1 builds bit-identical to the tested ROM (SHA1 f2d1344d…) |
| R-11 | (added 2026-10-30, M10b/M11) Port the new fixes to `fix/<ID>` branches off develop and draft upstream issue texts; the user pushes and files. | 2026-10-30 — **met**: 30 branches (integration build + MAME smoke test); issues/01–21 |
| R-12 | (added 2026-10-30, M12) Make the ROM flash-programmable in the MAME emulator (`../rosco-emulator` feature/sst-flash) so the flash tools can be tested. | 2026-10-30 — **met** at tag review-round-2: updateflash 2.42 → 2.42.1 end-to-end. Review fixes EMU-4…6 (cec16b598fa) re-verified (T-EMU4…6 PASS) and merged into rosco-m68k-ram-bios (dece8a1ff7c, --no-ff) |


## 3. UI colour and contrast (applies to any GUI/TUI component)
_Not applicable in this project so far: no GUI or TUI was built (all output is serial console text). Kept as a standing rule._
- UI-1: The default theme uses a white background with black text.
- UI-2: Every foreground/background pair has a WCAG contrast ratio of at least 4.5:1.
- UI-3: The user can raise contrast at runtime with presets AA (4.5), AAA (7), Max (21) and a custom minimum.
- UI-4: The contrast setting persists in a config file.
