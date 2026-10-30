# M3a — stage1/core firmware review (v2.42, r2.x, 1M)

_Source: review agent, 2026-10-30; static reading only. Paths relative to `code/firmware/rosco_m68k_firmware/` (on develop: `stage1/`)._
_✔ = spot-checked by the main session against the v2.42 source._

| ID | Title | Location (v2.42) | Cat | Sev | Conf | Fixed on develop |
|----|-------|------------------|-----|-----|------|------------------|
| A-1 ✔ | DEVICE_CTRL (TRAP 14 fn 16) can't set baud: handler uses D1, which the TRAP dispatcher has turned into 16×4=64 → CSRA always written $40; doc says param in D2.L | duart.asm:395-440; trap14.asm:28-34,131; InterfaceReference.md:971-993 | api-mismatch | medium | high | no |
| A-2 | `__divsi3`/`__modsi3` unsigned (−7/2 = 0x7FFFFFFC); /0 returns 0 | main1.c:260-301 | bug | medium | high | no (moved to stage1/common.c) |
| A-3 ✔ | `.early_data` placed inside `.data` before `_data_start`; linit copies from `_code_end` (= start of load image incl. early_data) → initialised `.data` gets wrong bytes (offset 518) | rosco_m68k_firmware_1M.ld:36-44; main1.c:88 | bug | medium | medium (logic confirmed; needs map to see impact) | yes (e2cec65) |
| A-4 ✔ | `or.w #0700,SR` — not $0700 (decimal → $2BC, octal → $1C0); interrupts not masked to level 7 in BERR/AERR/ILLEGAL handlers | rev2.asm:108,127,152 (rev1.asm too) | bug | low | high | no |
| A-5 | No NOP between INITMEMCOUNT write/read → memory sizing on 020+ | bootstrap.asm:261-262 | bug | medium (020+) | medium | yes (849bc81) |
| A-6 | Temp BERR handler choice uses signed `blt` on CPUINFO → 040/060 (or misdetected CPU) get 68000 handler → stack corruption | bootstrap.asm:346-347 | bug | low | high | no |
| A-7 | 060 printed as "MC680?0"; speed "0.0MHz" for model ≥4 | main1.c:150-164; cpuspeed.c:24-32 | bug | low | high | no |
| A-8 | CPU detection fragile: `clr.w D0` before `movec VBR`; 060 MOVEP traps via $F4; PMOVE MMUSR not in MAME | cputype.asm:33-35,60,86,99 | bug | medium | high | yes (1468b51, 662ca47) |
| A-9 | `decompress_stage2` returns `move D2,D0` (word) → failure can read as success when insize ≥ 64 KB | decompress.asm:12; main1.c:105 | bug | low | high | no |
| A-10 | r2 heartbeat tests SYSFLAGS bit 9 instead of bit 8 | rev2.asm:70-72 | bug | low | high | yes (7dc8256) |
| A-11 | warm_boot doesn't disable/flush 020+ caches | warmboot.asm:28-31 | missing | low-med | medium | yes (44fb181) |
| A-12 | TRAP 14 PRINT/PRINTLN trash D0; doc says only A0 modified | duart.asm:214-248; InterfaceReference.md:634-690 | api-mismatch | low | high | no |
| A-13 | No "exit boot mode" access → v2.42 incompatible with newer r2 GALs | bootstrap.asm:73-82 | missing | low (stock) / high (new GAL) | medium | yes (f54f73e) |
| A-14 | DUART TX waits on TxEMT not TxRDY → FIFO unused, slower output | duart.asm:222,300,317,333 | perf | low | med-high | no |
| A-15 | r1-DUART fallback in r2 build uses r2 register offsets → dead code | duart.asm:61-80 | bug | low | high | no |
| A-16 | Stubs/TODOs: SET_INTR unimplemented; ENABLE/DISABLE_XMIT/RECV empty on r2; machine.h declares undefined IDLE()/EARLY_PRINT_C(), wrong EFP addresses in comments, DUART_* macros expand to undefined names; version address comment wrong for HUGEROM; dummy PRINT/PRINTLN don't advance A0 (fixed 374009a) | bootstrap.asm:370; serial.asm:41-67; include/machine.h; rosco_m68k_private.asm:14 | todo/doc | low | high | mostly no |
| A-17 | INITDEVS `dbra` clears 129 longs (hits BERR_CONT_ADDR, harmless); MFP device block shift/ctrl ptr 0 (r1 only) | bootstrap.asm:231-241; mfp.asm:83-97 | bug | low | high | no |
| A-18 | pre_warm_boot runs C on caller's stack; cpuspeed/keyboard spin forever without tick | main1.c:138-141; cpuspeed.c:35-41; keyboard.c:29-39 | bug | low | medium | no |
| A-19 | GENERIC_HANDLER RTE on non-advancing exceptions → infinite loop; crashes only flash LED, no dump | bootstrap.asm:393-395; rev2.asm:107-179 | missing | low | high | no |
| A-20 | Makefile: stage2 depends on a directory, no header deps, `$(SYMS)` undefined, r2 message in r1 build | Makefile:189-193 | build | low | high | restructured |
| A-21 | cpuspeed 16-bit counter wraps on fast CPUs | cpuspeed.c:40 | bug | low | medium | no |

Checked and correct: vector table layout & VERSION at +$400; TRAP 13/14/15 slots; DUART 100 Hz timer; r2 TICK_HANDLER save/restore; TRAP 14 jump table range; char_device C wrapper offsets; BERR handler frame arithmetic (000/010/020); LZG decoder register saves.

## Not fully checked
Linked output (A-3 impact, A-4 encoding); MAME behaviour for CALLM/PMOVE/boot mode; DUART_BASE_R2 ($f800a8) vs decoder table; XR68C681 extended baud codes; rev1/MFP in depth; easy68k SDB fields $410-$412 init.
