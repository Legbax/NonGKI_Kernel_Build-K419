#!/usr/bin/env python3
# GhostBuster .nomedia FUSE mtime/ctime fixup: push the spoofed .nomedia timestamps past
# FUSE's writeback-cache. susfs propagates the spoofed_ino to the FUSE inode but FUSE keeps
# the local (real) i_mtime when writeback_cache is on. This forces i_mtime/i_ctime/i_atime
# from the matching SUS_KSTAT_HLIST entry (by spoofed_ino) in fuse_change_attributes_common.
import os, re, sys

# 1) fs/susfs.c: append the global helper (scans the kstat hlist by spoofed_ino)
sc = "fs/susfs.c"; s = open(sc).read()
if "susfs_sus_kstat_fuse_fixup_times" not in s:
    helper = r'''

#ifdef CONFIG_KSU_SUSFS_SUS_KSTAT
/* GhostBuster: defeat FUSE writeback-cache for the spoofed .nomedia timestamps. */
void susfs_sus_kstat_fuse_fixup_times(struct inode *inode) {
	struct st_susfs_sus_kstat_hlist *entry;
	int bkt;
	unsigned long ino;
	if (!inode)
		return;
	ino = inode->i_ino;
	rcu_read_lock();
	hash_for_each_rcu(SUS_KSTAT_HLIST, bkt, entry, node) {
		if (entry->info.spoofed_ino == ino) {
			inode->i_mtime.tv_sec  = entry->info.spoofed_mtime_tv_sec;
			inode->i_mtime.tv_nsec = entry->info.spoofed_mtime_tv_nsec;
			inode->i_ctime.tv_sec  = entry->info.spoofed_ctime_tv_sec;
			inode->i_ctime.tv_nsec = entry->info.spoofed_ctime_tv_nsec;
			inode->i_atime.tv_sec  = entry->info.spoofed_atime_tv_sec;
			inode->i_atime.tv_nsec = entry->info.spoofed_atime_tv_nsec;
			break;
		}
	}
	rcu_read_unlock();
}
#endif
'''
    open(sc, "w").write(s + helper); print("[GB] fs/susfs.c: appended fuse fixup helper")
else:
    print("[GB] fs/susfs.c: helper already present")

# 2) fs/fuse/inode.c: call the fixup at the end of fuse_change_attributes_common
fi = "fs/fuse/inode.c"; s = open(fi).read()
if "susfs_sus_kstat_fuse_fixup_times" in s:
    print("[GB] fuse/inode.c: call already present"); sys.exit(0)
anchor = "\tfi->orig_ino = attr->ino;"
if anchor not in s:
    print("[GB] FATAL: 'fi->orig_ino = attr->ino;' anchor not found in", fi); sys.exit(1)
call = ('#ifdef CONFIG_KSU_SUSFS_SUS_KSTAT\n'
        '\t{ extern void susfs_sus_kstat_fuse_fixup_times(struct inode *inode);\n'
        '\t  susfs_sus_kstat_fuse_fixup_times(inode); }\n'
        '#endif\n')
s = s.replace(anchor, call + anchor, 1)
open(fi, "w").write(s); print("[GB] fuse/inode.c: inserted fixup call before orig_ino")
