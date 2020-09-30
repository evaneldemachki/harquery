import os
import json
from typing import Iterable

from harquery.query import parse
from harquery.endpoint import HeadersBase

class HeadersPreset(HeadersBase):
    def __init__(self, workspace: 'Workspace', name: str):
        self._workspace = workspace
        self._name = name

        path = os.path.join(
            workspace._path, "presets", "headers", name + ".json")
        with open(path, "r") as f:
            self._data = json.load(f)

    @staticmethod
    def new(workspace: 'Workspace', name: str, data: list = None):
        path = os.path.join(
            workspace._path, "presets", "headers", name + ".json")

        if os.path.isfile(path):
            raise FileExistsError("Headers preset '{0}' already exists".format(name))

        if data is None:
            data = []

        with open(path, "w") as f:
            json.dump(data, f)
        
        print("Added new headers preset: '{0}'".format(name))

        return HeadersPreset(workspace, name)

    def save(self) -> None:
        path = os.path.join(
            self._workspace._path, "presets", "headers", self._name + ".json")
        
        with open(path, "w") as f:
            json.dump(self._data, f)
        
        print("Saved headers preset: '{0}'".format(self._name))

    def __repr__(self):
        repr_str = "headers > presets > {0}\n".format(self._name)

        count = 0
        for header in self._data:
            repr_str += "  {0}: {1}\n".format(
                header["name"], header["value"])
            
            count += 1
        
        if count == 0:
            return "headers > presets > {0}: (empty)".format(self._name)
        else:
            return repr_str[:-1]
        
        return repr_str

    __str__ = __repr__

class FiltersPreset:
    def __init__(self, workspace: 'Workspace', name: str):
        self._workspace = workspace
        self._name = name

        path = os.path.join(
            workspace._path, "presets", "filters", name + ".json") 
        with open(path, "r") as f:
            self._obj = json.load(f)

    @staticmethod
    def new(workspace: 'Workspace', name: str, data: list = None):
        path = os.path.join(
            workspace._path, "presets", "filters", name + ".json")

        if os.path.isfile(path):
            raise FileExistsError("Filters preset '{0}' already exists".format(name))

        if data is None:
            data = []

        with open(path, "w") as f:
            json.dump(data, f)
        
        print("Added new filters preset: '{0}'".format(name))

        return FiltersPreset(workspace, name)

    def add(self, query: str) -> None:
        if isinstance(query, str):
            doc = parse(query)
        elif isinstance(query, dict):
            doc = query
        else:
            raise TypeError  

        current_filters = [item["string"] for item in self._obj]
        if doc["string"] in current_filters:
            raise ValueError("duplicate filter '{0}'".format(doc["string"])) 

        self._obj.append(doc)

        print("added filter: {0}".format(doc["string"]))
    
    def take(self, filters: Iterable):
        count = 0
        current_filters = [item["string"] for item in self._obj]
        for filt in filters:
            if filt["string"] not in current_filters:
                self._obj.append(filt)
                count += 1
        
        print("Took {0} filters".format(count))
        
    def drop(self, index: int) -> None:
        if index < 0:
            index = len(self._obj) + index
        if index < 0 or index >= len(self._obj):
            raise IndexError

        drop_query = self._obj[index]["string"]
        self._obj.pop(index)

        print("removed filter: {0}".format(drop_query))
    
    def clear(self) -> None:
        self._obj = []

        print("removed all filters")
    
    def save(self) -> None:
        path = os.path.join(
            self._workspace._path, "presets", "filters", self._name + '.json')
        
        with open(path, "w") as f:
            json.dump(self._obj, f)
        
        print("Saved filters preset: '{0}'".format(self._name))
    
    def __iter__(self):
        for filt in self._obj:
            yield filt

    def __repr__(self):
        repr_str = "presets > filters > {0}\n".format(self._name)

        count = 0
        for i in range(len(self._obj)):
            query = self._obj[i]["string"]
            repr_str += "[{0}] {1}\n".format(i, query)
            count += 1

        if count == 0:
            return "presets > filters > {0}: (empty)".format(self._name)
        else:
            return repr_str[:-1]

    __str__ = __repr__