#!/usr/bin/env python3
# Insert the CMD_SUSFS_ADD_CLOCK_OFFSET dispatch handler into the KSU core_hook.c
# (ReSukiSU/KernelSU style: arg2 == CMD_SUSFS_*), right after the OPEN_REDIRECT #endif.
import sys, os, re, subprocess
snip = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "core_hook_clock_offset.snippet")).read()
# find the core_hook.c that holds the susfs OPEN_REDIRECT handler
out = subprocess.run("grep -rl 'CONFIG_KSU_SUSFS_OPEN_REDIRECT' --include=core_hook.c .",
                     shell=True, capture_output=True, text=True).stdout.split()
cand = [f for f in out if 'arg2 == CMD_SUSFS' in open(f, errors='ignore').read()] or out
if not cand:
    print("[GB] FATAL: no core_hook.c with susfs dispatch found"); sys.exit(1)
f = cand[0]; s = open(f).read()
print("[GB] core_hook dispatch file:", f)
if 'CMD_SUSFS_ADD_CLOCK_OFFSET' in s:
    print("[GB] handler already present; nothing to do"); sys.exit(0)
m = re.search(r'#endif[^\n]*CONFIG_KSU_SUSFS_OPEN_REDIRECT[^\n]*\n', s)
if not m:
    print("[GB] FATAL: OPEN_REDIRECT #endif anchor not found in", f); sys.exit(1)
s = s[:m.end()] + snip + s[m.end():]
open(f, 'w').write(s)
print("[GB] inserted CLOCK_OFFSET handler after OPEN_REDIRECT #endif in", f)
