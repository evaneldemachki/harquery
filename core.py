import os
import json
from copy import deepcopy
import pprint
from selenium import webdriver
from browsermobproxy import Server
import urllib.request
import urllib.robotparser
from urllib.parse import urlparse, unquote

from harquery.tree import segments_to_path, profile_tree
from harquery import _geckodriver
from harquery.query import execute


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
        if url[:len(leader)] == leader:
            url = url[len(leader):]

    if url[-1] == "/":
        url = url[:-1]

    return url.split("/")

class Filters:
    def __init__(self, profile, obj):
        self._profile = profile
        self._obj = obj

        for query in self._obj:
            self._profile._obj, _ = self._run(query)

    def use(self, name: str):
        preset_path = os.path.join(os.getcwd(), "har.bin", "presets", name + ".json")
        if not os.path.exists(preset_path):
            raise FileNotFoundError
        
        with open(preset_path, "r") as f:
            obj = json.load(f)
        
        for query in obj:
            self._profile._obj, _ = self._run(query)

        self._obj = obj

        print("using filters preset: {0}".format(name))

    def add(self, query):
        if self._profile._source is None:
            print("Cannot use filters on empty profile segment")
            return

        doc = execute(
            self._profile._obj,
            query, "filter"
        )

        self._profile._obj = doc["cursor"]
        self._obj.append({
            "interpreted": doc["interpreted"],
            "instructions": doc["instructions"]
        })

        self._profile.save()
        print("added filter: {0}".format(query))

    def drop(self, index: int):
        if self._profile._source is None:
            print("Cannot use filters on empty profile segment")
            return
        if index < 0:
            index = len(self._obj) + index
        if index < 0 or index >= len(self._obj):
            raise IndexError
            
        self._profile._obj = deepcopy(self._profile._source)
        drop_query = self._obj[index]
        new_obj = self._obj[:index] + self._obj[index+1:]
        for query in new_obj:
            self._profile._obj = execute(
                self._profile._obj,
                query, "filter"
            )

        self._obj = new_obj
        self._profile.save()

        print("removed filter: {0}".format(drop_query))
    
    def clear(self):
        self._profile._obj = deepcopy(self._profile._source)
        self._obj = []

        print("removed all filters")

    def __repr__(self):
        repr_str = ""
        for i in range(len(self._obj)):
            query = self._obj[i]["interpreted"]
            repr_str += "[{0}] {1}\n".format(i, query)

        return repr_str

    __str__ = __repr__

class Profile:
    def __init__(self, segments):
        self._segments = segments
        self._view = None

        base = segments[0]
        base_path = os.path.join(
            os.getcwd(), "har.bin", "profiles", base)
        
        index_path = os.path.join(base_path, "index.json")
        with open(index_path, "r") as f:
            self._index = json.load(f)

        self._cursor = segments
        self._load()

    @property
    def tree(self):
        print(profile_tree(self._index))

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
            path = segments_to_path(self._index, cursor)
        except:
            raise KeyError("ERROR: profile segment not found")

        self._cursor = cursor
        self._load()
        print(str(self))

    def get(self, index, query):
        entry = self._obj[index]
        inner = get_nested(entry, keys)
        return inner      
    
    def expand(self, index, query):
        entry = self._obj[index]
        inner = get_nested(entry, keys)
        if isinstance(inner, str):
            print(inner)
        else:
            pprint.pprint(inner)
    
    def raw_search(self, query):
        matches = []
        for i in range(0, len(self._obj)):
            obj = get_nested(self._obj[i], keys)

            if isinstance(obj, str):
                raw_obj = obj
            else:
                raw_obj = json.dumps(obj)
                
            if term in raw_obj:
                matches.append(i)
        
        return matches
                    
    def release(self):
        if self._source is None:
            print("This profile segment is empty")
            return
        self._view = None

    def show(self):
        if self._source is None:
            print("This profile segment is empty")
            return
        if self._view is None:
            pprint.pprint(self._obj)
            return

        doc = execute(self._obj, self._view, "select")

        for i in range(len(doc["cursor"])):
            entry = doc["cursor"][i]
            print("[{0}] {1}".format(i, entry))

        total = len(self._obj)
        print("Total entries: {0}".format(total))

    def select(self, query):
        if self._source is None:
            print("This profile segment is empty")
            return
        self._view = query
        print("set view to '{0}'".format(query))

    def save(self):
        if self._source is None:
            print("This profile segment is empty")
            return
        path = os.path.join(segments_to_path(self._index, self._cursor))
        filters_path = os.path.join(path, "filters.json")
        with open(filters_path, "w") as f:
            json.dump(self.filters._obj, f)

        print("saved profile filters")

    def _load(self):
        cursor_path = segments_to_path(self._index, self._cursor)
        # assure that source HAR file exists
        source_path = os.path.join(cursor_path, "source.har")
        if not os.path.exists(source_path):
            self._source = None
            self._obj = None
        else: # load source as dict
            with open(source_path, "r") as f:
                self._source = json.load(f)["log"]["entries"]
                self._obj = deepcopy(self._source)

        # load filters
        filters_path = os.path.join(cursor_path, "filters.json")
        with open(filters_path, "r") as f:
            self.filters = Filters(self, json.load(f))

    def __repr__(self):
        routes = "{0}".format(self._cursor[0])
        for r in self._cursor[1:]:
            routes += " > {0}".format(r)

        return "Profile: {0}".format(routes)

    __str__ = __repr__
