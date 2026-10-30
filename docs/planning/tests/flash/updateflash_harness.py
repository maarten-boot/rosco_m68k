import socket, subprocess, sys, time, re
emu, img, port, cwd, rompath, nv = sys.argv[1:7]
srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", int(port))); srv.listen(1)
p = subprocess.Popen([emu, "rosco_m68k_010", "-bios", "v242", "-rompath", rompath, "-nvram_directory", nv,
    "-skip_gameinfo", "-hard1", img, "-terminal", "null_modem", "-bitb", f"socket.127.0.0.1:{port}",
    "-video", "none", "-sound", "none", "-seconds_to_run", "200", "-nothrottle"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=cwd)
srv.settimeout(30); c, _ = srv.accept(); c.settimeout(0.2)
out = b""; t0 = time.time(); stage = 0
while time.time() - t0 < 240:
    try:
        d = c.recv(4096)
        if d: out += d
    except socket.timeout: pass
    if stage == 0 and b"press ENTER" in out: time.sleep(0.5); c.send(b"\r"); stage = 1
    elif stage == 1 and b'press "Y"' in out: time.sleep(0.5); c.send(b"Y"); stage = 2
    elif stage == 2 and out.count(b"Update Utility") >= 2: time.sleep(0.5); break
p.terminate(); p.wait(timeout=30)   # terminate (not kill) so MAME writes the nvram
txt = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out.decode("latin1")).replace("\r", "")
keep = [l for l in txt.split("\n") if re.search(r"Classic|ROM is|Logical|Found an update|indicates version|progress|flash|Flash|reboot|Oh dear|CPU @", l)]
i = txt.find("in progress"); j = txt.find("Update Utility", i)
print("\n".join(l for l in txt[i:j].split("\n") if l.strip()))
