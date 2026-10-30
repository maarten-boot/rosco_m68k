#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <vterm.h>
#include <machine.h>

static void d2(void) {
    char b[8];
    void *r = memcpy(b, "abc", 4);
    printf("#D2 memcpy ret==dest: %s (ret-dest=%d)\r\n", r == b ? "yes" : "NO", (int)((char*)r - b));
    char c[8];
    char *s = strncpy(c, "xy", 8);
    printf("#D2 strncpy ret==dest: %s\r\n", s == c ? "yes" : "NO");
}

static void d3(void) {
    char b[12] = "abcdefghij";
    memmove(b + 2, b, 6);       /* overlapping, dest above src */
    printf("#D3 memmove up   -> [%s] (expect ababcdefij)\r\n", b);
    memmove(b, b + 2, 6);       /* overlapping, dest below src */
    printf("#D3 memmove down -> [%s] (expect abcdefefij)\r\n", b);
    printf("#D3 memcmp: %d %d %d (expect 0 <0 >0)\r\n",
           memcmp("abc", "abc", 3), memcmp("abc", "abd", 3) < 0 ? -1 : 1, memcmp("abd", "abc", 3) > 0 ? 1 : -1);
}

static void d4(void) {
    const char *in = "abc";
    char *end = NULL;
    long v = strtol(in, &end, 10);
    printf("#D4 strtol(\"abc\") v=%ld end-in=%d (C std: 0)\r\n", v, (int)(end - in));
    v = strtol("\t42", &end, 10);
    printf("#D4 strtol(\"\\t42\") v=%ld (C std: 42)\r\n", v);
}

static void d8(void) {
    char b[48];
    memset(b, 0, sizeof b);
    int n = sprintf(b, "ab%fcd", 1e10);
    printf("#D8 sprintf(\"ab%%fcd\",1e10) n=%d strlen=%d buf=[%s]\r\n", n, (int)strlen(b), b);
    n = sprintf(b, "%lld|%d", (long long)7, 99);
    printf("#D8 sprintf(\"%%lld|%%d\",7LL,99) -> [%s] (expect 7|99)\r\n", b);
    const double vals[] = { 1e10, 1e-5, 123456.789, 9.99999e7, 1.0, 0.0 };
    for (unsigned i = 0; i < sizeof vals / sizeof vals[0]; i++) {
        sprintf(b, "%e", vals[i]);
        printf("#D8e %s\r\n", b);
    }
    n = sprintf(b, "%e|%d", 1.5, 99);
    printf("#D8 sprintf(\"%%e|%%d\",1.5,99) -> [%s] (expect 1.500000e+00|99)\r\n", b);
}

static void d12(void) {
    printf("#D12 vt_move_cursor_left(\"3\") emits: <");
    vt_move_cursor_left("3");
    printf("> (expect ESC[3D)\r\n");
    printf("#D12 vt_move_cursor_right(\"3\") emits: <");
    vt_move_cursor_right("3");
    printf("> (expect ESC[3C)\r\n");
}

static void d6(void) {
    void *p = calloc(0x10000, 0x10001);   /* overflows to 0x10000 */
    printf("#D6 calloc(0x10000,0x10001) = %p (expect NULL)\r\n", p);
}

static void d5(void) {
    enum { N = 2048 };
    static void *blk[N];
    int n = 0;
    while (n < N && (blk[n] = malloc(1024)) != NULL) n++;
    printf("#D5 allocated %d x 1KiB, last=%p\r\n", n, n ? blk[n-1] : NULL);
    void *tail = malloc(1);
    while (tail) { tail = malloc(1); }
    if (n) free(blk[n-1]);
    int ok = 0;
    for (int i = 0; i < 200; i++) {
        void *p = malloc(512);
        if (!p) break;
        memset(p, 0x5A, 512);
        free(p);
        ok++;
    }
    printf("#D5 after freeing last block: %d/200 malloc/free cycles ok\r\n", ok);
    for (int i = 0; i < n - 1; i++) free(blk[i]);
    void *big = malloc((size_t)(n - 1) * 1024);
    printf("#D5 re-alloc of all freed space: %p\r\n", big);
}

void kmain(void) {
    printf("\r\n#M8B libtest start\r\n");
    d2(); d3(); d4(); d8(); d12(); d6(); d5();
    printf("#M8B libtest end\r\n");

}
