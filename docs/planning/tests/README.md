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
