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
- **Method:** static review only (read the code). The MAME emulator at `../rosco-emulator` is available later to confirm findings at runtime. The quick emulator is **not** used for timing-sensitive checks.

## 2. Requirements
| ID | Requirement | Source (log date) |
|----|-------------|-------------------|
| R-1 | Find correctness errors (bugs, crashes, register/ABI misuse, hardware access errors) in the v2.42 firmware. | 2026-10-30 |
| R-2 | Find correctness errors in the v2.42 user libraries. | 2026-10-30 |
| R-3 | "Missing": list the functions documented in `InterfaceReference.md` that are not implemented, or are implemented differently. | 2026-10-30 — **met** by `reviews/R3-interface-table.md` (117 rows) |
| R-4 | "Missing": list the TODO/FIXME/stub/unimplemented paths. | 2026-10-30 |
| R-5 | "Missing": list r2.x hardware features that have no driver or only partial support. | 2026-10-30 |
| R-6 | List the fixes on `develop` after v2.42 that affect an r2.x 1M board, so the user can decide whether to upgrade. | 2026-10-30 |
| R-7 | For each finding, record the file:line at v2.42, the severity, the evidence, and whether `develop` already fixes it. | 2026-10-30 |
| R-8 | Record findings that need runtime confirmation as MAME test cases in `Tests.md`. | 2026-10-30 |

## 3. UI colour and contrast (applies to any GUI/TUI component)
- UI-1: The default theme uses a white background with black text.
- UI-2: Every foreground/background pair has a WCAG contrast ratio of at least 4.5:1.
- UI-3: The user can raise contrast at runtime with presets AA (4.5), AAA (7), Max (21) and a custom minimum.
- UI-4: The contrast setting persists in a config file.
