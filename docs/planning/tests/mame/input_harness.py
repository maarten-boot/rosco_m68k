import socket, subprocess, sys, time, re
emu, binf, port = sys.argv[1], sys.argv[2], int(sys.argv[3])
srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", port)); srv.listen(1)
dbg = f"{sys.argv[4]}/inp.dbg"
open(dbg, "w").write(f"gtime #5000\nload {binf},0x40000\npc=0x40000\ngo\n")
p = subprocess.Popen([emu, "rosco_m68k_010", "-bios", "v242", "-rompath", sys.argv[5], "-skip_gameinfo",
    "-terminal", "null_modem", "-bitb", f"socket.127.0.0.1:{port}", "-video", "none", "-sound", "none",
    "-seconds_to_run", "60", "-debug", "-debugger", "none", "-debugscript", dbg],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=sys.argv[4])
srv.settimeout(30); c, _ = srv.accept(); c.settimeout(0.2)
out = b""; t0 = time.time(); stage = 0
def pump():
    global out
    try:
        d = c.recv(4096)
        if d: out += d
    except socket.timeout: pass
while time.time() - t0 < 90:
    pump()
    if stage == 0 and b"#IN ready" in out:
        time.sleep(0.5)
        for ch in b"x" * 280 + b"\r":
            c.send(bytes([ch])); time.sleep(0.004)
        stage = 1
    elif stage == 1 and b"#D1 calling" in out:
        time.sleep(1.0); c.send(b"123\r"); stage = 2
    elif stage == 2 and b"#IN end" in out:
        time.sleep(0.3); pump(); break
p.kill()
txt = out.decode("latin1")
i = txt.find("#IN ready")
print(re.sub(r"x{20,}", lambda m: f"<x*{len(m.group())}>", txt[i:] if i >= 0 else txt[-1500:]))
