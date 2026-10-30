        org     $40000
        include "common.inc"
START:
        PRINTS  S_R
        moveq   #7,D0               ; no input yet -> expect 0
        trap    #15
        moveq   #0,D2
        move.b  D1,D2
        bsr     PRHEX
        PRINTS  S_W
.poll:  moveq   #7,D0
        trap    #15
        tst.b   D1
        beq.s   .poll               ; wait until task 7 reports input
        moveq   #5,D0               ; read it (task 5 -> D1.B)
        trap    #15
        moveq   #0,D2
        move.b  D1,D2
        PRINTS  S_G
        bsr     PRHEX
        bra     DONE
S_R:    dc.b    13,10,"#E5 task7 before input=",0
S_W:    dc.b    13,10,"#E5 waiting",0
S_G:    dc.b    13,10,"#E5 task7 saw input, char=",0
        even
