#!/usr/bin/env python3

import os
from zipfile import ZipFile
import re
import subprocess
import sys

if len(sys.argv) != 2:
    print(f"""
This runs a command on all versions of sqlite3.exe in the "archive" folder.

To use, run a command like:
{sys.argv[0]} "sqlite3 < test.sql"

'sqlite3' will automatically be replaced with each filename in turn.
""")
    exit(1)

for cur in os.listdir("archive"):
    ver = cur
    found = False
    cur = os.path.join("archive", cur)
    for x in os.listdir(cur):
        if re.search("sqlite-(shell-win32-x86-|tools-win32-x86-|)3[0-9._]+zip", x):
            with ZipFile(os.path.join(cur, x)) as zf:
                for inzip in zf.namelist():
                    if inzip.endswith("sqlite3.exe"):

                        fn = f"temp_{ver}_sqlite3.exe"
                        with zf.open(inzip, "r") as f_src:
                            with open(fn, "wb") as f_dest:
                                f_dest.write(f_src.read())

                        print("")
                        print(f"-- Running on {ver} --")
                        subprocess.check_call([fn, "--version"])
                        cmd = sys.argv[1]
                        cmd = cmd.replace("sqlite3", fn)
                        subprocess.call(cmd, shell=True)
                        os.unlink(fn)

                        break
