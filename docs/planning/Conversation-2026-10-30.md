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
