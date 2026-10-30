        org     $40000
        include "common.inc"
START:
        PRINTS  S_K4
        move.l  $6C,D2              ; VEC_IRQ3
        bsr     PRHEX
        PRINTS  S_OLD
        move.l  $1CDC,D2            ; old_irq3
        bsr     PRHEX
        PRINTS  S_EXIT
        move.l  $490,A0             ; EFP_PROG_EXIT -> warm boot
        jmp     (A0)
S_K4:   dc.b    13,10,"#K4 VEC_IRQ3=",0
S_OLD:  dc.b    " old_irq3=",0
S_EXIT: dc.b    " -> exit to warm boot",13,10,0
        even
