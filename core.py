import os
import json
import pprint
from selenium import webdriver
from browsermobproxy import Server
import urllib.request
import urllib.robotparser
from urllib.parse import urlparse, unquote
from typing import Union

from harquery.tree import segments_to_path, profile_tree, index_profile
from harquery import _geckodriver
from harquery.query import parse, execute, get_nested

def fetch_har_by_url(url, segments, index):
    project_dir = os.path.dirname(__file__)
    bpm_path = os.path.join(project_dir, "browsermob-proxy-2.1.1/bin/browsermob-proxy")

    server = Server(bpm_path)
    server.start()
    proxy = server.create_proxy()

    profile  = webdriver.FirefoxProfile()
    profile.set_proxy(proxy.selenium_proxy())
    
    driver = webdriver.Firefox(
        firefox_profile=profile, 
        executable_path=os.path.join(
            os.path.dirname(__file__), _geckodriver)
    )

    proxy.new_har(url, options={'captureHeaders': True, 'captureContent': True, 'captureBinaryContent': True})
    proxy.wait_for_traffic_to_stop(2000, 10000)

    driver.get(url)

    har = proxy.har

    server.stop()
    driver.quit()

    return har

def get_robots_list(url) -> list:
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url("{0}/robots.txt".format(url))
    rp.read()
    rrate = rp.request_rate("*")
    return rp.__str__().split("\n")

def parse_url(url):
    for leader in ("https://", "http://", "www."):
        # if leader is in beginning of string
        if url[:len(leader)] == leader:
            url = url[len(leader):]

    if url[-1] == "/":
        url = url[:-1]

    return url.split("/")

def reduce_filters(filters):
    reduced = filters._obj["filters"][:]
    if len(filters._obj["presets"]) != 0:
        for preset in filters._obj["presets"]:
            path = os.path.join(os.getcwd(), ".hq", "presets", preset + ".json")
            if not os.path.isfile(path):
                raise FileNotFoundError
            
            with open(path, "r") as f:
                obj = json.load(f)
            
            preset_strings = [p["string"] for p in obj]
            for i in range(len(reduced) - 1, -1, -1):
                filter_string = reduced[i]["string"]
                if filter_string in preset_strings:
                    reduced.pop(i)
    
    return reduced

class Preset:
    def __init__(self, workspace, name):
        self._workspace = workspace
        self._name = name

        path = os.path.join(
            workspace._path, "presets", name + ".json")

        with open(path, "r") as f:
            data = json.load(f)
        
        self._obj = data
    
    @property
    def filters(self):
        for i in range(len(self._obj)):
            doc = self._obj[i]
            print("[{0}] {1}".format(i, doc["string"]))
    
    @staticmethod
    def new(workspace: 'Workspace', name: str, data: list = None):
        path = os.path.join(
            workspace._path, "presets", name + ".json")

        if os.path.isfile(path):
            raise FileExistsError

        if data is None:
            data = []

        with open(path, "w") as f:
            json.dump(data, f)
        
        print("Added new preset: '{0}'".format(name))

        return Preset(workspace, name)
    
    def __len__(self):
        return len(self._obj)
        
    def __iter__(self):
        for doc in self._obj:
            yield doc
    
    def __setitem__(self, index: int, query: Union[str, dict]):
        if index < 0 or index >= len(self._obj):
            raise IndexError
        
        if isinstance(query, str):
            query = parse(query)
        elif isinstance(query, dict):
            pass
        else:
            raise TypeError

        self._obj[index] = query
        self._save()
    
    def use(self, filters: list, deep: bool = False):
        if not deep:
            reduced = reduce_filters(filters)
        else:
            reduced = filters._obj["filters"][:]
        
        self._obj = reduced
        self._save()
    
    def add(self, query: Union[str, dict]):
        if isinstance(query, str):
            query = parse(query)
        elif isinstance(query, dict):
            pass
        else:
            raise TypeError  
        
        self._obj.append(query)
        self._save()
    
    def drop(self, index: int):
        if index < 0 or index >= len(self._obj):
            raise IndexError

        self._obj.pop(index)
        self._save()        
    
    def _save(self):
        path = os.path.join(
            self._workspace._path, "presets", self._name)
        
        with open(path, "w") as f:
            json.dump(self._obj, f)
        
    def __repr__(self):
        return "Preset: {0}".format(self._name)
    
    __str__ = __repr__
        
class Filters:
    def __init__(self, profile, obj):
        self._profile = profile
        self._obj = obj

        for doc in self._obj["filters"]:
            data = execute(self._profile._obj, doc["object"], "filter")
            self._profile._obj = data

    def use(self, name: str):
        presets = self._profile._workspace.presets

        if name in presets:
            preset = presets[name]
        else:
            raise NameError("preset '{0}' does not exist".format(name))
        
        for doc in preset:
            self._profile._obj = execute(
                self._profile._obj, doc["object"], "filter")

        self._obj["filters"] += preset
        if name not in self._obj["presets"]:
            self._obj["presets"].append(name)

        self._profile._save()

        print("added ({0}) filters from preset: {1}".format(len(preset), name))

    def discard(self, name: str):
        presets = self._profile._workspace.presets

        if name in presets:
            preset = presets[name]
        else:
            raise NameError("preset '{0}' does not exist".format(name))
        
        if not name in self._obj["presets"]:
            raise NameError("preset '{0}' is not currently in use".format(name))
        
        preset_strings = [p["string"] for p in preset]

        delta = 0
        for i in range(len(self._obj["filters"]) - 1, -1, -1):
            doc = self._obj["filters"][i]
            if doc["string"] in preset_strings:
                self._obj["filters"].pop(i)
                delta += 1
        
        if delta != 0:
            self._profile._obj = self._profile._source
            for doc in self._obj["filters"]:
                self._profile._obj = execute(
                    self._profile._obj, doc["object"], "filter")
        
        index = self._obj["presets"].index(name)
        self._obj["presets"].pop(index)

        self._profile._save()

        print("Discarded ({0}) filters matching preset: '{1}'".format(delta, name))

    def add(self, query):
        if self._profile._obj is None:
            print("Cannot use filters on empty profile segment")
            return

        doc = parse(query)
        data = execute(
            self._profile._obj, doc["object"], "filter")

        self._profile._obj = data
        self._obj["filters"].append(doc)

        self._profile._save()
        
        print("added filter: {0}".format(doc["string"]))

    def drop(self, index: int):
        if self._profile._obj is None:
            print("Cannot use filters on empty profile segment")
            return

        if index < 0:
            index = len(self._obj["filters"]) + index
        if index < 0 or index >= len(self._obj["filters"]):
            raise IndexError
            
        self._profile._obj = self._profile._source

        drop_query = self._obj["filters"][index]["string"]
        new_obj = self._obj["filters"][:index] + self._obj["filters"][index+1:]
        for doc in new_obj:
            self._profile._obj = execute(
                self._profile._obj, doc["object"], "filter")

        self._obj["filters"] = new_obj

        self._profile._save()

        print("removed filter: {0}".format(drop_query))
    
    def clear(self):
        self._profile._obj = self._profile._source
        self._obj = {"presets": [], "filters": []}

        self._profile._save()

        print("removed all filters")

    def __repr__(self):
        if len(self._obj["presets"]) == 0:
            repr_str = ""
        else:
            presets_str = ", ".join(self._obj["presets"])
            repr_str = "Using presets: {0}\n".format(presets_str)
            
        count = 0
        for i in range(len(self._obj["filters"])):
            query = self._obj["filters"][i]["string"]
            repr_str += "[{0}] {1}\n".format(i, query)
            count += 1

        if count == 0:
            return "No filters added"
        else:
            return repr_str[:-1]

    __str__ = __repr__

class Profile:
    def __init__(self, workspace, name):
        self._workspace = workspace
        self._cursor = [name]
        self._focus = parse("request.url")

        self._load()

    @property
    def tree(self):
        print(profile_tree(self._cursor[0], self._index))

    @staticmethod
    def new(workspace: 'Workspace', url: str):
        #robotsTxt = get_robots_list(url)
        segments = parse_url(url)
        url = "http://" + "/".join(segments)

        path = os.path.join(workspace._path, "profiles")

        base_path_existed = True
        base_path = os.path.join(path, segments[0])
        if not os.path.exists(base_path):
            base_path_existed = False
            os.mkdir(base_path)

        index = index_profile(segments)

        har = fetch_har_by_url(url, segments, index)

        curr_path = os.path.join(
            workspace._path, "profiles",
            segments_to_path(index, segments)
        )
        source_path = os.path.join(curr_path, "source.har")
        with open(source_path, 'w') as json_file:
            json.dump(har, json_file)
        
        if base_path_existed:
            print("Extended profile: '{0}' at '{1}'".format(
                segments[0], "/".join(segments[1:])))
        elif len(segments) == 1:
            print("Created profile: '{0}'".format(url))
        else:
            print("Created profile: '{0}' at '{1}'".format(
                segments[0], "/".join(segments[1:])))

        profile = Profile(workspace, segments[0])
        profile._cursor = segments
        profile._load()

        return profile

    def cd(self, loc):
        rel_cursor = loc.split("/")
        if any(rel == "{hash}" for rel in rel_cursor):
            raise KeyError("ERROR: referenced reserved key '{hash}'")

        cursor = self._cursor[:]
        for rel in rel_cursor:
            if rel == ".":
                continue
            elif rel == "..":
                cursor.pop()
                continue
            else:
                cursor.append(rel)
        
        try:
            segments_to_path(self._index, cursor)
        except:
            raise KeyError("ERROR: profile segment not found")

        self._cursor = cursor
        self._load()
        print(str(self))

    def get(self, index, query):
        if self._is_empty("GET"): return

        obj = [self._obj[index]]
        query = parse(query)["object"]
        data = execute(obj, query, "focus")[0]

        return data  
    
    def expand(self, index, *keys):
        if self._is_empty("EXPAND"): return

        entry = self._obj[index]
        inner = get_nested(entry, keys)
        if isinstance(inner, str):
            print(inner)
        else:
            pprint.pprint(inner)

    def focus(self, query: str = "request.url"):
        if self._is_empty("FOCUS"): return

        self._focus = parse(query)
        print("set view to '{0}'".format(query))

    def show(self):
        if self._is_empty("SHOW"): return

        data = execute(
            self._obj, self._focus["object"], "focus")

        for i in range(len(data)):
            print("[{0}] {1}".format(i, data[i]))

        total = len(self._obj)
        print("Total entries: {0}".format(total))

    def _save(self):
        path = os.path.join(
            self._workspace.path, "profiles",
            segments_to_path(self._index, self._cursor)
        )

        filters_path = os.path.join(path, "filters.json")
        with open(filters_path, "w") as f:
            json.dump(self.filters._obj, f)

    @property
    def _index(self):
        index_path = os.path.join(
            self._workspace.path, "profiles", 
            self._cursor[0], "index.json"
        )
        with open(index_path, "r") as f:
            index = json.load(f)
        
        return index

    @property
    def _source(self):
        cursor_path = os.path.join(
            self._workspace.path, "profiles",
            segments_to_path(self._index, self._cursor)
        )
        source_path = os.path.join(cursor_path, "source.har")
        if not os.path.exists(source_path):
            source = None
        else:
            with open(source_path, "r") as f:
                source = json.load(f)["log"]["entries"]

        return source

    def _load(self):
        self._obj = self._source
        # load filters
        cursor_path = os.path.join(
            self._workspace.path, "profiles",
            segments_to_path(self._index, self._cursor)
        )
        filters_path = os.path.join(cursor_path, "filters.json")
        with open(filters_path, "r") as f:
            self.filters = Filters(self, json.load(f))
    
    def _is_empty(self, action):
        if self._obj is None:
            msg = "Cannot perform action '{0}' on empty profile segment"
            print(msg.format(action))
            return True
        
        return False

    def __repr__(self):
        routes = "{0}".format(self._cursor[0])
        for r in self._cursor[1:]:
            routes += " > {0}".format(r)

        return "Profile: {0}".format(routes)

    __str__ = __repr__
