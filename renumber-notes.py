#!/usr/bin/python3
# Renumber lecture notes pages.
# Bart Massey 2021

import argparse, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("-g", "--git-mv", help="use `git move`", action="store_true")
ap.add_argument("--no-git-mv", help="do not use `git move`", action="store_true")
ap.add_argument("--preview", help="just show moves", action="store_true")
ap.add_argument("offset", help="[+<OFFSET>|-<OFFSET>] (default +1)", nargs="?")
ap.add_argument("start", help="first target file number (default 1)", nargs="?")
args = ap.parse_args()

git_mv = args.git_mv
if not args.git_mv and os.path.isdir(".git"):
    git_mv = True
if args.no_git_mv:
    git_mv = False
    
off = args.offset
if off and not re.match("^[+-][0-9]+$", off):
    if args.start:
        print("offset must be +number or -number", file=sys.stderr)
        exit(1)
    args.start = off
    off = "+1"
if not off:
    print("offset must be nonempty", file=sys.stderr)
    exit(1)
if off[1] == "+":
    off = off[1:]
try:
    dirn = int(off)
except:
    print("offset must be an integer", file=sys.stderr)
    exit(1)

start = 1
if args.start:
    try:
        start = int(args.start)
        assert start >= 0
    except:
        print("start must be a non-negative integer", file=sys.stderr)
        exit(1)

files = set(os.listdir())
i = start
while True:
    target = None
    for f in files:
        if re.match(f"{i:02}-", f):
            target = f
            break
    if target is None:
        break
    new_name = re.sub(f"{i:02}-", f"{i+dirn:02}-", target)
    if git_mv:
        if args.preview:
            print(f"git mv {target} {new_name}")
        else:
            assert os.system(f"git mv {target} {new_name}") == 0
    else:
        if args.preview:
            print(f"mv {target} {new_name}")
        else:
            os.rename(target, new_name)
    i += 1
