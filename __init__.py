import os as __os

if __os.name == "nt":
    _geckodriver = "geckodriver.exe"
else:
    _geckodriver = "geckodriver"

__geckodriver_path = __os.path.join(
    __os.path.dirname(__file__), "geckodriver.exe")
if not __os.path.exists(__geckodriver_path):
    raise FileNotFoundError("Error: {0} not found".format(_geckodriver))

__bmp_path = __os.path.join(
    __os.path.dirname(__file__), "browsermob-proxy-2.1.1")
if not __os.path.exists(__bmp_path):
    raise FileNotFoundError("Error: browsermob-proxy not found")

from harquery.workspace import touch, Workspace

workspace = Workspace()

profiles = workspace.profiles
presets = workspace.presets
endpoints = workspace.endpoints
