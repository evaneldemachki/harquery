import os
import json
from copy import deepcopy

pdir = os.path.dirname(__file__)

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
        self._profile._display()
    
    def undo(self):
        self._profile._obj = deepcopy(self._profile._source)
        last_query = self._obj[-1]
        for query in self._obj[:-1]:
            self._profile._obj, _ = self._run(query)

        self._obj.pop(-1)
        print("removed filter: {0}".format(last_query))

    def _run(self, query):
        if "!=" in query:
            op = lambda a,b: a != b
            op_key = "!="
        elif "=" in query:
            op = lambda a,b: a == b
            op_key = "="
        elif "!#" in query:
            op = lambda a,b: b not in a
            op_key = "!#"
        elif "#" in query:
            op = lambda a,b: b in a
            op_key = "#"
        else:
            raise ValueError("invalid query")

        query = query.replace(" ","")
        
        def get_item(entry):
            item = entry
            for key in keys:
                item = item[key]
            
            return item
        
        query_split = query.split(op_key)
        assert len(query_split) == 2, "invalid query"
        keys = query_split[0].split(".")
        value = query_split[1]
        old_value = value
        # check for index notation
        if value[0]=="[" and value[-1]=="]":
            try:
                index = int(value[1:-1])
            except:
                raise ValueError("invalid index notation")

            value = get_item(self._profile._obj[index])
        
        obj = []
        for x in self._profile._obj:
            if op(get_item(x), value):
                obj.append(x)
        
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

    #TODO: 1. add filter by dictionaries key/value pairs in list (headers@["content-type"]=application/json)
    #      2. add filter by domain name (ie. term before .com/.net etc.)


    def reset_view(self):
        self._view = None

    def _display(self):
        def get_item(entry):
            item = entry
            for key in keys:
                item = item[key]
            
            return item

        keys = self._view.split(".")
        count = 0
        for i in range(len(self._obj)):
            entry = self._obj[i]
            print("[{0}] {1}".format(i, get_item(entry)))
            count += 1
        
        print("Total entries: {0}".format(count))

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
            
