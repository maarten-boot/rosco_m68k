# Flash tests (M12, rosco-emulator branch `feature/sst-flash`)

These need the emulator built from `../rosco-emulator` branch `feature/sst-flash`, which models the ROM as 2 × SST39SF040.

- **`flash_program_test.c`** (build it like `tests/libtest/`, against the v2.42.1 libs):
  - reads the chip IDs;
  - erases sector 127 on both chips, programs a pattern and verifies it through normal CPU reads.
  - Run it twice with the same `-nvram_directory`: the second run must report "pattern already present".
- **`updateflash_harness.py`**: the end-to-end update test.
  - Boots `rosco_m68k_010 -bios v242` from an SD image holding `ROSCODE1.BIN` = `updateflash.bin` and `rosco_m68k.rom` = the 2.42.1 image.
  - Answers the ENTER/Y prompts over a socket console.
  - Prints the console output from "flash update in progress" up to the next boot.
  - Arguments: `emu sdimage port cwd rompath nvramdir`.
