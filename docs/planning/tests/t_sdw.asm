        org     $40000
        include "common.inc"
BLK     equ     50
START:
        PRINTS  S_I
        lea     CARD,A1
        moveq   #1,D0               ; SD_INIT
        trap    #13
        move.l  D0,D2
        bsr     PRHEX
        lea     BUF,A0              ; fill pattern
        move.w  #511,D3
.f:     move.b  D3,(A0)+
        dbra    D3,.f
        PRINTS  S_W
        move.l  #BLK,D1
        lea     CARD,A1
        lea     BUF,A2
        moveq   #3,D0               ; SD_WRITE_BLOCK
        trap    #13
        moveq   #0,D2
        move.b  D0,D2
        bsr     PRHEX
        lea     BUF2,A0             ; clear read buffer
        move.w  #127,D3
.c:     clr.l   (A0)+
        dbra    D3,.c
        PRINTS  S_R
        move.l  #BLK,D1
        lea     CARD,A1
        lea     BUF2,A2
        moveq   #2,D0               ; SD_READ_BLOCK
        trap    #13
        moveq   #0,D2
        move.b  D0,D2
        bsr     PRHEX
        lea     BUF,A0              ; compare
        lea     BUF2,A1
        move.w  #511,D3
        moveq   #0,D2
.cmp:   cmpm.b  (A0)+,(A1)+
        beq.s   .ok
        addq.l  #1,D2
.ok:    dbra    D3,.cmp
        PRINTS  S_C
        bsr     PRHEX
        bra     DONE
S_I:    dc.b    13,10,"#SDW init=",0
S_W:    dc.b    " write=",0
S_R:    dc.b    " read=",0
S_C:    dc.b    " mismatches=",0
        even
CARD:   ds.b    64
BUF:    ds.b    512
BUF2:   ds.b    512
