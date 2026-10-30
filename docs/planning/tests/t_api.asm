        org     $40000
        include "common.inc"
START:
; T-A1: DEVICE_CTRL on device 0 with D2=$BB (doc: param in D2.L)
        PRINTS  S_A1
        lea     DEVBUF,A0
        moveq   #0,D0
        moveq   #9,D1               ; GET_DEVICE
        trap    #14
        move.l  D0,D2
        bsr     PRHEX
        lea     DEVBUF,A0
        moveq   #0,D0               ; command 0 = set baud
        move.l  #$BB,D2
        moveq   #16,D1              ; DEVICE_CTRL
        trap    #14
        move.l  D0,D2
        PRINTS  S_RES
        bsr     PRHEX
; T-K2: register + remove IRQ via kernel API at ($400)
        PRINTS  S_K2
        move.w  SR,D2
        bsr     PRHEX
        move.l  $400,A2             ; IKernel*
        pea     HANDLER
        move.l  #5,-(A7)
        move.l  44(A2),A1           ; register_irq
        jsr     (A1)
        addq.l  #8,A7
        PRINTS  S_REG
        move.w  SR,D2
        bsr     PRHEX
        move.w  $1cd2,D2
        bsr     PRHEX
        pea     HANDLER
        move.l  48(A2),A1           ; remove_irq
        jsr     (A1)
        addq.l  #4,A7
        PRINTS  S_REM
        move.w  SR,D2
        bsr     PRHEX
        PRINTS  S_CNT
        move.w  $1cd2,D2
        bsr     PRHEX
; restore interrupts so console keeps working
        move.w  #$2000,SR
        bra     DONE
HANDLER: dc.l   0,0,0,ISR
ISR:    moveq   #0,D0
        rts
DEVBUF: ds.b    32
S_A1:   dc.b    13,10,"#A1 GET_DEVICE=",0
S_RES:  dc.b    " DEVICE_CTRL ret=",0
S_K2:   dc.b    13,10,"#K2 SR before=",0
S_REG:  dc.b    " after register SR=",0
S_REM:  dc.b    13,10,"#K2 after remove SR=",0
S_CNT:  dc.b    " disable_intr_count=",0
        even
