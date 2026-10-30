#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <basicio.h>
#include <easy68k/easy68k.h>

static char buf[300];

void kmain(void) {
    printf("\r\n#IN ready\r\n");
    /* T-D11: readline with a 300-byte buffer; host sends 280 'x' + CR */
    memset(buf, '.', sizeof buf);
    int n = readline(buf, sizeof buf);
    printf("\r\n#D11 readline ret=%d strlen=%d first10=[%.10s] buf[256..265]=[%.10s]\r\n",
           n, (int)strnlen(buf, sizeof buf), buf, buf + 256);
    /* T-D1: prompt string must be printed, then a number read */
    printf("#D1 calling e68PrintStrReadNumSigned(\"PROMPT> \"): <");
    uint32_t v = e68PrintStrReadNumSigned("PROMPT> ");
    printf(">\r\n#D1 value=%ld (sent 123)\r\n#IN end\r\n", (long)v);
}
