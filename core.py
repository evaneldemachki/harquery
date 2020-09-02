import os
import json
from copy import deepcopy
import pprint

pdir = os.path.dirname(__file__)

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
        self._profile._obj, query = self._run(query)
        self._obj.append(query)
        print("added filter: {0}".format(query))

    def undo(self):
        self._profile._obj = deepcopy(self._profile._source)
        last_query = self._obj[-1]
        for query in self._obj[:-1]:
            self._profile._obj, _ = self._run(query)

        self._obj.pop(-1)
        print("removed filter: {0}".format(last_query))

    def querySwitch(query):
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
    def _run(self, query):
        query = query.replace(" ","")

        base_op, op_key = querySwitch(query)
        if base_op is None || op_key is None:
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
    def __init__(self, name):
        self._name = name
        path = pdir + "/profile/{0}".format(name)
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        # assure that source HAR file exists
        source_path = path + "/source.har".format(name)
        if not os.path.exists(source_path):
            raise FileNotFoundError(source_path)
        # load source as dict
        with open(source_path, "r", encoding="utf-8") as f:
            self._source = json.load(f)["log"]["entries"]

        self._obj = deepcopy(self._source)

        # assure that filters JSON exists
        filters_path = path + "/filters.json"
        if not os.path.exists(filters_path):
            raise FileNotFoundError(filters_path)
        # load profile as dict
        with open(filters_path, "r") as f:
            self.filters = Filters(self, json.load(f))

    # export current proxy to JSON file
    def export(self):
        pass
    # create sub-profile for nested API calls
    def branch(self, name):
        pass

    # TODO: add filter by domain name (ie. term before .com/.net etc.)


    def reset_view(self):
        self._view = None

    def show(self):
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
        self._view = query
        print("set view to '{0}'".format(query))

    @property
    def name(self) -> str:
        return self._name

    @name.setter # rename profile directory name on name change
    def name(self, value):
        current_name = self.name
        # rename profile folder
        new_path = pdir + "/profile/{0}".format(value)
        os.rename(pdir + "/profile/{0}".format(self.name), new_path)
        self._path = new_path
        self._name = value

        print("renamed profile: {0} -> {1}".format(current_name, value))

    def save(self):
        path = pdir + "/profile/{0}/filters.json".format(self.name)
        with open(path, "w") as f:
            json.dump(self.filters._obj, f)

        print("saved profile filters")

    def __repr__(self):
        return "Profile: {0}".format(self.name)

    __str__ = __repr__
