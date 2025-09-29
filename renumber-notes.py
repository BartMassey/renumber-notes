#!/usr/bin/python3
# Renumber lecture notes pages.
# Bart Massey 2021

import argparse, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--no-git-mv", help="use non-git `mv`", action="store_true")
ap.add_argument("--preview", help="just show moves", action="store_true")
ap.add_argument("-d", "--digits", help="number of digits in file prefix", type=int)
ap.add_argument("offset", help="[+<OFFSET>|-<OFFSET>] (default +1)", nargs="?")
ap.add_argument("start", help="first target file number (default 1)", nargs="?")
args = ap.parse_args()

git_mv = not args.no_git_mv

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
if off[0] == "+":
    off = off[1:]
try:
    dirn = int(off)
except:
    print("offset must be an integer", file=sys.stderr)
    exit(1)

files = set(os.listdir())

# Detect common invariant prefix across files
# Example: "02-1-intro.md", "02-2-basics.md" -> prefix is "02-"
def find_common_prefix(filenames):
    """Find longest common prefix that ends with a non-digit followed by digit"""
    if not filenames:
        return ""

    # Try different prefix lengths
    candidates = []
    for f in filenames:
        # Find all positions where we have pattern ending in non-digit + digit
        for i in range(len(f)):
            if i > 0 and not f[i-1].isdigit() and f[i:].lstrip() and f[i].isdigit():
                candidates.append(f[:i])

    if not candidates:
        return ""

    # Find the longest prefix that is common to all files
    for prefix_len in range(max(len(c) for c in candidates), 0, -1):
        for candidate in candidates:
            if len(candidate) >= prefix_len:
                prefix = candidate[:prefix_len]
                # Check if this prefix is common to all files
                if all(f.startswith(prefix) for f in filenames):
                    # Verify that after removing prefix, files still match \d+-
                    if all(re.match(r"^(\d+)-", f[len(prefix):]) for f in filenames if f.startswith(prefix)):
                        return prefix
    return ""

numbered_files = [f for f in files if re.match(r"^(\d+)-", f) or re.search(r"-(\d+)-", f)]
prefix = find_common_prefix(numbered_files) if numbered_files else ""

# Find all numbered files to determine appropriate digit width
max_num = 0
min_num = None
input_digits = {}  # Map from file number to its digit width
for f in files:
    # Remove prefix before matching
    fname = f[len(prefix):] if f.startswith(prefix) else f
    match = re.match(r"^(\d+)-", fname)
    if match:
        digit_str = match.group(1)
        num = int(digit_str)
        max_num = max(max_num, num)
        if min_num is None or num < min_num:
            min_num = num
        input_digits[num] = len(digit_str)

# Determine start number
if args.start:
    try:
        start = int(args.start)
        assert start >= 0
    except:
        print("start must be a non-negative integer", file=sys.stderr)
        exit(1)
elif min_num is not None:
    # Infer start from lowest-numbered file
    start = min_num
else:
    start = 1

# Determine output digit width
if args.digits:
    ndigits = args.digits
elif input_digits:
    # Use the maximum digit width found, expanded if necessary for offset
    max_after_offset = max_num + abs(dirn)
    ndigits = max(max(input_digits.values()), len(str(max_after_offset)))
else:
    ndigits = 2  # default to 2 digits if no numbered files found

i = start
while True:
    target = None
    # Try to find file with any digit width
    for f in files:
        if i in input_digits:
            # Remove prefix before matching
            fname = f[len(prefix):] if f.startswith(prefix) else f
            # Match file with the specific digit width it uses
            if re.match(f"^{i:0{input_digits[i]}}-", fname):
                target = f
                break
    if target is None:
        break
    # Replace with output digit width (keeping the prefix)
    fname = target[len(prefix):] if target.startswith(prefix) else target
    old_pattern = f"^{i:0{input_digits[i]}}-"
    new_fname = re.sub(old_pattern, f"{i+dirn:0{ndigits}}-", fname)
    new_name = prefix + new_fname
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
