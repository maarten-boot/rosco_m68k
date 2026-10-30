# M3b — stage2 + blockdev review (v2.42, r2.x, 1M)

_Source: review agent, 2026-10-30; static reading only. Paths relative to `code/firmware/rosco_m68k_firmware/`._
_✔ = spot-checked by the main session against the v2.42 source._

Develop note: blockdev moved to `stage1/blockdev/`, but ata.c, bbsd.c, bbspi.c, syscalls_asm.asm are byte-identical apart from includes — "no" means the bug is still on develop.

| ID | Title | Location (v2.42) | Cat | Sev | Conf | Fixed on develop |
|----|-------|------------------|-----|-----|------|------------------|
| B-1 ✔ | BIN kernel load has no upper bound → can overwrite stage2 (0xF0000), stack, SDB | stage2/load/load.c:57-65 | bug | medium | high | no |
| B-2 | Kermit receive memcpy to RAM unbounded; pointer not reset between files | stage2/kermit/kermit_support.c:95-99 | bug | medium | high | no |
| B-3 | ELF loader checks p_memsz but reads p_filesz; memset underflow if filesz>memsz; e_entry unchecked | stage2/load/load.c:133,158 | bug | low | high | no |
| B-4 ✔ | `BBSD_initialize` returns OK when CMD58 fails, card struct left uninitialised | blockdev/bbsd.c:68-69 (result init :40) | bug | medium | high | no |
| B-5 | SD write ignores data-response token (WRITE_RESPONSE_OK defined, unused) → failed writes reported OK | blockdev/bbsd.c:297-319 | bug | medium | medium | no |
| B-6 | SD timeouts counted in polled bytes, likely shorter than spec (250 ms write busy, 100 ms read, ~1 s init) | blockdev/include/bbsd.h:36-52 | bug | medium | low | no |
| B-7 ✔ | `spi_read_buffer`: "LED on" writes DUART_INPUT offset = **OPCR** on write; "LED off" writes OUT_LO (= on) | blockdev/dua_spi_asm.asm:156,172 | bug | low→medium* | high | yes (d375bc2/478bac2) |
| B-8 | ATA LBA28 only; LBA ≥ 2^28 (128 GiB) silently wraps — writes corrupt wrong sector | blockdev/ata.c:212-216, 264-268 | missing | medium | high | no |
| B-9 | ATA write: no BSY wait, no ERR/DF check, no CACHE FLUSH | blockdev/ata.c:275-280 | bug | medium | medium | no |
| B-10 | ATA probe OP_TIMEOUT=500000 polls: slow boot with empty IDE, spun-down disks missed; stale TODO | blockdev/ata.c:23,73-141 | bug/todo | low | medium | no |
| B-11 | 16-bit access to possibly odd-aligned caller buffers → address error | blockdev/ata.c:134,227,276 | bug | low | low | no |
| B-12 | FW_SPI_INIT returns 1 on success; doc says 0 = OK | blockdev/syscalls_asm.asm:213; InterfaceReference.md:317-326 | api-mismatch | low | high | no |
| B-13 | stage2 memcpy returns end pointer instead of dest (latent) | stage2/common.c:30-39 | bug | low | high | moved/likely libc |
| B-14 | `__divsi3`/`__modsi3` implemented unsigned (latent wrong signed results) | stage2/common.c:73-78 | bug | low | high | no |
| B-15 | Kermit RECVCHAR blocks forever (no timeout); SSW slot buffer overlaps by 1 byte | stage2/kermit/kermit_support.c:39-69 | bug/todo | low | low | no |
| B-16 | No GPT/extended/superfloppy; FAT12 & exFAT (all SDXC >32 GB) rejected; only SPI CS0 tried | stage2/part/part.c; fat_io_lib | missing | low-med | high | no |
| B-17 | `fl_attach_media` result ignored; 0-byte ROSCODE1.BIN "loads" and jumps to garbage | stage2/load/load.c:269,59-68 | bug | low | medium | unknown |
| B-18 | ATA_DEBUG build doesn't compile (part.c:107,113); SEVERE message missing `[0m` (main2.c:106); rev1 red_led_off uses uninit D1; dead TODO in bbsd.c:83 | various | bug/todo | low | high | no |
| B-19 ★ | **(added in M8)** In the release build, `ROSCO_M68K_ATA` reaches only gcc, not vasm, so FW_ATA_INIT/READ/WRITE/IDENT are stubs → IDE boot and TRAP 13 ATA are dead | blockdev/include.mk:14; blockdev/syscalls_asm.asm:334-420 | build bug | high | high (confirmed in MAME) | yes (d375bc2) |

\* B-7 rated higher by main session: writing 0x08 to OPCR reprograms DUART output-port pin functions (OP3) on every SD multi-byte read — overlaps M3e item 478bac2.

Boot menu/config: none in v2.42 (SD → IDE master/slave → Kermit); boot menu is develop-only.

## Not fully checked
Stage2 size/stack headroom below 0xF0000 (no link map); fat_io_lib internals beyond init/fread; E-Kermit core; GCC widening of bool returns to D0.L for TRAP 13 asm callers; rev1/MFP paths; wall-clock timing (needs hardware).
