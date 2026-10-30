        org $40000
        include "common.inc"
START:  PRINTS S
        bra DONE
S:      dc.b 13,10,"#B8 loaded the WRAP kernel",0
        even
