import os
from shutil import rmtree

from typing import Tuple, Any

from harquery.core import Profile
from harquery.endpoint import Headers, Endpoint
from harquery.errors import WorkspaceNotFoundError
from harquery.preset import FiltersPreset, HeadersPreset

class WorkspacePointer:
    __slots__ = ["_workspace", "_locator", "_extension", "_constructor"]
    def __init__(self, workspace: 'Workspace', locator: list, extension: str, constructor: object):
        self._workspace = workspace
        self._locator = locator
        self._constructor = constructor
        self._extension = extension

    def add(self, *args: Tuple[Any]) -> object:
        return self._constructor.new(self._workspace, *args)
    
    def drop(self, key: str) -> None:
        if key not in self:
            raise KeyError
        
        path_string = self._path_string(key)

        path = os.path.join(
            self._workspace.path, *self._locator, path_string)
        
        if self._extension is None:
            rmtree(path)
        else:
            os.remove(path)
        
        print("Removed {0}: '{1}'".format(self._locator[0][:-1], key))
    
    def _ftcheck(self) -> 'function':
        if self._extension is None:
            return os.path.isdir
        else:
            return os.path.isfile
    
    def _strf(self) -> 'function':
        if self._extension is None:
            return lambda x: x
        else:
            ext_len = len(self._extension)
            return lambda x: x[:-ext_len]

    def _path_string(self, key) -> str:
        if self._extension is None:
            return key
        else:
            return key + self._extension              

    def __getitem__(self, key: str) -> object:
        if key in self:
            return self._constructor(self._workspace, key)
        else:
            raise KeyError
    
    def __iter__(self) -> str:
        ftcheck = self._ftcheck()
        strf = self._strf()
        
        path = os.path.join(self._workspace._path, *self._locator)
        for item in os.listdir(path):
            if ftcheck(os.path.join(path, item)):
                yield strf(item)
    
    def __len__(self) -> int:
        ftcheck = self._ftcheck()
        strf = self._strf()
        
        path = os.path.join(self._workspace._path, *self._locator)
        count = 0
        for item in os.listdir(path):
            if ftcheck(os.path.join(path, item)):
                count += 1
        
        return count

    def __repr__(self) -> str:
        repr_str = ""

        count = 0
        for item in self:
            repr_str += "| " + item + "\n"
            count += 1
        
        if count == 0:
            repr_str = "{0} is empty"
            loc_str = ".".join(self._locator)
            repr_str = repr_str.format(loc_str)
        else:
            repr_str = repr_str[:-1]
        
        return repr_str
    
    __str__ = __repr__

class PresetIndex:
    def __init__(self, workspace):
        self.filters = WorkspacePointer(
            workspace, ["presets", "filters"], ".json", FiltersPreset)
        self.headers = WorkspacePointer(
            workspace, ["presets", "headers"], ".json", HeadersPreset)

class Workspace:
    def __init__(self, path: str = None):
        if path is None:
            self._path = os.path.join(os.getcwd(), ".hq")
        else:
            self._path = path

        self.load()
    
    @property
    def path(self) -> str:
        return self._path

    def load(self):
        if os.path.isdir(self._path):
            self.profiles = WorkspacePointer(
                self, ["profiles"], None, Profile)
            self.endpoints = WorkspacePointer(
                self, ["endpoints"], ".json", Endpoint)
            self.presets = PresetIndex(self)
        else:
            self.profiles = self.endpoints = self.presets = None

    def init(self):
        bin_path = os.path.join(os.getcwd(), ".hq")
        if not os.path.isdir(bin_path):
            os.mkdir(bin_path)

        prof_path = os.path.join(bin_path, "profiles")
        if not os.path.isdir(prof_path):
            os.mkdir(prof_path)

        ep_path = os.path.join(bin_path, "endpoints")
        if not os.path.isdir(ep_path):
            os.mkdir(ep_path)

        presets_path = os.path.join(bin_path, "presets")
        if not os.path.isdir(presets_path):
            os.mkdir(presets_path)
        
        for sub in ["filters", "headers"]:
            sub_path = os.path.join(presets_path, sub)
            if not os.path.isdir(sub_path):
                os.mkdir(sub_path)

        self.load()