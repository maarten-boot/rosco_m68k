        org     $40000
        include "common.inc"
START:
        PRINTS  S_K1
        move.l  $10,D2
        bsr     PRHEX
        move.l  $400,A2             ; IKernel*
        move.l  A2,APIP
; give the PMM 64 KiB at $80000 (firmware gives it none, K-9g)
        move.l  #$10000,-(A7)
        move.l  #$80000,-(A7)
        move.l  4(A2),A1            ; mem_free
        jsr     (A1)
        addq.l  #8,A7
; start(init_stack, 4K, INIT, idle_stack, 4K, IDLE)
        pea     IDLE
        move.l  #$1000,-(A7)
        move.l  #$70000,-(A7)
        pea     INIT
        move.l  #$1000,-(A7)
        move.l  #$72000,-(A7)
        move.l  80(A2),A1           ; start
        jsr     (A1)
        bra     DONE
INIT:   rts                         ; init task returns at once -> task_done
IDLE:   move.l  #200000,D3
.w:     subq.l  #1,D3
        bne.s   .w
        PRINTS  S_AFT
        move.l  $10,D2
        bsr     PRHEX
        bra     DONE
APIP:   dc.l    0
S_K1:   dc.b    13,10,"#K1 illegal-instr vector ($10) before=",0
S_AFT:  dc.b    13,10,"#K1 after init task returned, ($10)=",0
        even
