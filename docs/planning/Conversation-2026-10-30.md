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

## 7. Commit request
**User:** "commit the first round"
**Claude:** everything was already committed (5 commits on `planning/session-docs`, working tree clean, branch not pushed). Asked whether "commit" means push, squash into one commit, tag, or open a PR.
**User:** "tag it , i can push you can't" — decision: annotated tag `review-round-1`. The user pushes; Claude does not push.

## 8. Status, prune, M8b
**User:** "status?" → reported: branch pushed by the user, tag `review-round-1` is local (whether it is on the remote could not be checked), M8 partial, M8b/M9 open.
**User:** "prune it, then start M8b" — pruned the stale scratchpad worktree; started M8b.
- **M8b:** the scratchpad had been cleared, so v2.42 and the libs were rebuilt (ROM SHA1 unchanged).
  - **Confirmed:** K-1 (vector $10 → $72FAE), K-4 (old_irq3 self-chain after warm boot), E-6, V-1, D-2, D-6, D-8, D-12.
  - **Partly confirmed:** E-3 (masked: byte @1 = $10), B-4 (benign: "Ignoring unrecognised SD card"), D-4 (tab only).
  - **Not reproduced:** D-5.
  - **Not testable:** X-* and V-3 (MAME has no Xosera/V9958 model), B-2 (no host kermit).

## 9. Pending tests, then R-3
**User:** "run the 7 pending tests, then R-3" (no corrections needed).
- **Pending tests:**
  - **Confirmed:** A-2 (ROM `__divsi3`: −7/2=$7FFFFFFC), B-17 (0-byte BIN → crash), D-11 (readline wraps at 256), D-1 (garbage prompt).
  - **Not reproduced:** A-9 is latent (zipped stage2 only $3320 bytes).
  - **Not testable:** D-13 (no m68k gdb on the host).
- **New B-19:** IDE boot never works on the v2.42 release, because `ROSCO_M68K_ATA` reaches gcc but not vasm, so the ATA EFP entry points are stubs. Fixed on develop (d375bc2).
  - **Proof:** a test-only build with the define added to vasm boots from IDE.
  - **B-8:** confirmed on that build. A partition at LBA 2^28+2048 loads the decoy kernel at LBA 2048.
- **R-3:** an agent built the conformance table: 117 rows (56 match, 11 match except for the A0 clobber, 32 partial, 10 mismatch, 8 stubs, 0 missing, 14 undocumented).
  - **Main session checked:** the TRAP15 A0 clobber (E-8) and the task-7 r2.x stub (E-5) in source.
  - **New findings:** E-8, B-20, B-21, E-9, D-19, D-20, A-22.
  - Spec R-3 marked met; all of R-1…R-8 are now addressed.

## 10. M9 — fix strategy
**User:** "yes, start M9" (no corrections needed).
- Checked develop: the ROM kernel is off by default there (`WITH_KERNEL?=false`). So K-* is avoided by configuration, not fixed. The same mitigation is `NO_KERNEL=true` on v2.42.
- Wrote FixStrategy.md:
  - **Options:** A (upgrade), B (maint/2.42), C (maint plus develop ports, recommended).
  - **Batches:** batch 0 is build flags only, batch 1 is backports, batch 2 is small new fixes, batch 3 is larger work; plus doc-only and defer lists.
  - **User decisions D1–D4:** strategy, fitted hardware, ROM kernel use, upstreaming.
- Added Spec R-9 and Plan M10.
- **User answers (M9):**
  - **D1:** option C (maint/2.42 plus develop ports).
  - **D4:** draft issue texts.
  - **D2 (hardware):** not answered.
  - **D3/CPU:** "the standalone board with either a directly loaded app or the start app from disk loader uses the ROM kernel i presume, that is one usecase. Later the minix2 image will use part of the existing ROM code for sd card (bit banged SPI)".
- **Proposed correction:** "usecase" → "use case".
- **Uncertainty raised:** in v2.42 only `software/kernel_test` uses the ROM kernel API at $400. Normal programs, whether Kermit-loaded or ROSCODE1.BIN from SD, use start_serial plus TRAP 13/14/15, and `-lkernel` is empty. So the presumption is probably wrong. Asked the user to confirm.
- **Noted:** minix2 will rely on the ROM SD/SPI path (TRAP 13). That raises B-4, B-5, B-6, B-7, B-12 and B-20 (A0 clobber) in priority.
- **User confirmed:** NO_KERNEL=true; CPU MC68010.
- **Hardware question (D2):** not answered a second time, so it is recorded as open; not asking again for now.
- **FixStrategy.md updated:**
  - Decision table added.
  - The minix2 TRAP 13 SD path promotes B-4, B-5, B-6, B-12 and B-20.
  - K-* deferred.
- **Plan:** M9 done; M10 (implementation) next; M11 (issue texts) proposed.

## 11. M10 batches 0 and 1
**User:** "yes, start with batches 0 and 1" (no corrections needed).
- Created `maint/2.42` from tag v2.42 (worktree in the scratchpad; the commits are in the repo).
  - **Batch 0:** NO_KERNEL default (29a2b69); ATA define for vasm (d14d648).
  - **Batch 1, cherry-picked:** 478bac2, 849bc81, 2b18fb2, c899e46.
  - **Batch 1, hand-ported:** A-3 via `_data_load_start` (82377cc), 1468b51 with path rewrite (06ab09f), heartbeat bit A-10 (4f07454).
  - **Skipped:** 44c9b5a (68000 only), c8ec0ba (keyboard, D2 open), f54f73e (GALs).
- **Regression (ROM 6b18ee0d…):** T-K3, T-B19, T-B7, T-A3, CPU banner 000/010/020, RAM size, SD boot and the libs build all PASS.
