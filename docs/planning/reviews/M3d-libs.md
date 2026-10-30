# M3d — user libraries review (v2.42)

_Source: review agent, 2026-10-30; static reading + `make -n -p` only. Paths relative to `code/software/libs/`._
_✔ = spot-checked by the main session against the v2.42 source._

ABI check: TRAP 14 (0-13, 16-18) / TRAP 13 (0-4) function codes in machine.asm, SDB offsets ($40C, $414, $41C) and CharDevice layout all match InterfaceReference.md.

| ID | Title | Location (v2.42) | Cat | Sev | Conf | Fixed on develop |
|----|-------|------------------|-----|-----|------|------------------|
| D-1 ✔ | `e68PrintStrReadNumSigned` puts string ptr in D1, TRAP 15 task 18 expects A1 → prompt from garbage A1 | src/easy68k/easy68k.S:302-306 | api-mismatch | medium | high | no |
| D-2 | `memcpy` returns end pointer, not dest; `strncpy` inherits | src/cstdlib/string.c | bug | medium | high | no |
| D-3 | No memmove/memcmp/strstr/strtok/qsort/strtoul/strtod/puts/… → GCC-emitted memmove/memcmp fail to link | src/cstdlib | missing | medium | high | no |
| D-4 | `strtol` sets *endptr to s-1 on no-digits; only ' ' skipped as whitespace | src/cstdlib/stdlib.c | bug | low | high | no |
| D-5 | `heap_free` of physically last block reads past heap end (no `heap->end` check) → heap corruption; first block never coalesces | src/shmall/heap.c:94-100 | bug | medium | medium | no |
| D-6 | `calloc` multiply overflow unchecked; size 0xFFFFFFFF wraps; `realloc(p,0)` leaks | src/shmall/rosco_m68k.cpp | bug | low-med | high | no |
| D-7 ✔ | libm include.mk `find .` runs from libs/ → libm.a contains every lib's objects incl. float printf → `-lm` can silently override nofloat/softfloat printf; also `filter-out **/printf-*.o` is a no-op | src/libm/include.mk:1-2; Makefile | build | medium | high | no |
| D-8 | printf `%f` > PRINTF_MAX_FLOAT returns idx 0 (resets output); `%e/%g` don't consume va_arg; `%lld` consumes only long → following args misaligned | src/printf/printf.c (_ftoa ~372); printf_config.h | bug | medium | high | no |
| D-9 | init.S saves EFP_PROG_EXIT into .bss before `__kinit` zeroes it → vector restored as 0 | src/start_serial/init.S | bug | low | high | yes (f14e03c) |
| D-10 | `exit()` ignores status, not noreturn | src/cstdlib/stdlib.c | bug | low | medium | partial |
| D-11 | `readline` uint8_t index → >256-byte buffers overwrite start / never terminate; fgets no '\n', ignores EOF/stream | src/machine/basicio.c; src/cstdlib/fgets.c | bug | low-med | high | no |
| D-12 | vterm cursor left/right ANSI codes swapped; calloc(6)/calloc(10) too small; NULL derefs; ESC[6n blocks forever | src/vterm/vterm.c | bug | low-med | high | no |
| D-13 ✔ | gdb RingBuffer `mask` never initialised (0) → buffered input lost | src/gdb/gdb-support.c:31; buffer.asm | bug | low-med | high | no |
| D-14 | gdb ISR reads SRA/SRB as absolute addrs $2/$12; IMR misses RxRDY_A; VECADDR assumes VBR=0 | src/gdb/interrupt.asm | bug | low | high | no |
| D-15 | gdb `move.w d0,(a7)-` invalid EA in level-7 handler | src/gdb/m68k-stub-asm.asm:163 | bug | medium | high | yes (2b18fb2) |
| D-16 | debug_stub fault address offset only right for 68010 format 8 | src/debug_stub/debug_stub.asm | bug | low | high | yes (c899e46) |
| D-17 | sst_flash: wait() no timeout, no IRQ protection in lib, no verify, Tida TODO (sequences themselves correct) | src/sst_flash/sst.c | bug/todo | medium | medium | no |
| D-18 | Doc/header drift: `-lkernel` has no lib; KERNEL_API_ADDRESS 0x400 collides with SDB; no _EFP_PROG_EXIT/INPUTCHAR/CHECKINPUT in link scripts; magic typo; cache.asm signed `blt` skips 040/060; some stubs don't extend D0.B | various | doc/api | low | high | partial |

## Not fully checked
libm internals (`math_err.c` err=1 noted); fat_io_lib internals; nothing built/run (vasm acceptance of `(a7)-`, GCC use of memcpy return, bool return extension are reasoned).
