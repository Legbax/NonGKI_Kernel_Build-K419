#!/usr/bin/env python3
# Insert the CMD_SUSFS_ADD_CLOCK_OFFSET case into the KSU susfs supercall dispatch
# (switch(cmd){ case CMD_SUSFS_*: susfs_*(arg); return 0; } in kernel/supercall/supercall.c).
import sys, os, re, subprocess
snip = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "core_hook_clock_offset.snippet")).read()
# find the file with the susfs dispatch switch (has 'case CMD_SUSFS_ADD_SUS_PATH')
out = subprocess.run("grep -rl 'case CMD_SUSFS_ADD_SUS_PATH' --include=*.c .",
                     shell=True, capture_output=True, text=True).stdout.split()
if not out:
    # broaden: any file dispatching CMD_SUSFS
    out = subprocess.run("grep -rl 'CMD_SUSFS_ADD_SUS_KSTAT' --include=*.c .",
                         shell=True, capture_output=True, text=True).stdout.split()
if not out:
    print("[GB] FATAL: no susfs dispatch (.c with CMD_SUSFS_ADD_SUS_PATH) found"); 
    print("[GB] diag: files with CMD_SUSFS:"); 
    print(subprocess.run("grep -rln 'CMD_SUSFS' --include=*.c . | head", shell=True, capture_output=True, text=True).stdout)
    sys.exit(1)
f = out[0]; s = open(f).read()
print("[GB] susfs dispatch file:", f)
if 'CMD_SUSFS_ADD_CLOCK_OFFSET' in s:
    print("[GB] CLOCK_OFFSET case already present"); sys.exit(0)
# insert the CLOCK_OFFSET case right before the first 'case CMD_SUSFS_ADD_SUS_PATH:'
m = re.search(r'\n([ \t]*)case CMD_SUSFS_ADD_SUS_PATH:', s)
if not m:
    print("[GB] FATAL: anchor 'case CMD_SUSFS_ADD_SUS_PATH:' not found"); sys.exit(1)
ins_at = m.start() + 1  # after the preceding newline
s = s[:ins_at] + snip + s[ins_at:]
open(f, 'w').write(s)
print("[GB] inserted CLOCK_OFFSET case before CMD_SUSFS_ADD_SUS_PATH in", f)
