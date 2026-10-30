; helpers: PRINT string at A0 (TRAP 14 fn 0), PRHEX D2.L as 8 hex digits
PRINTS  macro
        lea     \1,A0
        moveq   #0,D1
        trap    #14
        endm
        bra     START
PRHEX:  movem.l D0-D3,-(A7)
        moveq   #7,D3
.l:     rol.l   #4,D2
        move.l  D2,D0
        and.l   #$F,D0
        move.b  HEX(PC,D0.w),D0
        moveq   #2,D1
        trap    #14
        dbra    D3,.l
        movem.l (A7)+,D0-D3
        rts
HEX:    dc.b    "0123456789ABCDEF"
        even
DONE:   PRINTS  S_END
.h:     bra.s   .h
S_END:  dc.b    13,10,"#END#",13,10,0
        even
