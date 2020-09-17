import os
import json
from copy import deepcopy
import pprint
from selenium import webdriver
from browsermobproxy import Server
import urllib.request
import urllib.robotparser

from harquery.tree import segments_to_path, profile_tree

pdir = os.path.dirname(__file__)

def fetch_har_by_url(url, segments, index):
    project_dir = os.path.dirname(__file__)
    bpm_path = os.path.join(project_dir, "browsermob-proxy-2.1.1/bin/browsermob-proxy")

    server = Server(bpm_path)
    server.start()
    proxy = server.create_proxy()

    profile  = webdriver.FirefoxProfile()
    profile.set_proxy(proxy.selenium_proxy())
    driver = webdriver.Firefox(firefox_profile=profile)

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

def query_switch(query):
    if "!=" in query:
        return lambda a,b: a != b, "!="
    elif "=" in query:
        return lambda a,b: a == b, "="
    elif "!#" in query:
        return lambda a,b: b not in a, "!#"
    elif "#" in query:
        return lambda a,b: b in a, "#"
    else:
        return None, None

def get_nested(entry, keys):
    item = entry
    for key in keys:
        item = item[key]

    return item

def get_inner(entry, keys):
    # keys = [{name:content-type}, [value]]
    locator = keys[0][1:-1].split(":")
    # locator = [name, content-type]
    section = None
    for item in entry:
        if locator[0] in item:
            if item[locator[0]] == locator[1]:
                section = item
                break

    if section is None: # locator key/value pair not found
        return None

    value = get_nested(section, keys[1])
    return value

class Filters:
    def __init__(self, profile, obj):
        self._profile = profile
        self._obj = obj

        for query in self._obj:
            self._profile._obj, _ = self._run(query)

    def add(self, query):
        if self._profile._source is None:
            print("Cannot use filters on empty profile segment")
            return

        self._profile._obj, query = self._run(query)
        self._obj.append(query)
        self._profile.save()
        print("added filter: {0}".format(query))

    def undo(self):
        if self._profile._source is None:
            print("Cannot use filters on empty profile segment")
            return

        self._profile._obj = deepcopy(self._profile._source)
        last_query = self._obj[-1]
        for query in self._obj[:-1]:
            self._profile._obj, _ = self._run(query)

        self._obj.pop(-1)
        self._profile.save()
        print("removed filter: {0}".format(last_query))

    def _run(self, query):
        query = query.replace(" ","")

        base_op, op_key = query_switch(query)
        if base_op is None or op_key is None:
            raise ValueError("invalid query: no match operators")
            
        op = lambda a,b: base_op(a,b) if a is not None else False
        # response.headers@{name:content-type}->value=application/json
        query_split = query.split(op_key)
        # [response.headers@{name:content-type}->value, application/json]
        assert len(query_split) == 2, "invalid query: duplicate match operators"
        if "@" in query_split[0]:
            sub_split = query_split[0].split("@")
            # [response.headers, {name:content-type}->value]
            keys = sub_split[0].split(".")
            # [response, headers]
            inner_keys = sub_split[1].split("->")
            # [{name:content-type}, value]
            inner_keys[1] = inner_keys[1].split(".")
            # [{name:content-type}, [value]]
            get_func = lambda entry, keys: get_inner(get_nested(entry, keys), inner_keys)
        else:
            keys = query_split[0].split(".")
            get_func = get_nested

        value = query_split[1]
        old_value = value # save for return query replacement

        # check for reference notation (inserts value from corresponding entry)
        if value[0]=="[" and value[-1]=="]":
            try:
                index = int(value[1:-1])
            except:
                raise ValueError("invalid index notation")

            value = get_func(self._profile._obj[index], keys)

        obj = []
        for entry in self._profile._obj:
            if op(get_func(entry, keys), value):
                obj.append(entry)

        return obj, query.replace(old_value, value)

    def __repr__(self):
        repr_str = ""
        for i in range(len(self._obj)):
            query = self._obj[i]
            repr_str += "[{0}] {1}\n".format(i, query)

        return repr_str

    __str__ = __repr__

class Profile:
    def __init__(self, segments):
        self._segments = segments
        self._view = None

        base = segments[0]
        base_path = os.path.join(
            os.getcwd(), "har.bin", "profile", base)
        
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

    # export current proxy to JSON file
    def export(self):
        pass
    # create sub-profile for nested API calls
    def branch(self, name):
        pass

    # TODO: add filter by domain name (ie. term before .com/.net etc.)

    def reset_view(self):
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

        if "@" in self._view:
            view_split = self._view.split("@")
            inner_keys = view_split[1].split("->")
            inner_keys[1] = inner_keys[1].split(".")
            keys = view_split[0].split(".")
            count = 0
            for i in range(len(self._obj)):
                entry = self._obj[i]
                value = get_inner(get_nested(entry, keys), inner_keys)
                if value is not None:
                    print("[{0}] {1}".format(i, value))
                    count += 1
        else:
            count = len(self._obj)
            keys = self._view.split(".")
            for i in range(len(self._obj)):
                entry = self._obj[i]
                print("[{0}] {1}".format(i, get_nested(entry, keys)))

        total = len(self._obj)
        print("Total entries: {0} | excluded: {1}".format(total, total - count))

    def set_view(self, query):
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

        # assure that filters JSON exists
        filters_path = os.path.join(cursor_path, "filters.json")
        # load filters
        with open(filters_path, "r") as f:
            self.filters = Filters(self, json.load(f))

    def __repr__(self):
        routes = "{0}".format(self._cursor[0])
        for r in self._cursor[1:]:
            routes += " > {0}".format(r)

        return "Profile: {0}".format(routes)

    __str__ = __repr__
