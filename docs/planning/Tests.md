# Test cases

_Runtime checks for v2.42 findings (Spec R-8). Run in MAME (`../rosco-emulator`, rosco_classicv2 driver) unless noted. The quick emulator is not used for timing-sensitive tests._
_Status: pending = not run yet. Results from M7/M8 (2026-10-30, MAME rosco_m68k_010 `-bios v242`, ROM SHA1 6ff2a658… reproduced from source). Test sources: `tests/`._
_Status legend: pending = not run; "Static" = can be verified from a build artefact (map, listing) without running._

## Firmware findings
| ID | Finding | Setup / steps | Expected if bug present | Pass criterion (fixed) | Status |
|----|---------|---------------|-------------------------|------------------------|--------|
| T-K3 | K-3 | Boot the default v2.42 1M build; in the MAME debugger read long @ $400 | value ≠ $B105D47A (kernel API pointer) | $B105D47A | **FAIL (bug confirmed)** 2026-10-30: $400 = $00001DF8 from ~3.65 s (api_init); magic intact before that |
| T-K1 | K-1 | Kernel test program: start one task that returns; watchpoint on writes to $10–$13 | watchpoint fires from `suspend`; vector 4 = stack address | no write to $10 | **FAIL (bug confirmed)**: ($10) $00E05654 → $00072FAE (init-stack address) after the init task returned |
| T-K2 | K-2 | Program: register, then remove an IRQ handler; read SR and `disable_intr_count` | SR mask 7, count 1 | mask restored, count 0 | **FAIL (bug confirmed)**: after remove SR=$2704, count=1 |
| T-K4 | K-4 | Load a program, exit (warm boot), trigger a level 1–7 autovector IRQ | SP shrinks continuously / hang | handler runs once | **FAIL (bug confirmed)**: 2nd irq_init (warm boot) sets old_irq3 = $E05D8E = irq_3 itself → self-chain |
| T-B7 | B-7 | Boot from an SD image; watch DUART writes to OPCR (offset $1A) during reads | OPCR written $08; red LED stays on | no OPCR writes; LED off after read | **FAIL (bug confirmed)**: OPCR written $08 ×5 during SD boot |
| T-A3 | A-3 | **Static:** link map / `objdump -h`: compare LOADADDR(.data) with `_code_end` and `_data_start`; list the .data symbols | .data initialisers shifted by sizeof(.early_data) | n/a (fixed by e2cec65) | **FAIL (bug confirmed, static)**: copy source `_code_end`=$E0A8DE is the CODE section (ATA routine), not .data LMA $E0A904; `selected_drive` gets $20 instead of $FF (harmless in this build, latent) |
| T-A4 | A-4 | **Static:** vasm listing of rev2.asm:108; or MAME: execute an illegal opcode and read SR in the flash loop | immediate ≠ $0700; SR mask < 7 | mask 7 | **FAIL (bug confirmed, static)**: encoded `oriw #$02BC,SR` at $E00A1A/$E00A52/$E00AAA |
| T-A1 | A-1 | Program: TRAP 14 fn 16, D0=0, D2=$BB, A0=device 0; watch CSRA write | CSRA ← $40 | CSRA ← $BB | **FAIL (bug confirmed)**: CSRA written $40 (requested $BB); console lost afterwards |
| T-A2 | A-2 | Program (68010 build): compute (−7)/2 and (−7)%2 via the firmware's `__divsi3` | 0x7FFFFFFC / wrong remainder | −3 / −1 | **FAIL (bug confirmed)**: −7/2=$7FFFFFFC, −7%2=1, 7/−2=0 (ROM `__divsi3`/`__modsi3` called directly) |
| T-A9 | A-9 | Corrupt one byte of the zipped stage2 in the ROM image; boot | boots garbage / hangs | "Stage 2 failed" message | **Not reproduced (latent)**: corrupted stage2 → "Stage 2 failed; Stop." correctly. Zipped stage2 is only $3320 bytes; the bug needs ≥ 64 KiB |
| T-A12 | A-12 | Set D0=$DEADBEEF, TRAP 14 fn 0 with a string | D0 changed | D0 preserved (per doc) | **FAIL (bug confirmed)**: D0 $DEADBEEF → $DEADBE00 |
| T-E1 | E-1 | `move.l #21,d0; trap #15` | crash / jump to garbage | returns normally | **FAIL (bug confirmed)**: task 21 → bus error, debug_stub dump, warm boot |
| T-E2 | E-2 | `moveq #0,d1; moveq #3,d0; trap #15` | nothing printed | "0" | **FAIL (bug confirmed)**: task 3 with 0 prints nothing; 42 prints "42" |
| T-E3 | E-3 | Task 16 D1=0 (prompt off), then D1=1 (prompt on), then task 4 | no "?" prompt | prompt shown | **Code bug confirmed, symptom masked**: "on" stores byte @1 = $10 (from SSP vector), which is non-zero, so the prompt does re-enable on this config |
| T-E4 | E-4 | Call task 8 repeatedly for 2 s | value cycles 49..0 | monotonically increasing ticks | **FAIL (bug confirmed)**: task 8 returned $01 then $18 while SDB_UPTICKS=$20E |
| T-E6 | E-6 | Task 11 D1=$0505, then print "X"; inspect the terminal | X at row/col 5 (1-based) | X at row/col 6 (1-based) | **FAIL (bug confirmed)**: emits ESC[5;5H |
| T-V1 | V-1 | V9958 attached; A0=$2000, fill $2000–$2800 with $AA, call FW_CLRSCR | $2000/$2002 region modified | memory untouched | **FAIL (bug confirmed)**: $2000 $AAAAAAAA → $00AA60AA (called ROM routine directly, no V9958 in MAME) |
| T-V3 | V-3 | D1.L=$00100000, PRINTCHAR at the bottom row to force a scroll; watchpoint on $100000–$10FFFF | 80-byte zero write | no write | **Not testable in MAME** (no V9958 model); still open |
| T-X1 | X-1 | Xosera: write a pattern to VRAM above the text area; CUP to the last column; ESC[K | pattern erased | pattern intact | **Not testable in MAME** (no Xosera model) |
| T-X2 | X-2 | Fill a line, cursor to column 0, ESC[K | last character remains | line fully cleared | **Not testable in MAME** (no Xosera model) |
| T-X3 | X-3 | Cursor on the bottom row, ESC E | no scroll; cursor off-screen | scrolls one line | **Not testable in MAME** (no Xosera model) |
| T-B1 | B-1 | FAT SD image with a 750 KB ROSCODE1.BIN; boot | hang/crash near the end of load | load rejected or bounded | **FAIL (bug confirmed)**: 768000-byte BIN overwrites stage2 → bus error at PC=$0F0206 → warm boot reloads same file → **crash/reboot loop** |
| T-B2 | B-2 | Kermit-send a file > 704 KB | corruption near $F0000 | transfer rejected | **Not run**: no Kermit sender on the host |
| T-B4 | B-4 | SD model returning an error on CMD58 | boot proceeds with garbage card type | init error reported | **Partly confirmed** (fault injection at $E02118): init reports OK; stage2 then prints "Ignoring unrecognised SD card", no crash |
| T-B19 | B-19 | Boot from a normal FAT32 IDE image (partition at LBA 2048) on the stock v2.42 ROM | no "ATA Device 0:" line; "No bootable media found" | boots ROSCODE1.BIN from IDE | **FAIL (bug confirmed)**: FW_ATA_INIT disassembles to `moveq #1,d0; rts`. With `-DROSCO_M68K_ATA` added for vasm, the same image boots |
| T-B8 | B-8 | IDE image > 128 GiB with a partition beyond LBA 2^28 | reads/writes wrap to low sectors | error or LBA48 | **FAIL (bug confirmed)** on an ATA-enabled test build (see B-19): partition at LBA 2^28+2048 → loaded the decoy at LBA 2048 |
| T-B17 | B-17 | 0-byte ROSCODE1.BIN on SD | "Loaded 0 bytes", jumps to garbage | load refused | **FAIL (bug confirmed)**: "Loaded 0 bytes", jumps to $40000 → illegal instruction → warm boot |

## Library findings (build a test program against v2.42 libs)
| ID | Finding | Steps | Expected if bug present | Pass criterion | Status |
|----|---------|-------|-------------------------|----------------|--------|
| T-D1 | D-1 | `e68PrintStrReadNumSigned("Enter: ")` | no or garbage prompt | "Enter: " printed | **FAIL (bug confirmed)**: garbage (".....") printed instead of "PROMPT> "; the number was read correctly |
| T-D2 | D-2 | `char b[8]; memcpy(b,"abc",4)==b` | false | true | **FAIL (bug confirmed)**: memcpy ret−dest = 4; strncpy also returns ≠ dest |
| T-D5 | D-5 | Allocate until NULL; pre-fill memsize−32K with $FF; free the last block; malloc/free loop | heap corruption / crash | stable | **Not reproduced**: 866×1 KiB filled, last freed, 200/200 cycles OK, full re-alloc OK (needs non-zero garbage above heap end) |
| T-D7 | D-7 | **Static:** `m68k-elf-ar t libm.a` | lists printf.o, sdfat, vterm, … | math objects only | **FAIL (bug confirmed, static)**: libm.a has 313 members incl. printf.o, putchar.o, basicio.o, kinit.o, vterm.o, heap.o, sst.o |
| T-D8 | D-8 | softfloat: `n=sprintf(b,"ab%f",1e10)` | n and b wrong | n = strlen(b) | **FAIL (bug confirmed)**: n=2, buf="cd"; "%lld|%d" → "|0"; "%e|%d" → "e|1073217536" |
| T-D11 | D-11 | `readline(buf, 300)` and type 280 characters | buffer start overwritten | 299 characters stored | **FAIL (bug confirmed)**: 280 chars into a 300-byte buffer → ret=24, buffer start overwritten, bytes 256+ untouched |
| T-D4 | D-4 | `strtol("abc",&end)` and `strtol("\t42")` | end = s−1; tab not skipped | end = s; 42 | **Partly confirmed**: end−in = 0 (correct), but "\t42" → 0 (tab not skipped) |
| T-D6 | D-6 | `calloc(0x10000,0x10001)` | non-NULL (overflowed size) | NULL | **FAIL (bug confirmed)**: returned $0000B09E |
| T-D12 | D-12 | `vt_move_cursor_left(1)` | cursor moves right | moves left | **FAIL (bug confirmed)**: left emits ESC[3C, right emits ESC[3D |
| T-D13 | D-13 | gdb to MAME; send characters while running, then break in | characters lost | delivered | **Not testable here**: host gdb has no m68k target |

## UI rules (carried over; only applies if a GUI/TUI is built)
| ID | Spec ref | Description | Expected result | Status |
|----|----------|-------------|-----------------|--------|
| T-UI-1 | UI-1 | Start the UI with no config | white background, black text | n/a |
| T-UI-2 | UI-2 | Compute the contrast ratio of every theme colour pair | all ≥ 4.5:1 | n/a |
| T-UI-3 | UI-3 | Switch the preset to AAA at runtime | all ≥ 7:1 without a restart | n/a |
| T-UI-4 | UI-4 | Set the preset in the config file and restart | preset applied at startup | n/a |

## Regression runs on `maint/2.42`
### Batches 0+1 (2026-10-30, ROM SHA1 6b18ee0d…, maint/2.42 @ 4f07454)
| Test | Fix | Result |
|------|-----|--------|
| T-K3 | NO_KERNEL default (K-*) | **PASS**: $400 = $B105D47A at 6 s (was $00001DF8) |
| T-B19 | ATA define for vasm (B-19/B-21) | **PASS**: FW_ATA_INIT calls ATA_init; boots ROSCODE1.BIN from an IDE image ("ATA Device 0: … Loaded 112 bytes") |
| T-B7 | 478bac2 (SPI LED registers) | **PASS**: OPCR written once ($00, init) during SD boot; no $08 writes (was 5) |
| T-A3 | _data_load_start (A-3) | **PASS** (static + ROM bytes): copy source = .data LMA + $206; `selected_drive` initialiser = $FF |
| CPU banner | 1468b51 (A-8) | **PASS**: rosco_m68k_000 → MC68000, _010 → MC68010, _020 → MC68020 (42.8 MHz is a known MAME timing artefact) |
| RAM size | 849bc81 (A-5) | **PASS**: 1048576 bytes on 000/010/020 |
| SD boot | regression | **PASS**: loads ROSCODE1.BIN from SD |
| libs build | 2b18fb2 (D-15), c899e46 (S-2/D-16) | **PASS**: libs and firmware build with -Werror; runtime check of the debug_stub frames on 020 still to do |
| A-10 | heartbeat bit | static: `btst #0` on the SYSFLAGS high byte (bit 8) |

Note: the earlier test programs that call fixed ROM addresses (`t_div`, `t_misc` V-1) must use the new map addresses on maint builds. The kernel tests (T-K1, T-K2, T-K4) no longer apply with NO_KERNEL=true.
