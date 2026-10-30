        org     $40000
        include "common.inc"
START:
; T-E3: task 16 - D1=0 prompt off, D1=1 prompt on; read PROMPT_ON ($411)
        PRINTS  S_E3
        moveq   #0,D1
        moveq   #16,D0
        trap    #15
        moveq   #0,D2
        move.b  $411,D2
        bsr     PRHEX
        PRINTS  S_E3B
        moveq   #1,D1
        moveq   #16,D0
        trap    #15
        moveq   #0,D2
        move.b  $411,D2
        bsr     PRHEX
; T-E6: task 11 D1=$0505 -> raw escape sequence goes to console
        PRINTS  S_E6
        move.w  #$0505,D1
        moveq   #11,D0
        trap    #15
        PRINTS  S_E6B
        bra     DONE
S_E3:   dc.b    13,10,"#E3 after task16 D1=0 PROMPT_ON=",0
S_E3B:  dc.b    " after D1=1 PROMPT_ON=",0
S_E6:   dc.b    13,10,"#E6 task11($0505) emits <",0
S_E6B:  dc.b    "> (EASy68K 0-based 5,5 -> expect ESC[6;6H)",0
S_SP:   dc.b    " ",0
        even
