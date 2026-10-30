# M3c — kernel, video, easy68k, debug_stub review (v2.42)

_Source: review agent, 2026-10-30; static reading only. Paths relative to `code/firmware/rosco_m68k_firmware/`._
_✔ = spot-checked by the main session against the v2.42 source._
_Build note (main session): the default v2.42 build includes the ROM kernel (unless NO_KERNEL=true), V9958 (unless WITH_VDP=false) and Xosera ANSI (unless XOSERA_ANSI_CON=false). The firmware debug_stub is only included with WITH_DEBUG_STUB=true._
_Debug-stub IDs renamed S-x (agent used D-x, which clashes with M3d)._

## Kernel
| ID | Title | Location | Cat | Sev | Conf | Develop |
|----|-------|----------|-----|-----|------|---------|
| K-1 ✔ | task_done sets current_task=NULL then suspend stores SP at NULL+$10 → **overwrites illegal-instruction vector**; also enables IRQs before yield | kernel/sched.c:71-90; kernel/task.asm:299-306 | bug | high | high | no |
| K-2 ✔ | `irq_remove`: `bra list_node_delete` skips `enable_interrupts` → IRQs stay masked, nesting count leaks | kernel/kmachine.asm:296-300 | bug | medium | high | no |
| K-3 ✔ | KERNEL_API_ADDRESS = 0x400 = SDB_MAGIC → kernel init overwrites SDB magic after boot | kernel/include/kernelapi.h:27; kernel/api.c:49 | bug | medium | high | no |
| K-4 | Kernel re-initialised on every warm boot; 2nd irq_init chains IRQ vectors to themselves → recursion on any autovector IRQ | main1.c:138-141; kernel/kmachine.asm:83-136 | bug | medium | medium | no |
| K-5 | slab_alloc after failed bitmap search: dirty d0 → ~65k-iteration loop per partial slab, slabs never reused | kernel/slab.asm:85-96; kernel/bitmap.asm:279-292 | bug | medium | high | no |
| K-6 | slab_free never moves full slab back to partial; init Task pmm_alloc'd but slab_free'd | kernel/slab.asm:148-158,197-239; sched.c:152 | bug | medium | high | no |
| K-7 | task_wait/task_signal: no pending-signal latch (lost wake-up, documented) | kernel/task.asm:351-473 | todo | medium | high | no |
| K-8 | pmm_free sorts with stale size after coalesce | kernel/pmm.c:142-153 | bug | low | high | no |
| K-9 | Minor: 68010-only frames; TRACE build compile error; README typo; VBR assumed 0; irq_register no range check; prio 4 masked to 0; PMM gets no RAM | various | low | low | high | no |

## EASy68K (TRAP #15)
| ID | Title | Location | Cat | Sev | Conf | Develop |
|----|-------|----------|-----|-----|------|---------|
| E-1 ✔ | Task > 20: `rte` with saved D0 still on stack → crash; range check on D0.L not D0.B | easy68k/syscalls_asm.asm:35-46 | bug | high | high | no |
| E-2 | Signed output of 0 prints nothing (tasks 3,17,20); INT_MIN prints "-" | easy68k/syscalls.c:20-37 | bug | high | high | no |
| E-3 ✔ | Task 16 uses `move.b 0,X` / `move.b 1,X` (absolute, not `#`) → prompt/LF can never be re-enabled | easy68k/syscalls_asm.asm:332-344 | bug | medium | high | no |
| E-4 | Task 8 returns heartbeat down-counter ($408) not uptime ($40C); D1 upper word stale | easy68k/syscalls_asm.asm:265-267 | bug/doc | medium | high | no |
| E-5 | Task 7 stub on r2.x ("TODO else for r2X"); all input via RECVCHAR, keyboard ignored | easy68k/syscalls_asm.asm:246-261 | missing | medium | high | partial |
| E-6 | Task 11 / ANSI_MOVEXY sends 0-based row/col to 1-based ESC[r;cH → off by one | ansicon.asm:16-46 | bug | medium | high | unknown |
| E-7 | Missing tasks (10,19,21-23,32,33,50+,51-59,80+); no line editing; regs A1/D1 clobbered; flags persist across programs; task 9 ignores EFP_HALT | various | missing | low | high | no |

## V9958 (video9958/vdpcon.asm)
| ID | Title | Location | Cat | Sev | Conf | Develop |
|----|-------|----------|-----|-----|------|---------|
| V-1 | CLRSCR calls BUFFERFLIP with caller's A0 instead of VDP base → ~1.9 KB written to arbitrary memory | :255-273 | bug | high | high | no |
| V-2 | CLRSCR doesn't reset DISPLAYSTART | :263 | bug | medium | high | no |
| V-3 | Scroll path `adda.l D1,A1` with dirty upper D1 → 80-byte zero write anywhere | :486,595 | bug | high | med-high | no |
| V-4 | Backspace at CURPOS 0 after wrap writes BUFFER-1 | :515-551 | bug | low | medium | no |
| V-5 | No MOVEXY, no ANSI interpretation, LF ignored, TAB/BEL unhandled, CLEARDATA 2 bytes over, 10 MHz delays | various | missing | low-med | high | no |

## Xosera ANSI (videoXoseraANSI/xosera_ansiterm_m68k.c)
| ID | Title | Location | Cat | Sev | Conf | Develop |
|----|-------|----------|-----|-----|------|---------|
| X-1 | `xansi_clear(start==end)` → count 0xFFFF → clears all 64K VRAM (ESC[K at last col, ESC[1K at col 0) | :331-370,1224-1255 | bug | high | high | no |
| X-2 | EL/ED ranges off by one (last column / cursor cell not erased) | :1210-1251 | bug | medium | high | no |
| X-3 | ESC E compares y with cols instead of rows | :970-977 | bug | medium | high | no |
| X-4 | CSI parser drops empty leading param (`ESC[;5H`); 16-bit param wrap | :1564-1597 | bug | medium | high | no |
| X-5 | DECSCNM ?5h/?5l both toggle; visualbell loop bound uses address | :1097-1107 | bug | low-med | high | no |
| X-6 | Doc says CSI ?20h, code needs CSI 20h | ANSI_REFERENCE.md vs :1157-1172 | doc | low-med | high | no |
| X-7 | Delayed-wrap flag mishandled (blank line after full line+CRLF; off-screen cursor on last row; SGR resets position) | :286-326,737-831 | bug | medium | medium | no |
| X-8 | SGR gaps: truecolour sets colour 8, 22/24/27 ignored, 8-15 unmapped, multi-param private modes | various | missing | low | high | no |
| X-9 | Scroll-down blitter path possibly off by one | :693-734 | bug | low | low | unknown |
| X-10 | Query replies/cursor blink only on RECVCHAR/CHECKCHAR, not INPUTCHAR (keyboard) | xosera_ansiterm_init.asm:50-130 | bug | medium | medium | yes (44574b3) |
| X-11 | Minor: PRINTLN(0) reads NULL; memclear n=0 loops forever; unbounded vblank waits; controls inside CSI eaten | various | low | low | high | no |

## debug_stub (firmware, WITH_DEBUG_STUB only)
| ID | Title | Location | Cat | Sev | Conf | Develop |
|----|-------|----------|-----|-----|------|---------|
| S-1 | Dump dereferences faulting PC unguarded → double fault/halt on odd/unmapped PC | debug_stub/debug_stub.asm:117-124,159-160 | bug | medium | med-high | no |
| S-2 | Stack-frame offsets 68010-only | debug_stub/debug_stub.asm:117-125 | bug | low-med | high | yes (c899e46) |

## Not fully checked
Xosera register defs vs hardware version; font.asm; kernel tests; SIG_IMMED; VDP/Xosera timing at r2.x clock; real blitter semantics; kernel on 68020; $500-$C8A data block layout vs other users.
