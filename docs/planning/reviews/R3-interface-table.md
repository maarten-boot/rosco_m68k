# R3 - rosco_m68k v2.42: InterfaceReference.md vs implementation (conformance table)

_Produced 2026-10-30 by a review agent; spot-checked by the main session: G1 (TRAP 15 A0 clobber, syscalls_asm.asm:42 with no restore in EPILOGUE/EPILOGUE2) and TRAP 15 task 7 r2.x stub (syscalls_asm.asm:246-258) confirmed in source. The other 8 known mismatches were already confirmed at runtime in M8/M8b._

Source tree: tag `v2.42`, `code/` (v2.42, built default: r2.x, 1M HUGEROM, 68000, ROM kernel, V9958, Xosera ANSI, debug_stub, EASy68K, blockdev, ATA C code; REVISION1X NOT defined; ROSCO_M68K_ATA NOT defined for the assembler).
Method: read source and `rosco_m68k.dis`/`.sym` (ROM truth). Nothing in the repo was edited.

Path abbreviations: `FW/` = `firmware/rosco_m68k_firmware/`, `LIB/` = `software/libs/src/`. `dis:` = address in `FW/rosco_m68k.dis`.

Status vocabulary
- Implemented: `yes` / `stub` / `missing`.
- Matches doc: `yes` / `no` / `partial` / `yes+G1` (= matches the row's own contract but is subject to the global finding G1 below; counted separately).

## Global findings referenced from rows

- **G1 (TRAP #15 trashes A0 on every task).** `FW/easy68k/syscalls_asm.asm:42` `move.l JUMPTABLE(PC,D0),A0` (dis e05818 `moveal %pc@(e05820,%d0:w),%a0`). A0 is never restored (the A0 push/pop in tasks 13/14/17/18 saves the already-clobbered value). Doc §1 intro says "all registers other than those stated are preserved"; A0 is stated only for task 11.
- **G2 (TRAP #13 trashes A0 on every function incl. CHECK_*).** `FW/blockdev/syscalls_asm.asm:33` `move.l .JUMPTABLE(PC,D0),A0`. Doc lists only D0 as modified for FC 0, 5, 15.
- **G3 (TRAP #14 passes D1 = FC*4 to EFP and device functions).** `FW/trap14.asm:32-33` (`add.l D1,D1` twice) before dispatch; D1 is restored only at `.EPILOGUE` (:59). Handler preserves A1 and D1 for the caller (:26-27, :59-60), so the caller sees D1 intact, but callee code sees the multiplied value. This is the root cause of the DEVICE_CTRL defect.
- **G4 (SDB layout in user lib differs from doc).** `LIB/machine/include/machine.h:176-183` names $40A `heartbeat_frequency` (doc: system flags), $410 `e68k_reserved` (u32, covers $413 internal flags); comment says magic "B105DA7A" (real value $B105D47A). `LIB/start_serial/link_scripts/*.ld:40-50` has no symbol for $40A and no EFP symbols for $490/$494/$498.

## 1.1 TRAP #13 - block device / SPI (D0.L = function code; handler `FW/blockdev/syscalls_asm.asm:25-63`, out-of-range FC rte silently at :28-29)

| Doc § | Name | Doc contract | Implemented? | Matches doc? | Mismatch detail (file:line evidence) | Lib wrapper |
|---|---|---|---|---|---|---|
| 1.1.2.1 | CHECK_SD_SUPPORT (0) | in D0=0; out D0=$1234FEDC; modifies D0 only | yes | partial | Returns magic (`syscalls_asm.asm:65-67`, dis e0281a `movel #305463004,%d0`). But A0 also trashed (G2). | `SD_check_support` (LIB/sdfat/sdcard_asm.S:14) |
| 1.1.2.2 | SD_INIT (1) | A1=SDCard*; out D0 = status (0 OK); trashes A0, may trash A1 | yes (EFP_SD_INIT -> FW_SD_INIT -> BBSD_initialize) | partial | (a) D1 also trashed (dis e01f8e `moveq #0,%d1`), doc does not list D1. (b) If CMD58 fails on a V2 card the code does `goto finally` with `result` still `BBSD_INIT_OK` (`blockdev/bbsd.c:40,68-69`): returns 0 (success) while `sd->initialized` was never set. | `SD_initialize` (sdcard_asm.S:26; saves A0/A1, not D1 - OK for C ABI) |
| 1.1.2.3 | SD_READ_BLOCK (2) | D1=block, A1=SDCard*, A2=buf; D0 0=fail; D1/A0/A1/A2 may be trashed | yes | yes | FW_SD_READ->SD_BLOCK_OP pushes A2,D1,A1 and calls BBSD_read_block (dis e028b6-e028d8). bool returned in D0. | `SD_read_block` (sdcard_asm.S:36; matches doc example) |
| 1.1.2.4 | SD_WRITE_BLOCK (3) | as FC 2 | yes | yes | BBSD_write_block present in ROM (dis e02482); `-DSD_BLOCK_READ_ONLY` (blockdev/include.mk:8) only removes partial-read code (bbsd.c:80,212,432), not write. | `SD_write_block` (sdcard_asm.S:46) |
| 1.1.2.5 | SD_READ_REGISTER (4) | D1=cmd, A1, A2=16-byte buf; D0 0=fail | yes | yes | BBSD_readreg (bbsd.c:122) reads 16 bytes + 2 CRC. | `SD_read_register` (sdcard_asm.S:56) |
| 1.1.2.6 | CHECK_SPI (5) | out D0=$1234FEDC; modifies D0 only | yes | partial | Same code as FC 0; A0 trashed (G2). | none |
| 1.1.2.7 | SPI_INIT (6) | out D0: 0 = OK, else failed; A0 arbitrary | yes | **no** | `BBSPI_initialize` returns `true` (`blockdev/bbspi.c:27-35`; dis e019d0 `moveq #1,%d0; rts`). Success = 1, opposite to doc and to the `FW_SPI_INIT` source comment (syscalls_asm.asm:213 "0 = OK"). The SPI pin modes are no-ops on r2.x (`dua_gpio_spi.h` `#define pinMode(...)`), so it can never return failure. | none |
| 1.1.2.8 | SPI_ASSERT_CS (7) | D1 = 0 or 1; out D0 (0 failed, else OK); A0 arbitrary | yes | partial | Result semantics OK (dis e028fa-e02912, invalid dev returns 0). A1 is also trashed (`syscalls_asm.asm:226` `move.l #BBSPI_assert_cs1,A1`, dis e028e6) - undocumented. Doc pin text "CS0=GPIO1, CS1=GPIO5" is the r1.x/MFP mapping (`mfp_gpio_spi.h:38,50`); r2.x build uses DUART OPR bit 2 (CS0) and bit 7 (CS1) (`dua_gpio_spi.h:31,43`). | none |
| 1.1.2.9 | SPI_DEASSERT_CS (8) | as FC 7 | yes | partial | Same: A1 trashed (dis e028ee-e028f4); r2.x pin text differs. | none |
| 1.1.2.10 | SPI_TRANSFER_BYTE (9) | D1=byte; out D0=byte received; A0 arbitrary | yes | yes | FW_SPI_TRANSFER_BYTE -> BBSPI_transfer_byte (dis e02914). Upper D0 bits are 0 only because D0 held FC*4 (<256) - fine. | none |
| 1.1.2.11 | SPI_TRANSFER_BUFFER (10) | A1=buf, D1=count; D0=count; A1 maybe modified | yes | yes | SPI_BUFFER_OP pushes D1,A1 (dis e02948); BBSPI_transfer_buffer returns count (bbspi.c:69-72). | none |
| 1.1.2.12 | SPI_RECV_BYTE (11) | out D0=byte; A0 arbitrary | yes | partial | `spi_read_byte` (blockdev/dua_spi_asm.asm:105-107) uses D1 and A1 without saving -> both trashed, doc lists only D0/A0. Doc text ("Send and receive a byte (exchange)") is copy-paste. | none |
| 1.1.2.13 | SPI_RECV_BUFFER (12) | A1, D1=count; D0=count | yes | yes | BBSPI_recv_buffer returns count (bbspi.c:82-85). | none |
| 1.1.2.14 | SPI_SEND_BYTE (13) | D1=byte; A0 arbitrary, D1 may be trashed | yes | partial | FW_SPI_SEND_BYTE (syscalls_asm.asm:282-288) is a copy of TRANSFER_BYTE, so D0 returns the received byte (undocumented) and the clock is a full exchange. Doc text copy-paste. | none |
| 1.1.2.15 | SPI_SEND_BUFFER (14) | A1, D1=count; D0=count | yes | yes | BBSPI_send_buffer returns count (bbspi.c:87-90). | none |
| 1.1.2.16 | CHECK_ATA_SUPPORT (15) | D0=$1234FEDC iff ATA present | yes | **no** | Returns the magic unconditionally (same CHECK_SUCCESS, syscalls_asm.asm:50) although all four ATA entries are stubs in this build, so the "is ATA supported" probe lies. stage2 `ATA_support_check` (FW/stage2/idehdd/ata.asm:17-20) is fooled. | none (stage2 `ATA_support_check` only) |
| 1.1.2.17 | ATA_INIT (16) | D1=0/1, A1=ATADevice*; D0 = ATAInitStatus (0 OK) | **stub** | no | `FW_ATA_INIT` assembled without `ROSCO_M68K_ATA` (syscalls_asm.asm:334-341): dis e02952 `moveq #1,%d0; rts` (always "failure"). C `ATA_init` is in ROM (dis e02bf4) but unreachable from TRAP 13. main1.c:234 still runs `ata_init()` (C has the define). | none (stage2 `ATA_init` calls EFP directly, ata.asm:25-33) |
| 1.1.2.18 | ATA_READ_SECTORS (17) | D1=LBA, D2=count, A1, A2; D0=sectors read | **stub** | no | dis e02956 `moveq #0,%d0; rts` -> always 0 sectors. `ATA_read_sectors` dis e02d40 is dead code. | none (stage2 only) |
| 1.1.2.19 | ATA_WRITE_SECTORS (18) | as FC 17 | **stub** | no | dis e0295a `moveq #0,%d0` then falls into FW_ATA_IDENT (no rts between, harmless). `ATA_write_sectors` e02eb8 dead. | none |
| 1.1.2.20 | ATA_IDENTIFY (19) | A1, A2=512B buf; D0 0=failed 1=ok | **stub** | no | dis e0295c `moveq #0,%d0; rts`. `ATA_ident` e03030 dead. | none |

## 1.2 TRAP #14 - character IO (D1.L = function code; handler `FW/trap14.asm:25-143`, FC>18 -> `.EPILOGUE` no-op at :29-30; A1 and D1 saved/restored :26-27,:59-60)

Console in the default build with no video hardware = DUART A (EFP_PRINT=EARLY_PRINT_DUART, PRINTCHAR/SENDCHAR=SENDCHAR_DUART; `FW/duart.asm:114-122`). With V9958 / Xosera the PRINT family is replaced and DOES preserve D0 (vdpcon.asm:`V9958_CON_PRINT` pushes D0; xosera_ansiterm_init.asm:75-86 `movem.l d0-d1/a1`).

| Doc § | Name | Doc contract | Implemented? | Matches doc? | Mismatch detail | Lib wrapper |
|---|---|---|---|---|---|---|
| 1.2.2.1 | PRINT (0) | D1=0, A0=str; modifies only A0 (ends after NUL) | yes | **no** (serial console) | `EARLY_PRINT_DUART` `move.b (A0)+,D0` (duart.asm:219; dis e008b0 `moveb %a0@+,%d0`) trashes D0.B; D0 not listed in doc. A0 end-pointer OK. Preserved on V9958/Xosera consoles. | `mcPrint` (LIB/machine/machine.asm:20; saves D0,D1,A0 so hides it) |
| 1.2.2.2 | PRINTLN (1) | as PRINT + CRLF | yes | **no** (serial console) | `EARLY_PRINTLN_DUART` (duart.asm:240-248) calls the same loop; D0 trashed. V9958 PRINTLN emits only CR (`SZ_CR` = $0D, vdpcon.asm:715) but its PUTCHAR treats CR as newline. | `mcPrintln` (:33) |
| 1.2.2.3 | SENDCHAR (2) | D0.B char; modifies nothing | yes | yes | `SENDCHAR_DUART` duart.asm:296-304 saves A0, D0 intact. | `mcSendchar` (:72) |
| 1.2.2.4 | RECVCHAR (3) | out D0.B; blocks | yes | yes | `RECVCHAR_DUART` duart.asm:344-352. Xosera replaces EFP_RECVCHAR with a wrapper (D0 only modified). | `mcReadchar` (:85) |
| 1.2.2.5 | PRINTCHAR (4) | D0.B; modifies nothing | yes | yes | SENDCHAR_DUART / V9958_CON_PUTCHAR (saves D1-D3/A0-A1) / XANSI_CON_PRINTCHAR (saves d0-d1/a0-a1). Doc text typo "in D0.B to by A0". | `mcPrintchar` (:46) |
| 1.2.2.6 | SETCURSOR (5) | D0.B 0 hide / non-zero show; nothing modified | yes | yes | UART: `EFP_DUMMY_NOOP` (duart.asm:121). V9958: `tst.b D0` (vdpcon.asm:~300). Xosera: XANSI_CON_SETCURSOR. | `mcSetcursor` (:59) |
| 1.2.2.7 | CHECKCHAR (6) | out D0.B 0/non-zero | yes | yes | `CHECKCHAR_DUART` (duart.asm:255-261) returns SRA&1; upper D0 bits unchanged (doc says D0.B only). | `mcCheckchar` (:97) |
| 1.2.2.8 | CHECK_DEVICE_SUPPORT (7) | D0=$1234FEDC | yes | yes | trap14.asm:99-101. | `mcCheckDeviceSupport` (:179) |
| 1.2.2.9 | GET_DEVICE_COUNT (8) | out D0.W | yes | yes | char_device.asm:16-18. In this build count = 2 (DUART A type 2, DUART B type 3; duart.asm:125-150). | `mcGetDeviceCount` (:199) |
| 1.2.2.10 | GET_DEVICE (9) | D0.W idx, A0=dest 32B; out D0.B 0/non-zero; A0 trashed | yes | yes | char_device.asm:21-43; copies 8 longs, A0 advanced by 32; `cmp.w DEVICE_COUNT,D0 / bhs`. | `mcGetDevice` (:212) |
| 1.2.2.11 | ADD_DEVICE (10) | A0=struct; out D0.B 0-15 index, >15 fail; (only D0.B listed as modified) | yes | partial | On success A0 is advanced by 32 (char_device.asm:56-63, `(A0)+`) but doc lists no A0 change (other device calls say "A0 Trashed"). Index/failure semantics OK (:48-49,:66; failure returns 16). | `mcAddDevice` (:227) |
| 1.2.2.12 | DEVICE_RECVCHAR (11) | A0=CHAR_DEVICE; out D0.B; A0 trashed | yes | yes | char_device.asm:72-75 jumps to `8(A0)`; `D_RECVCHAR_DUART_A` (duart.asm:362-368) trashes A0. | `mcReadDevice` (:255) |
| 1.2.2.13 | DEVICE_SENDCHAR (12) | D0.B, A0; A0 trashed | yes | yes | char_device.asm:77-80 `12(A0)`. | `mcSendDevice` (:269) |
| 1.2.2.14 | DEVICE_CHECKCHAR (13) | A0; out D0.B; A0 trashed | yes | yes | char_device.asm:82-85 `4(A0)`. | `mcCheckDevice` (:241) |
| 1.2.2.15 | RESERVED (14) | do not call | yes (no-op) | yes | trap14.asm:52 -> `.EPILOGUE`. | none |
| 1.2.2.16 | RESERVED (15) | do not call | yes (no-op) | yes | trap14.asm:53. | none |
| 1.2.2.17 | DEVICE_CTRL (16) | D0.L = cmd (low byte) + data, **D2.L = 32-bit parameter**, A0; out D0 (0 unknown cmd); A0 trashed | yes | **no** | `D_CTRL_DUART_A/B` read the baud selector from **D1.B**, not D2: `move.b D1,DUART_CSRA(A0)` (duart.asm:404; dis e00972 `moveb %d1,%a0@(2)`), while the header comment (:390) and doc say D2. Via TRAP 14, D1 = 16*4 = $40 (G3, trap14.asm:32-33), so a TRAP-14 caller always writes **$40** to CSRA/CSRB whatever it puts in D2. Return value (1 ok / 0 unknown cmd, duart.asm:405,409) and A0 trash match. Direct (non-TRAP) calls with D1 set would work. Doc also does not say what command 0 is. (r1.x build only: the MFP device block has a NULL ctrl pointer, mfp.asm device setup `move.l #0,(A0)+` at offset $18 -> jsr to address 0; not in this build.) | `mcDeviceCtrl` (machine.asm:284-294) loads D2 per doc, so the wrapper is correct vs doc and the firmware ignores it |
| 1.2.2.18 | INPUTCHAR (17) | out D0.B; blocks | yes | yes | EFP_INPUTCHAR = copy of RECVCHAR at boot (bootstrap.asm:113), replaced by keyboard handler if `rosco_kbd` found on device 1 (keyboard.c:97-121, keyboard_efp.asm:32-39, saves A0/A1). | `mcInputchar` (:322) |
| 1.2.2.19 | CHECKINPUT (18) | out D0.B | yes | yes | bootstrap.asm:114; keyboard_efp.asm:23-30. | `mcCheckInput` (:334) |

## 1.3 TRAP #15 - EASy68K layer (D0.L = task; handler `FW/easy68k/syscalls_asm.asm:34-75`). See G1 for A0.

| Doc § | Name | Doc contract | Implemented? | Matches doc? | Mismatch detail | Lib wrapper |
|---|---|---|---|---|---|---|
| 1.3.2.1 | PRINTLN_LEN (0) | D1.W len, A1=str; D1 trashed, A1 after last char | yes | yes+G1 | syscalls_asm.asm:82-105; dbra loop prints D1.W chars (no 255 limit enforced), then CRLF via FW_PRINT. | `e68PrintlnLen` (LIB/easy68k/easy68k.S:22) |
| 1.3.2.2 | PRINT_LEN (1) | as 0 w/o CRLF | yes | yes+G1 | :90-105. | `e68PrintLen` (:38) |
| 1.3.2.3 | READSTR (2) | doc: **A0**=buffer; out D1.W len (max 80), string at (A1) | yes | partial | Doc is self-contradictory (args say A0, description/outputs say A1). Code uses **A1** (`move.l A1,-(A7)` :110; restored at :155). Max 80 chars + NUL needs 81-byte buffer (:122,:136-139). Only CR terminates (:128); no backspace; LF is stored. Prompt "Input$> " printed if $411 non-zero. | `e68ReadlnStr` (:54, uses A1) |
| 1.3.2.4 | DISPLAYNUM_SIGNED (3) | D1.L; D1 possibly trashed | yes | partial | Value **0 prints nothing**: `print_signed_impl` loops `while (value > 0)` (FW/easy68k/syscalls.c:36) then `*bp = 0; return bp+1` (:45-47) -> empty string (dis e05ae2-e05af4: `tstl %d2; bnes`, `clrb %a0@+`). Non-zero values OK incl. INT_MIN. Shared by tasks 17, 20. | `e68DisplayNumSigned` (:71) |
| 1.3.2.5 | READNUM (4) | out D1.L | yes | yes+G1 | :172-229. Accepts digits only (a leading '-' is ignored, so no negative numbers), max 10 digits, no overflow check; CRLF printed if $412 set; prompt "Input#> " if $411. Doc silent on these. | `e68ReadlnNum` (:86) |
| 1.3.2.6 | READCHAR (5) | out D1.B; blocks | yes | yes+G1 | :232-235 `move.l D0,D1` (D1.L = char, upper bytes 0 because D0 was FC*4). | `e68ReadChar` (:101) |
| 1.3.2.7 | SENDCHAR (6) | D1.B; D1 trashed | yes | yes+G1 | :239-242; D1 actually preserved (superset-safe). | `e68SendChar` (:117) |
| 1.3.2.8 | CHECKINPUT (7) | out D1.B 1 if pending | yes (reads nothing) | **no** | Under `ifd REVISION1X` (syscalls_asm.asm:249-253) it reads MFP_RSR directly; REVISION1X is undefined for r2.x, so the ROM contains only `moveb #0,%d1; braw EPILOGUE2` (dis e05992-e05996; the `moveb #1,%d1` at e0599a is unreachable). **Always returns 0 on r2.x.** Even on r1.x it ignores the default UART (the TODO at :246). | `e68CheckRecv` (:132) |
| 1.3.2.9 | GETUPTICKS (8) | out D1.L = upticks (hundredths since boot, SDB $40C) | yes | **no** | `move.w $408,D1` (syscalls_asm.asm:266; dis e059a2 `movew 408 <SDB_TICKCNT>,%d1`) returns the heartbeat down-counter (reload 50, cycles 49..0 once per ~0.5 s, rev2.asm:64-97), not upticks at $40C (rev2.asm:57-59). Only D1.W is written; D1 upper word is left as the caller had it. Doc's "word-sized, rolls over every 655.36 s" also contradicts its own SDB table ($40C is 4 bytes). | `e68GetTicks` (:148) returns `move.l D1,D0` -> upper 16 bits are caller garbage |
| 1.3.2.10 | TERMINATE (9) | disable ints, halt; never returns | yes | yes+G1 | JUMPTABLE entry `HALT` (:58) -> `STOP_HEART; stop #$2700` (bootstrap.asm:~350). Calls HALT directly, **not through EFP_HALT ($42C)**, so replacing the EFP does not affect this task. | `e68Halt` (:163) |
| 1.3.2.11 | MOVEXY (11) | D1.W high=COL 0-79, low=ROW 0-31, (0,0) top left; $FF00 = clear; D1,D2,A0 trashed | yes | partial | **Off-by-one:** `ANSI_MOVEXY` sends ESC[ low ; high H with the raw values (FW/ansicon.asm:25-38; no +1) while ANSI CUP is 1-based: coordinate 0 and 1 select the same row/col, and every position N>=1 lands on 0-based N-1, i.e. one row up / one column left of what the 0-based doc promises. D1/D2 are actually preserved (saved by movem, :17). $FF00 clear OK (syscalls_asm.asm:272-281). V9958 console has no ANSI parser (no ESC handling in vdpcon.asm), so the sequence is printed as text. | `e68MoveXY` (:175), `e68ClearScr` (:195) |
| 1.3.2.12 | SETECHO (12) | D1.B 0/1; D1 trashed | yes | yes+G1 | :285-287 `move.b D1,ECHO_ON` ($410). | `e68SetEcho` (:210) |
| 1.3.2.13 | PRINTLN_SZ (13) | A1=sz; D1 trashed; A1 after NUL | yes | yes+G1 | :291-297. | `e68Println` (:225) |
| 1.3.2.14 | PRINT_SZ (14) | as 13 w/o CRLF | yes | yes+G1 | :301-307. | `e68Print` (:240) |
| 1.3.2.15 | PRINT_UNSIGNED (15) | D1.L, D2.B base 2-36 (else ignored); D1,D2 trashed | yes | yes+G1 | :311-316; `print_unsigned` ignores base<2 or >36 (syscalls.c:87-89); prints 0 correctly (:93). D2 actually preserved. | `e68DisplayNumUnsigned` (:255) |
| 1.3.2.16 | SETDISPLAY (16) | D1.B 0/1 prompt off/on, 2/3 LF off/on | yes | **partial (absolute addressing)** | Source `move.b 0,PROMPT_ON` / `move.b 1,PROMPT_ON` / `...LF_DISPLAY` (syscalls_asm.asm:332,336,340,344; dis e05a0e `moveb 0,411`, e05a16 `moveb 1,411`, e05a1e `moveb 0,412`, e05a26 `moveb 1,412`) uses memory at addresses 0 and 1 as the source instead of `#0`/`#1`. Those are the first two bytes of the initial-SSP vector: byte 0 = 0 and byte 1 = (RAM size>>16)&$FF ($10 for 1 MB after main1.c:144 sets vector 0 = memsize). So it works by accident for 0 / non-zero and breaks if vector 0 changes (e.g. user RAM-resident vector table / 68010 VBR move irrelevant, but SSP vector edits, or byte 1 == 0). | `e68SetDisplayOpt` (:271) |
| 1.3.2.17 | PRINTSZ_NUM (17) | A1=sz, D1.L; D1,A1 trashed | yes | partial | Uses `print_signed` -> value 0 prints nothing (see task 3). A1 is actually preserved (FW_PRINT restores A1). | `e68PrintStrNumSigned` (:286) |
| 1.3.2.18 | PRINTSZ_READ_NUM (18) | A1=sz; out D1.L | yes (firmware) | yes+G1 | syscalls_asm.asm:363-370. **Lib bug:** wrapper loads the string pointer into **D1** (`move.l (12,A7),D1  ; ... into A1`, LIB/easy68k/easy68k.S:304) instead of A1, so the firmware prints from whatever A1 held. | `e68PrintStrReadNumSigned` (:302) - **broken** |
| 1.3.2.19 | PRINTNUM_SIGNED_WIDTH (20) | D1.L, D2.B width; D1,A1 trashed | yes | partial | `print_signed_width` returns without printing if width==0 or >=76 (syscalls.c:56-58); if the number is wider than the field the leading characters are dropped (:65-68); 0 prints as blanks (same `print_signed_impl` bug). Falls through into EPILOGUE2 (:374-381) - fine. | `e68PrintNumSignedWidth` (:318) |
| 1.3 (intro) | Task numbers > 20 | doc: other codes reserved | yes | **no** (crash) | Handler pushes D0 (:35) then for `D0 > 20` executes `rte` without popping (:37-38,:45-46; dis e0580a `movel %d0,%sp@-`, e05812 `bhis e0581e`, e0581e `rte`). rte then pops D0 as SR+PC high word -> wild jump/privilege change. Tasks 10 and 19 are safe no-ops (JUMPTABLE :59,:68). TRAP 13/14 handle bad FCs safely. | n/a |

## 2. System Data Area

| Doc § | Name | Doc contract | Implemented? | Matches doc? | Mismatch detail | Lib wrapper |
|---|---|---|---|---|---|---|
| 2.1 | Exception vectors $0-$3FF | 256 vectors; movable via VBR on 68010+ | yes | partial | Table copied from ROM by START (bootstrap.asm:73-82). Vectors 2-11 are replaced by `debug_stub()` (main1.c:240-242, debug_stub.asm:36-42) - not mentioned. Unused TRAP vectors are `GENERIC_HANDLER`, which is not a pure no-op: it writes $2BADB105 to $404 (bootstrap.asm:393-395). Vector 0 is rewritten to memsize after boot (main1.c:144). | `mcGetVecBase` (machine.asm:301) |
| 2.2 $400 | SDB Magic $B105D47A | constant magic | yes at boot, **overwritten** | **no** | INITSDB writes the magic (bootstrap.asm:146; dis e00458) and main1 checks it (main1.c:183), but with the default ROM kernel `api_init()` (called at main1.c:254 and in pre_warm_boot) stores `&api` at $400 (`kernel/api.c:49-50`, `kernel/include/kernelapi.h:27`; dis e06834 `movel %a0,400`). After boot $400 is a pointer, not the magic. Libs still describe it as magic (`_SDB_MAGIC`, G4). | `_SDB_MAGIC` (linker sym) |
| 2.2 $404 | Status code | set by exception handlers | yes | yes | Init $C001C001 (bootstrap.asm:147), GENERIC_HANDLER sets $2BADB105 (:394). Values undocumented. | `_SDB_STATUS` |
| 2.2 $408 | W: internal tick counter | internal | yes | yes | Reload 50 then counts 49..0 (rev2.asm:64-97). Exposed incorrectly as "uptime" by task 8. | `_SDB_RSRVD_408` |
| 2.2 $40A | W: system flags | default $FFXX | yes | yes | Init $FF00 (bootstrap.asm:149). Lib struct calls it `heartbeat_frequency` (G4); no lib symbol. | none |
| 2.2 $40C | L: upticks | updated by tick handler | yes | yes | rev2.asm:57-59, DUART timer ~100 Hz (duart.asm:106-110). 32-bit, so no 655 s rollover. | `_TIMER_100HZ` |
| 2.2 $410 | B: Easy68k echo flag | | yes | yes | Set to 1 only by INSTALL_EASY68K_TRAP_HANDLERS (syscalls_asm.asm:391); not initialised if EASy68K omitted. | `_EASY68K_ECHOON` |
| 2.2 $411 | B: prompt flag | | yes | yes | :392; see task 16 bug. | `_EASY68K_PROMPT` |
| 2.2 $412 | B: LF display flag | | yes | yes | :393; also applied by task 4. | `_EASY68K_SHOWLF` |
| 2.2 $413 | B: internal flags | tick handler | yes | yes | LED on/off state in r2.x tick handler (rev2.asm:74-89). | `_SDB_RSRVD_413` |
| 2.2 $414 | L: size of first RAM block | | yes | yes | INITMEMCOUNT (bootstrap.asm:247-280). | `_SDB_MEM_SIZE` |
| 2.2 $418 | L: default UART base | | yes | yes | DUART base ($F00001 on r2 mainboard) stored by duart.asm:83. | `_SDB_UART_BASE` |
| 2.2 $41C | L: CPU info (3 bits model, 29 bits speed) | | yes | yes | cputype.asm:111-114; speed in kHz (main1.c:166-171); 0 when NO_TICK. | `_SDB_CPU_INFO` |
| 2.2 flags | bit 15 CTS (MFP GPIP7) | | not in this build | partial | Only used by r1.x MFP code (`mfp.asm` SENDCHAR/RECVCHAR); r2.x DUART path never reads it. | none |
| 2.2 flags | bits 14-10 "MUST BE 1 for SPI/SD" | | not enforced | partial | No code in blockdev/ or either SPI backend reads $40A (grep: only rev1/rev2 tick handlers, mfp.asm). Clearing them has no effect in this build. | none |
| 2.2 flags | bit 9 LED1 | gates LED | yes | partial | rev2.asm:70-72 tests bit 1 of the high byte (= word bit 9) to allow the heartbeat LED, which on r2.x is DUART OPR5 (`W_OPR_SETCMD #$20`), not "MFP GPIP1". | none |
| 2.2 flags | bit 8 LED0 | | not in this build | partial | Used only in rev1 tick handler. | none |
| 2.3 | EFPT range $420-$4FF (56 slots) | 0xE0 bytes | yes (31 used) | yes | Slots $49C-$4FF are neither initialised nor used (INITEFPT ends at $498, bootstrap.asm:162-202): contents are RAM garbage. | n/a |
| 2.4 | VDA $500-$117F | video-owned | yes | yes | Xosera data $500-$57F (`XANSI_CON_DATA`), V9958 BUFFER from $50A (.sym). Doc says layout TODO. | n/a |
| 2.5 | Reserved area 1 $1180-$17FF | "reserved for future" | used | partial | $1180 BERR_SAVED and $1184 BERR_FLAG live here (rosco_m68k_private.asm:31-32, shared with machine.h). | n/a |
| 2.6 | BSS $1800-$1FFF | firmware BSS | yes | yes | DEVICE_COUNT $1800, DEVICE_BLOCKS $1802-$1A01, BERR_CONT_ADDR $1A02, .data $1A06, .bss ends $1E4C (.sym). Fits. | n/a |

## 2.3 Extension Function Pointer Table (EFPT) slots

Defaults come from INITEFPT dummies (bootstrap.asm:162-226) then are replaced as shown. Doc rule: contract = the TRAP function it serves; "must remain at that address", supervisor mode, supervisor stack.

| Doc § | Name ($addr) | Doc contract | Implemented? | Matches doc? | Mismatch detail | Lib wrapper |
|---|---|---|---|---|---|---|
| 2.3 | FW_PRINT ($420) | A0 -> after NUL | yes | partial | D0 trashed on serial console (see 1.2.2.1). V9958/Xosera replace it. | `_EFP_PRINT` symbol (machine.h:220) |
| 2.3 | FW_PRINTLN ($424) | | yes | partial | as above. | `_EFP_PRINTLN` |
| 2.3 | FW_PRINTCHAR ($428) | | yes | yes | | `_EFP_PRINTCHAR` |
| 2.3 | FW_HALT ($42C) | disable ints + halt | yes | partial | Set to `HALT` (bootstrap.asm:198) but **never called**: TRAP 15 task 9 jumps to `HALT` directly (syscalls_asm.asm:58). Changing the EFP has no effect. | `_EFP_HALT` |
| 2.3 | FW_SENDCHAR ($430) | via default UART | yes | yes | | `_EFP_SENDCHAR` |
| 2.3 | FW_RECVCHAR ($434) | | yes | yes | Xosera wraps it (XANSI_CON_RECVCHAR, xosera_ansiterm_init.asm:243). | `_EFP_RECVCHAR` |
| 2.3 | FW_CLRSCR ($438) | clear console | yes | yes | UART/Xosera: ANSI string via FW_PRINT (ansicon.asm:48-53); V9958: V9958_CON_CLRSCR (clobbers D0, A1 - callers FW_CLRSCR saves A1). Only reachable via TRAP15 task 11/$FF00 (no TRAP 14 function). | `_EFP_CLRSCR` |
| 2.3 | FW_MOVEXY ($43C) | D1.W: high X(col), low Y(row) | yes | partial | Note 1 matches code but see off-by-one (task 11). Not overridden by V9958 or Xosera (always ANSI text). | `_EFP_MOVEXY` |
| 2.3 | FW_SETCURSOR ($440) | D0.B | yes | yes | | `_EFP_SETCURSOR` |
| 2.3 | FW_CHECKCHAR ($444) | | yes | yes | Xosera wraps it. | `_EFP_CHECKCHAR` |
| 2.3 | FW_PROGRAM_LOADER ($448) | defaults to SD/Kermit | yes | yes | `default_program_loader` (main1.c:104-124, installed :122-124) decompresses and calls stage2, which does SD/Kermit. Initial value `START` until then (bootstrap.asm:199). | `_EFP_PROGLOADER` |
| 2.3 | FW_SD_INIT ($44C) | = TRAP 13 FC1 | yes | partial | see 1.1.2.2 | none (no `_EFP_SD_*` symbol; stage2 `sdcard.asm:31`) |
| 2.3 | FW_SD_READ ($450) | = FC2 | yes | yes | | none |
| 2.3 | FW_SD_WRITE ($454) | = FC3 | yes | yes | | none |
| 2.3 | FW_SD_REG ($458) | = FC4 | yes | yes | | none |
| 2.3 | FW_SPI_INIT ($45C) | = FC6 (0 OK) | yes | **no** | returns 1 (see 1.1.2.7). Pre-blockdev dummy returns -1 (bootstrap.asm:181). | `_EFP_SPI_INIT` (link script only) |
| 2.3 | FW_SPI_ASSERT_CS ($460) | = FC7 | yes | partial | A1 trashed | `_EFP_SPI_CS_A` |
| 2.3 | FW_SPI_DEASSERT_CS ($464) | = FC8 | yes | partial | A1 trashed | `_EFP_SPI_CS_D` |
| 2.3 | FW_SPI_TRANSFER_BYTE ($468) | | yes | yes | | `_EFP_SPI_XFER_B` |
| 2.3 | FW_SPI_TRANSFER_BUFFER ($46C) | | yes | yes | | `_EFP_SPI_XFER_M` |
| 2.3 | FW_SPI_RECV_BYTE ($470) | | yes | partial | D1, A1 trashed | `_EFP_SPI_RECV_B` |
| 2.3 | FW_SPI_RECV_BUFFER ($474) | | yes | yes | | `_EFP_SPI_RECV_M` |
| 2.3 | FW_SPI_SEND_BYTE ($478) | | yes | partial | returns D0 | `_EFP_SPI_SEND_B` |
| 2.3 | FW_SPI_SEND_BUFFER ($47C) | | yes | yes | | `_EFP_SPI_SEND_M` |
| 2.3 | FW_ATA_INIT ($480) | | **stub** | no | dis e02952 (returns 1) | `_EFP_ATA_INIT`; stage2 `ata.asm:32` |
| 2.3 | FW_ATA_READ ($484) | | **stub** | no | dis e02956 (returns 0) | `_EFP_ATA_READ` |
| 2.3 | FW_ATA_WRITE ($488) | | **stub** | no | dis e0295a | `_EFP_ATA_WRITE` |
| 2.3 | FW_ATA_IDENT ($48C) | | **stub** | no | dis e0295c | `_EFP_ATA_IDENT` |
| 2.3 | FW_PROG_EXIT ($490) | used by lib exit() | yes | yes | main1.c:145 sets it to `pre_warm_boot`; `start_serial/init.S:69-82` saves/replaces/restores it. No machine.h extern and no link-script symbol. | init.S only |
| 2.3 | FW_INPUTCHAR ($494) | blocking default input | yes | yes | bootstrap.asm:113; keyboard_efp.asm:20. Not in LIB link scripts / machine.h (G4). | `mcInputchar` goes via TRAP |
| 2.3 | FW_CHECKINPUT ($498) | | yes | yes | bootstrap.asm:114; keyboard_efp.asm:19. | `mcCheckInput` via TRAP |
| 2.3 | Note 2 / EFP call convention | "same registers as TRAP"; supervisor | partial | partial | EFP functions are entered with D1 = FC*4 when reached through TRAP 14 (G3). SD/SPI/ATA EFPs are entered from the TRAP 13 handler with A0 already used as the jump register. | n/a |

## 3. Character devices

| Doc § | Name | Doc contract | Implemented? | Matches doc? | Mismatch detail | Lib wrapper |
|---|---|---|---|---|---|---|
| 3.1 | 16 devices, UARTs auto-created | | yes | yes | C_NUM_DEVICES=16 (rosco_m68k_private.asm:43), DEVICE_BLOCKS 16*32 B (bootstrap.asm:~385). INITDEVS clears 129 longs (516 B), 4 bytes past the block (harmless, overwrites BERR_CONT_ADDR). | `CharDevice` (machine.h:190-199) |
| 3.2 | CHAR_DEVICE 32 B layout (data, CHECK $4, RECV $8, SEND $C, rsvd $10/$14, CTRL $18, caps $1C W, flags $1E, type $1F) | | yes | yes | Offsets used by char_device.asm:73,78,83,88 and duart.asm:131-148. Lib struct names $18 as `reserved2` (G4-like naming gap, layout same). | `CharDevice` |
| 3.2.1 | Capability flags (ignored) | | yes | yes | Written 0. | |
| 3.2.2 | Device types 1=MFP, 2=DUART A, 3=DUART B | | partial | partial | This r2.x build only creates types 2 and 3 (MFP block only under REVISION1X, mfp.asm). | |
| 3.3 | Device functions: A0 = struct, D0 return; legal to call directly | | yes | partial | Direct calls work (`D_CTRL_DUART_*` expects baud in D1, see DEVICE_CTRL). | |

## Undocumented in code

- TRAP 13: any FC > 19 silently ignored (rte, D0 unchanged) - doc says "reserved"; behaviour not stated (syscalls_asm.asm:28-29).
- TRAP 14: any FC > 18 silently ignored (trap14.asm:29-30).
- TRAP 15: tasks 10 and 19 are accepted no-ops (JUMPTABLE entries `EPILOGUE`, :59,:68); tasks > 20 crash (see 1.3 intro row).
- EFP: slots $49C-$4FF unused and uninitialised; Xosera replaces RECVCHAR/CHECKCHAR (doc says "default UART").
- EFP/device functions see D1 = FC*4 (G3).
- SDB $400 becomes the ROM-kernel `IKernel*` (`KERNEL_API_ADDRESS` $400, kernel/include/kernelapi.h:27).
- $404 status values $C001C001 ("OK") and $2BADB105 (bad exception) not described.
- Other memory used: BERR_SAVED/FLAG $1180/$1184, DEVICE_COUNT $1800, DEVICE_BLOCKS $1802, BERR_CONT_ADDR $1A02, `api` struct at ~$1DF8 (.bss), `keyboard_device` (.bss), Xosera data $500, V9958 BUFFER $50A.
- debug_stub installs handlers on vectors 2-11 in the default build (main1.c:240).
- Keyboard auto-detect on char device 1 (DUART B) switching INPUTCHAR/CHECKINPUT (keyboard.c:97-121) - only hinted at in doc 1.2.2.18.
- Easy68K input/echo behaviours: prompts "Input$> " / "Input#> ", ECHO/LF flags applied to READNUM, no negative numbers, no backspace.
- Firmware-internal C/asm helpers (FW_PRINT_C, GET_CHAR_DEVICE_C, CHAR_DEV_*_C, FW_MOVEXY, FW_CLRSCR, BUSYWAIT_C, HALT, SET_INTR) exported but undocumented.
- User lib: wrappers `mcBusywait`, `mcDelaymsec10`, `mcDisableInterrupts`, `mcEnableInterrupts`, `mcGetVecBase`, `mcInputchar`, `mcCheckInput`, `e68ClearScr` have no doc section; no lib wrappers at all for TRAP 13 FC 5-19 (SPI, ATA, CHECK_*), `sdfat` covers FC 0-4 only.
- Doc hygiene (no functional effect): header says "firmware 2.0" (build is 2.42); TOC titles differ from body ("SPI & Block device IO", "Character device IO routines" vs "Block device IO", "Basic IO routines"); TOC omits "System flags word", "CPU Info", 3.2.1, 3.2.2; duplicate "# 2." heading; TRAP 15 intro cross-references sections 1.1.2.1/1.1.2.3 (wrong); references to `bootstrap.S`, `trap14.S`, `sdcard/syscalls_asm.S` (files are `.asm`, blockdev/); copy-paste descriptions for SPI_RECV_BYTE, SPI_SEND_BYTE and CHECK_SPI/ATA ("SD support is always available").

## Summary

117 table rows in total: 59 function rows (TRAP13 20, TRAP14 19, TRAP15 19 tasks + the ">20" row), 16 SDB/flag rows, 5 memory-map rows, 32 EFP rows, 5 character-device rows.

| Category | Function rows (59) | SDB (16) | Memory (5) | EFP (32) | Char dev (5) | **Total (117)** |
|---|---|---|---|---|---|---|
| Implemented and matches doc (`yes`) | 22 | 11 | 3 | 17 | 3 | **56** |
| Implemented, matches except global A0 clobber G1 (`yes+G1`) | 11 | 0 | 0 | 0 | 0 | **11** |
| Partial match | 14 | 4 | 2 | 10 | 2 | **32** |
| Mismatch (`no`, implemented) | 8 | 1 | 0 | 1 | 0 | **10** |
| Stub (ATA, all `no`) | 4 | 0 | 0 | 4 | 0 | **8** |
| Missing | 0 | 0 | 0 | 0 | 0 | **0** |
| Undocumented-in-code items (separate section) | | | | | | **14 bullets** (13 behaviour/layout items + 1 doc-hygiene list) |

Per interface: TRAP13 = 7 yes, 7 partial, 2 no, 4 stub; TRAP14 = 15 yes, 1 partial, 3 no; TRAP15 = 11 yes+G1, 6 partial, 3 no (tasks 7, 8, >20).
"Missing" is 0 for firmware entry points; what is missing is user-lib coverage: no wrappers for TRAP13 FC 5-19, the lib link scripts define `_EFP_*` only up to $48C (nothing for $490/$494/$498), and there is no `$40A` symbol.
The 10 `no` rows are: SPI_INIT, CHECK_ATA_SUPPORT, TRAP14 PRINT, PRINTLN, DEVICE_CTRL, TRAP15 task 7, task 8, task >20, SDB magic $400, EFP FW_SPI_INIT.
Known-defect confirmation: all 8 pre-known mismatches confirmed (DEVICE_CTRL D1/$40, PRINT/PRINTLN D0 - only on the serial console, SPI_INIT=1, task 8 reads $408, task 16 absolute addressing, task 11 off-by-one, task >20 crash, ATA stubs, SDB magic overwritten). The task-11 "off-by-one" is a 0-based vs 1-based ANSI mismatch; there is no separate off-by-one in the loop counters. New findings: G1/G2, task 7 dead on r2.x, CHECK_ATA_SUPPORT lying, print of 0, task 9 bypassing EFP_HALT, SD_INIT CMD58 false-OK, e68PrintStrReadNumSigned wrapper bug, e68GetTicks garbage high word, SPI CS pin text is r1-only, flag bits 14-10 not enforced.

### Top 10 mismatches by user impact

1. **TRAP15 task 7 CHECKINPUT always returns 0 on r2.x** (REVISION1X not defined; dis e05992). Any EASy68K program polling for input never sees a key.
2. **TRAP15 task numbers > 20 crash** (push D0 then bare `rte`, dis e0581e). Any call with an unknown task number takes down the machine.
3. **ATA over TRAP 13 is entirely stubbed** (dis e02952-e0295e) while CHECK_ATA_SUPPORT still returns the success magic, so software that probes first will try and fail; stage2 ATA boot also uses these EFPs.
4. **TRAP14 DEVICE_CTRL ignores D2 and writes D1 = $40 to the DUART CSR** (duart.asm:404, trap14.asm:32-33): baud change via the documented interface sets a constant wrong rate.
5. **TRAP15 task 8 GETUPTICKS returns the 49..0 heartbeat counter** from $408 (not $40C upticks), upper D1 word undefined; `e68GetTicks` passes the garbage on.
6. **SPI_INIT returns 1 on success; doc says 0 = OK** (dis e019d0) - callers following the doc treat success as failure (and the call can never fail).
7. **Print routines TRAP15 3/17/20 print nothing for value 0** (syscalls.c:36,45); width variant prints blanks.
8. **TRAP15 trashes A0 on every task** (G1) and **TRAP13 trashes A0 on CHECK_*** (G2) contrary to the documented "all other registers preserved".
9. **SDB magic at $400 is overwritten by the ROM-kernel API pointer** after boot (kernel/api.c:50); anything validating the magic after boot (or trusting `_SDB_MAGIC`) fails.
10. **TRAP15 task 16 SETDISPLAY and task 11 MOVEXY**: SETDISPLAY reads bytes from vector-table addresses 0/1 instead of immediates (works only by accident); MOVEXY positions are off by one (0-based doc vs 1-based ANSI); plus TRAP14 PRINT/PRINTLN trashing D0 on the serial console, and the `e68PrintStrReadNumSigned` wrapper passing the string in D1 instead of A1.
