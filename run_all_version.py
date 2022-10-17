#!/usr/bin/env python3

import os
from zipfile import ZipFile
import re
import subprocess
import sys
import json

args = [x for x in sys.argv[1:] if x not in {"--debug"}]
debug = "--debug" in sys.argv[1:]

if len(args) != 1:
    print(f"""
This runs a command on all versions of sqlite3.exe in the "archive" folder.

To use, run a command like:
{sys.argv[0]} "sqlite3 < test.sql"

'sqlite3' will automatically be replaced with each filename in turn.
Multiple commands can be run, separated by a semicolon.  The special
command "reset" will remove any files that were created in the current
folder after a run.

Use --debug to use debug executables.
""")
    exit(1)

SHOW_VERSION_INFO = False

if debug:
    r = re.compile("sqlite-shell-win-debug-([0-9]+).zip")
else:
    r = re.compile("sqlite-(shell-win32-x86-|tools-win32-x86-|)3[0-9._]+zip")

versions = {}
if SHOW_VERSION_INFO:
    with open("versions.jsonl") as f:
        for cur in f:
            dir_name, date, ver = json.loads(cur)
            versions[dir_name] = f"{ver} ({date})"

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
                        sqlite_ver = subprocess.check_output([fn, "--version"]).decode("utf-8").strip()
                        if SHOW_VERSION_INFO:
                            print(f"# {versions.get(ver, ver)}", flush=True)
                        print(f"# {sqlite_ver}{' (debug)' if debug else ''}", flush=True)

                        files = set(x for x in os.listdir(".") if os.path.isfile(x))
                        cmd = args[0].replace("sqlite3", fn)
                        for sub_cmd in cmd.split(";"):
                            if sub_cmd.strip().lower() == "reset":
                                for test in os.listdir("."):
                                    if os.path.isfile(test) and test not in files:
                                        os.unlink(test)
                            else:
                                ret = subprocess.call(sub_cmd, shell=True)
                                if ret != 0:
                                    print("EXIT CODE: " + str(ret))
                        os.unlink(fn)

                        break
