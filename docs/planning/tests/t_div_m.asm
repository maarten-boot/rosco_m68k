        org     $40000
        include "common.inc"
DIVSI3  equ     $E0157C
MODSI3  equ     $E015AE
CALL2   macro                   ; \1=func \2=a \3=b
        move.l  #\3,-(A7)
        move.l  #\2,-(A7)
        jsr     \1
        addq.l  #8,A7
        move.l  D0,D2
        bsr     PRHEX
        endm
START:
        PRINTS  S1
        CALL2   DIVSI3,-7,2
        PRINTS  S2
        CALL2   MODSI3,-7,2
        PRINTS  S3
        CALL2   DIVSI3,7,-2
        PRINTS  S4
        CALL2   DIVSI3,100,7
        bra     DONE
S1:     dc.b    13,10,"#A2 -7/2=",0
S2:     dc.b    " (expect FFFFFFFD)  -7%2=",0
S3:     dc.b    " (expect FFFFFFFF)  7/-2=",0
S4:     dc.b    " (expect FFFFFFFD)  100/7=",0
        even
