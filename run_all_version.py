#!/usr/bin/env python3

from zipfile import ZipFile
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

def show_help():
    print(textwrap.dedent(f"""
        This runs a command on all versions of sqlite3.exe in the "archive" folder.

        To use, run a command like:
        {sys.argv[0]} "sqlite3 < test.sql"

        'sqlite3' will automatically be replaced with each filename in turn.
        Multiple commands can be run, separated by a semicolon.  The special
        command "reset" will remove any files that were created in the current
        folder after a run.

        Use --debug to use debug executables.
    """))

def run_sqlite(temp_fn, args, current_files):
    cmd = args[0].replace("sqlite3", temp_fn)
    for sub_cmd in cmd.split(";"):
        if sub_cmd.strip().lower() == "reset":
            for test in os.listdir("."):
                if os.path.isfile(test) and test not in current_files:
                    os.unlink(test)
        else:
            ret = subprocess.call(sub_cmd, shell=True)
            if ret != 0:
                print("EXIT CODE: " + str(ret))

def enum_versions():
    with open("versions.jsonl") as f:
        for row in f:
            if len(row):
                yield json.loads(row)

def main():
    args = [x for x in sys.argv[1:] if x not in {"--debug"}]
    debug = "--debug" in sys.argv[1:]

    if len(args) != 1:
        show_help()
        exit(1)

    if debug:
        r = re.compile("sqlite-shell-win-debug-([0-9]+).zip")
    else:
        r = re.compile("sqlite-(shell-win32-x86-|tools-win32-x86-|)[0-9._]+zip")

    for dir_name, date, ver in enum_versions():
        archive_names = [x for x in os.listdir(os.path.join("archive", dir_name)) if r.search(x)]
        if archive_names:
            with ZipFile(os.path.join("archive", dir_name, archive_names[0])) as zf:
                zip_files = [x for x in zf.namelist() if x.endswith("sqlite3.exe")]
                if zip_files:
                    temp_fn = f"temp_sqlite3_{ver}.exe"
                    with open(temp_fn, "wb") as f_dest, zf.open(zip_files[0], "r") as f_src:
                        shutil.copyfileobj(f_src, f_dest)

                    current_files = set(x for x in os.listdir(".") if os.path.isfile(x))
                    print("", flush=True)
                    print(f"# {ver}{' (debug)' if debug else ''}, released {date}", flush=True)
                    run_sqlite(temp_fn, args, current_files)
                    os.unlink(temp_fn)

if __name__ == "__main__":
    main()
