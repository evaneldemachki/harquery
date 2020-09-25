import os

from harquery.core import Profile, Preset
from harquery.endpoint import Endpoint
from harquery.errors import WorkspaceNotFoundError

def touch():
    bin_path = os.path.join(os.getcwd(), ".hq")
    if not os.path.exists(bin_path):
        os.mkdir(bin_path)

    prof_path = os.path.join(bin_path, "profiles")
    if not os.path.exists(prof_path):
        os.mkdir(prof_path)

    ep_path = os.path.join(bin_path, "endpoints")
    if not os.path.exists(ep_path):
        os.mkdir(ep_path)

    presets_path = os.path.join(bin_path, "presets")
    if not os.path.exists(presets_path):
        os.mkdir(presets_path)

    workspace.load()

class WorkspacePointer:
    __slots__ = ["_workspace", "_dir_name", "_extension", "_constructor"]
    def __init__(self, workspace: 'Workspace', dir_name: str):
        self._workspace = workspace
        self._dir_name = dir_name
        if dir_name == "profiles":
            self._extension = None
            self._constructor = Profile
        elif dir_name == "presets":
            self._extension = ".json"
            self._constructor = Preset
        elif dir_name == "endpoints":
            self._extension = ".json"
            self._constructor = Endpoint

    def add(self, *args):
        return self._constructor.new(self._workspace, *args)
    
    def _ftcheck(self) -> 'function':
        path = os.path.join(self._workspace.path, self._dir_name)
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

    def __getitem__(self, key: str) -> object:
        if key in self:
            return self._constructor(self._workspace, key)
        else:
            raise FileNotFoundError
    
    def __iter__(self):
        ftcheck = self._ftcheck()
        strf = self._strf()
        
        path = os.path.join(self._workspace.path, self._dir_name)
        for item in os.listdir(path):
            if ftcheck(os.path.join(path, item)):
                yield strf(item)

    
    def __repr__(self) -> str:
        repr_str = ""

        count = 0
        for item in self:
            repr_str += "| " + item + "\n"
            count += 1
        
        if count == 0:
            repr_str = "No {0} have been created in current workspace"
            repr_str = repr_str.format(self._dir_name)
        else:
            repr_str = repr_str[:-1]
        
        return repr_str
    
    __str__ = __repr__

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
            self.profiles = WorkspacePointer(self, "profiles")
            self.endpoints = WorkspacePointer(self, "endpoints")
            self.presets = WorkspacePointer(self, "presets")
        else:
            self.profiles = self.endpoints = self.presets = None