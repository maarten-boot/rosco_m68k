        org     $40000
        include "common.inc"
START:
; T-A12: PRINT should preserve D0
        move.l  #$DEADBEEF,D0
        lea     S_A12,A0
        moveq   #0,D1
        trap    #14
        move.l  D0,D2
        bsr     PRHEX
; T-E2: task 3 prints signed D1 = 0
        PRINTS  S_E2
        moveq   #0,D1
        moveq   #3,D0
        trap    #15
        PRINTS  S_E2B
        move.l  #42,D1
        moveq   #3,D0
        trap    #15
        PRINTS  S_CLOSE
; T-E4: task 8 ticks, twice ~0.3s apart
        PRINTS  S_E4
        moveq   #8,D0
        trap    #15
        move.l  D1,D2
        bsr     PRHEX
        move.l  #150000,D3
.w:     subq.l  #1,D3
        bne.s   .w
        PRINTS  S_SP
        moveq   #8,D0
        trap    #15
        move.l  D1,D2
        bsr     PRHEX
        PRINTS  S_UP
        move.l  $40C,D2
        bsr     PRHEX
; T-E8: A0 must survive TRAP 15 (task 6 = send char)
        PRINTS  S_E8
        move.l  #$12345678,A0
        move.l  #'*',D1
        moveq   #6,D0
        trap    #15
        move.l  A0,D2
        bsr     PRHEX
; T-E1: task 21 (out of range) - should return
        PRINTS  S_E1
        move.l  A7,D2
        bsr     PRHEX
        moveq   #21,D0
        trap    #15
        PRINTS  S_E1OK
        move.l  A7,D2
        bsr     PRHEX
        bra     DONE
S_A12:  dc.b    13,10,"#A12 D0 after PRINT=",0
S_E2:   dc.b    13,10,"#E2 zero=[",0
S_E2B:  dc.b    "] 42=[",0
S_CLOSE: dc.b   "]",0
S_E4:   dc.b    13,10,"#E4 task8=",0
S_SP:   dc.b    " then ",0
S_UP:   dc.b    " SDB_UPTICKS=",0
S_E8:   dc.b    13,10,"#E8 A0 after trap15 (was 12345678)=",0
S_E1:   dc.b    13,10,"#E1 before trap15 #21 SP=",0
S_E1OK: dc.b    13,10,"#E1 returned SP=",0
        even
