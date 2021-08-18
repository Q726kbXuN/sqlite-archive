#!/usr/bin/env python3

from urllib.request import urlopen, urlretrieve
from urllib import parse
import re
from bs4 import BeautifulSoup
import os


def normalize_ver(ver):
    ver = ver.replace("_", ".")
    if "." in ver:
        ver = ver.split(".")
        ver = ver[0:1] + [f"{int(x):02d}" for x in ver[1:] if len(x)]
        ver = "".join(ver)
    ver += "0" * (7 - len(ver))
    return f"{ver[0]}.{ver[1:3]}.{ver[3:5]}.{ver[5:]}"


def main():
    url = "https://sqlite.org/download.html"
    data = urlopen(url).read()
    soup = BeautifulSoup(data, 'html.parser')

    # Find the version number
    r = re.compile("^sqlite-(amalgamation|source)-(?P<ver>3[0-9_.]+)")
    for link in soup.find_all('a', href=True):
        m = r.search(link.get_text())
        if m:
            ver = m.group('ver')
            break

    # Now that we have the version, pull out all of the links
    # Some are hidden by JS, so decode those
    r = re.compile("d391\\('(?P<a>a[0-9]+)','(?P<href>[^']+)'\\);")
    js = {}
    for m in r.finditer(data.decode("utf-8")):
        js[m.group('a')] = m.group('href')

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href == "hp1.html":
            href = js[link['id']]

        use = False
        if ver in href:
            for token in ["source", "amalgamation", "shell", "tools", "dll"]:
                if token in href:
                    use = True
            for token in ["html", "snapshot"]:
                if token in href:
                    use = False
        
        if use:
            dest_dir = os.path.join("archive", normalize_ver(ver))
            dest = os.path.join(dest_dir, href.split("/")[-1])
            if os.path.isfile(dest):
                print(f"{dest} already exists.")
            else:
                print(f"Downloading {dest}", flush=True, end="")
                os.makedirs(dest_dir, exist_ok=True)
                urlretrieve(parse.urljoin(url, href), dest)
                print(", done.")


if __name__ == "__main__":
    main()

