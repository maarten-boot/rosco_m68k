# Conversation log — 2026-10-30

## 1. Working rules set by the user
- Keep a daily conversation log, plus Plan.md, Spec.md and test cases.
- Suggest a Spec/Plan/code crosscheck after significant changes.
- Before proceeding, suggest corrections for sentences that contain errors or uncertainties, and confirm them with the user.
- GUI/TUI: default to a white background with black text, a contrast ratio of at least 4.5:1 on every colour pair, and contrast that can be raised interactively or through a config file.

**Corrections proposed by Claude:**
- Use the term "WCAG contrast ratio ≥ 4.5:1", not "contrast index > 4.5".
- Black on white is already 21:1, so raising contrast only affects the other colour pairs. Offer presets AA (4.5), AAA (7) and Max (21), plus a custom minimum.
- Asked whether the date format should be YY or YYYY.

## 2. User decisions
- Files go in a subfolder: `docs/planning/`.
- Work on a new branch, `planning/session-docs`, so the files can be committed.
- Date format: `YYYY-MM-DD`.
- The rules apply to all sessions. They are saved globally in `~/.claude/CLAUDE.md`.
- Test-case format was not specified. Default: `Tests.md`, traced to Spec items.

## 3. Next
- Waiting for the user's scenario description.

## 4. Scenario introduced
**User:** "ok we have a existing implementation of firmware for teh rosco classic board here. I am at v2.42 on my hardware and would like to inspect the firmware and its libraries for errors or missing items."

**Proposed corrections:** "a existing" → "an existing"; "teh" → "the".

**Findings while scoping:**
- Tag `v2.42` exists. `develop` is 79 commits ahead and includes firmware fixes such as CPU type detection (#477), the ROMFS move to 0x30000 (#478), the PMOVE MMUSR → TC change for MAME (#462), and the warm-boot crash fix.
- Firmware: `code/firmware/rosco_m68k_firmware` (stage1, stage2, kernel, romfs; API documented in `InterfaceReference.md`). The Makefile has a `REVISION1X` switch for r1.x boards.
- Libraries: `code/software/libs`.

**Open questions put to the user:** board revision, review baseline (tag/develop/both), library scope, the meaning of "missing", review method, ROM size.

## 5. Scope agreed
**User:** "defaults are fine, go ahead; we have a mame emulator at ../rosco-emulator (we also have a quick emulator but ist timing cannot be trusted, mame has a better timing accuracy)"

**Proposed correction:** "ist" → "its".

**Decisions:**
- Board: r2.x.
- Target: tag `v2.42`, compared against `develop`.
- Code: firmware plus `code/software/libs`.
- "Missing": all four kinds (InterfaceReference gaps, TODOs/stubs, hardware features without drivers, fixes made after v2.42).
- Method: static review only.
- ROM: 1M HUGEROM.
- MAME (`../rosco-emulator`) is the reference emulator for runtime checks. The quick emulator is not used for timing.

**Actions:**
- Updated Spec.md (R-1…R-8) and Plan.md (M1–M6).
- Created a read-only v2.42 worktree in the scratchpad.
- Started five parallel review agents (M3a–M3e).
- M3e (develop diff) finished; summary saved to reviews/M3e-develop-diff.md.
- M3b (stage2/blockdev) finished: 18 findings; B-1, B-4, B-7 spot-checked against source. Saved to reviews/M3b-stage2-blockdev.md.
- M3a (core firmware) finished: 21 findings; A-1, A-3, A-4 spot-checked against source. Saved to reviews/M3a-core-firmware.md.
- M3d (user libs) finished: 18 findings; D-1, D-7, D-13 spot-checked against source. Saved to reviews/M3d-libs.md.
- M3c (kernel/EASy68K/video/debug_stub) finished: 34 findings; K-1, K-2, K-3, E-1, E-3 spot-checked. Firmware debug_stub IDs renamed S-x to avoid a clash with the libs' D-x.
- Main session confirmed that the default v2.42 build includes the ROM kernel, V9958 and Xosera ANSI, so K/V/X findings apply to the user's ROM.
- M4: consolidated into Findings.md (91 findings, about 88 unique, 14 verified, ranked P1–P5).
- M5: Tests.md rewritten with 34 MAME/static test cases.
- M6: first crosscheck recorded in Plan.md. Gaps: R-3 has no full API table; nothing has been built or run.
- Proposed next milestones: M7 build for static checks, M8 run P1 tests in MAME, M9 decide where fixes go.

## 6. Next step
**User:** "yes, start with M7 and M8" (no corrections needed).
- **M7:** found the docker toolchain recipe in `../rosco-emulator/roms/README.md` and rebuilt v2.42. The ROM is bit-identical to the emulator's `-bios v242`. Static checks: A-3 confirmed (worse than described: the copy source is the CODE section; in practice only `selected_drive` is affected), A-4 confirmed (`$02BC`), D-7 confirmed (libm.a has 313 members including printf and the other libs).
- **M8:** the MAME build `rosco` has rosco_m68k_000/010/020/030. Confirmed at runtime: K-3, K-2, A-1, A-12, E-1, E-2, E-4, B-7, B-1. B-1 causes a crash/reboot loop.
- **Correction:** debug_stub *is* in the default build (`WITH_DEBUG_STUB?=true`). The M3c note and A-19 were updated.
- Test sources and MAME scripts saved in `docs/planning/tests/`.
