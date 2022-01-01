#!/usr/bin/env python3

import os
from zipfile import ZipFile
import re
import subprocess
import sys

args = [x for x in sys.argv[1:] if x not in {"--debug"}]
debug = "--debug" in sys.argv[1:]

if len(args) != 1:
    print(f"""
This runs a command on all versions of sqlite3.exe in the "archive" folder.

To use, run a command like:
{sys.argv[0]} "sqlite3 < test.sql"

'sqlite3' will automatically be replaced with each filename in turn.
Use --debug to use debug executables.
""")
    exit(1)

if debug:
    r = re.compile("sqlite-shell-win-debug-([0-9]+).zip")
else:
    r = re.compile("sqlite-(shell-win32-x86-|tools-win32-x86-|)3[0-9._]+zip")

for cur in os.listdir("archive"):
    ver = cur
    found = False
    cur = os.path.join("archive", cur)
    for x in os.listdir(cur):
        if r.search(x):
            with ZipFile(os.path.join(cur, x)) as zf:
                for inzip in zf.namelist():
                    if inzip.endswith("sqlite3.exe"):

                        fn = f"temp_{ver}_sqlite3.exe"
                        with zf.open(inzip, "r") as f_src:
                            with open(fn, "wb") as f_dest:
                                f_dest.write(f_src.read())

                        print("", flush=True)
                        print(f"----- Running on {ver}{' (debug)' if debug else ''} -----", flush=True)
                        subprocess.check_call([fn, "--version"])
                        cmd = args[0].replace("sqlite3", fn)
                        subprocess.call(cmd, shell=True)
                        os.unlink(fn)

                        break
