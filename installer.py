import os
import struct
import shutil
from tarfile import TarFile
from zipfile import ZipFile
import requests
import time

if os.name == "nt":
    gd_path = "geckodriver.exe"

    if os.path.isfile(os.path.join("harquery", gd_path)):
        print("Harquery dependencies are already installed")
        exit()

    if 8 * struct.calcsize("P") == 32:
        gd_url = "https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-win32.zip"
    elif 8 * struct.calcsize("P") == 64:
        gd_url = "https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-win64.zip"
    gd_dc = "zip"
    decompressor = ZipFile
else:
    gd_path = "geckodriver"

    if os.path.isfile(os.path.join("harquery", gd_path)):
        print("Harquery dependencies are already installed")
        exit()

    gd_url = "https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-macos.tar.gz"
    gd_dc = "tar.gz"
    decompressor = TarFile.open

bmp_url = "https://codeload.github.com/lightbody/browsermob-proxy/zip/browsermob-proxy-2.1.1"

if not os.path.isdir("temp"):
    os.mkdir("temp")

print("installing geckodriver v0.27.0...")

geckodriver = requests.get(gd_url, stream=True)
target_path = os.path.join("temp", "geckodriver.{0}".format(gd_dc))
with open(target_path, "wb") as f:
    for chunk in geckodriver.iter_content(chunk_size=128):
        f.write(chunk)

target_path = os.path.join("temp", "geckodriver.{0}".format(gd_dc))
gd_archive = decompressor(target_path)
gd_archive.extract(gd_path, "harquery")

gd_archive.close()

print("installing browsermob-proxy v2.1.1")

bmp = requests.get(bmp_url, stream=True)
target_path = os.path.join("temp", "browsermob-proxy-2.1.1.zip")
with open(target_path, "wb") as f:
    for chunk in bmp.iter_content(chunk_size=128):
        f.write(chunk)

target_dir = "browsermob-proxy-browsermob-proxy-2.1.1"
bmp_archive = ZipFile(target_path)
bmp_archive.extractall("harquery")

from_path = os.path.join("harquery", "browsermob-proxy-browsermob-proxy-2.1.1")
to_path = os.path.join("harquery", "browsermob-proxy-2.1.1")
os.rename(from_path, to_path)

bmp_archive.close()
shutil.rmtree("temp")



