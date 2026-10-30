# v2.42 runtime tests (MAME)

Small vasm test programs plus MAME debugger scripts used for milestone M8 (2026-10-30).

## Build the programs
Use the `roscopeco/rosco_m68k` docker image (vasm), as in `../rosco-emulator/roms/README.md`:

    docker run --rm -u "$(id -u):$(id -g)" --group-add 1001 -v "$PWD:$PWD" -w "$PWD" \
      --entrypoint /usr/bin/env roscopeco/rosco_m68k \
      PATH=/home/linuxbrew/.linuxbrew/bin:/usr/bin:/bin vasmm68k_mot -Fbin -m68010 -quiet -o t_easy.bin t_easy.asm

## Run them
The `.dbg` files use `$TESTS` (the folder holding the .bin files) and `$OUT` (an output folder) as placeholders. Replace them with absolute paths before running, for example with `sed`.

    ../rosco-emulator/rosco rosco_m68k_010 -bios v242 -rompath ../rosco-emulator/roms -skip_gameinfo \
      -terminal null_modem -bitb console.txt -video none -sound none -nothrottle -seconds_to_run 9 \
      -debug -debugger none -debugscript mame/run_prog.dbg

- **Programs:** `run_*.dbg` waits 5 s of emulated time, then loads a program at $40000 and jumps to it. The quickload slot fires at 3 s, which is before boot finishes on v2.42.
- **SD images:** for B-7 and B-1, build a 64 MiB image with an MBR and a FAT32 partition at sector 2048. Put ROSCODE1.BIN on it (`mcopy` is available in the `rosco-emulator:local` image) and pass `-hard1 sd.img`.
- **Output:** console output goes to `console.txt`. Strip the ANSI escapes before reading it.
- **Watchpoint logs:** MAME's debugger `printf` is not captured with `-debugger none`. The scripts therefore log PCs and data into RAM at $60000 and `save` that range. Don't use $80000: the firmware's memory sizing writes test values there.

## M8b additions (2026-10-30)
- **`t_misc.asm`:** E-3, E-6 and V-1. V-1 calls `V9958_CON_CLRSCR` at $E031BE directly, because MAME has no V9958.
- **`t_k1.asm`:** gives the PMM 64 KiB, then calls kernel `start()` with an init task that returns at once. It then checks vector $10.
- **`t_k4.asm`:** prints the IRQ3 chain, then exits through EFP_PROG_EXIT (warm boot). Run it with `mame/k4_irq_chain.dbg`, which logs VEC_IRQ3 and old_irq3 at the end of each `irq_init`.
- **`mame/b4_cmd58_inject.dbg`:** fault injection. It forces the CMD58 result to non-zero at $E02118 during an SD boot.
- **`libtest/`:** a C program linked against the v2.42 libs (D-2, D-4, D-6, D-8, D-12, D-5). Copy it to `code/software/m8b_libtest/` and run `make` in the docker image. The entry point is `kmain`.
- **Not testable in this MAME build:** V9958/Xosera hardware (X-*, V-3 scroll path), Kermit transfer (B-2, needs a host kermit), slow SD cards (B-6).

## Pending-test round (2026-10-30)
- **`t_div.asm`:** A-2. Calls the ROM `__divsi3` and `__modsi3` directly.
- **A-9:** flip one byte of the zipped stage2 in `rosco_m68k.rom` (ROM offset $7DBE), then boot it with `rosco-test.sh -m rosco_m68k_010 <rom>`.
- **B-17:** SD image with a 0-byte ROSCODE1.BIN.
- **B-8:**
  - Disk image: build a sparse raw `.hd` image of about 129 GiB, passed as `-hard2` (the IDE master). Give it one MBR partition starting at LBA 2^28+2048 holding a FAT32 volume with `t_b8_REAL.bin` as ROSCODE1.BIN. Write a decoy FAT32 volume with `t_b8_WRAP.bin` at LBA 2048, outside the partition table. Write the volumes into the image with `dd ... seek=<lba> conv=notrunc,sparse`; mtools fails at offsets beyond 4 GiB.
  - Firmware: this needs a v2.42 build that adds `DEFINES:=$(DEFINES) -DROSCO_M68K_ATA` to `blockdev/include.mk`. Without it, IDE boot never works (B-19).
  - Running it: put the ROM in `<rompath>/rosco_m68k_010/rosco_m68k_242.rom` and use `-bios v242 -rompath <rompath>`. MAME warns about the checksum and runs anyway.
- **`inputtest/` plus `mame/input_harness.py`:** D-11 and D-1. The harness listens on a TCP port, starts MAME with `-bitb socket.127.0.0.1:<port>`, and types input into the console.
- **D-13 (gdb stub):** not testable here, because the host gdb has no m68k target.
