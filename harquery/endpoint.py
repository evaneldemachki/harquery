from urllib.parse import urlparse, parse_qs, parse_qsl, urlencode
import requests
import pprint
import json
from typing import Any, Iterable
import os

class HeadersBase:
    def to_dict(self):
        return self._data[:]

    def drop(self, key: str) -> None:
        for i in range(len(self._data)):
            entry = self._data[i]
            if entry["name"] == key:
                self._data.pop(i)
                return

        raise KeyError      

    def __getitem__(self, key: str) -> str:
        for entry in self._data:
            if entry["name"] == key:
                return entry["value"]
        
        raise KeyError

    def __iter__(self):
        keys = [entry["name"] for entry in self._data]
        for key in keys:
            yield key
    
    def __setitem__(self, key: str, value: str) -> None:
        key = key.lower()

        found = False
        for entry in self:
            if entry == key:
                found = True
                entry["value"] = value

        if not found:
            self._data.append({
                "name": key,
                "value": value
            })

class QueryArray:
    def __init__(self, entry: list):
        self._data = entry

    def __getitem__(self, i):
        try:
            return self._data[i]
        except:
            raise KeyError
    
    def __iter__(self):
        return self._data.__iter__()
 
    def __len__(self):
        return len(self._data)

    def __add__(self, value):
        if value not in self._data:
            return QueryArray(self._data + [value])
    
    def __sub__(self, value):
        if value in self._data:
            index = self._data.index(value)

            new_data = self._data[0:index] + self._data[index+1:]
            return QueryArray(new_data)
        else:
            return self
    
    def drop(self, index):
        try:
            self._data.pop(index)
        except:
            raise KeyError
    
    def __repr__(self):
        return str(self._data)
    
    __str__ = __repr__

class Query:
    def __init__(self, query_str):
        self._data = {}
        data = parse_qs(query_str)
        for key in data:
            self._data[key] = QueryArray(data[key])
    
    def encode(self):
        return urlencode(self._data, doseq=True)
    
    def __getitem__(self, key):
        try:
            return self._data[key]
        except:
            raise KeyError
    
    def __setitem__(self, key, value):
        if isinstance(value, QueryArray):
            self._data[key] = value
        elif isinstance(value, str):
            self._data[key] = QueryArray([value])
        elif isinstance(value, list) or isinstance(value, tuple):
            try:
                self._data[key] = QueryArray([str(val) for val in value])
            except:
                raise TypeError
        else:
            try:
                self._data[key] = QueryArray([str(value)])
            except:
                raise TypeError
    
    def __iter__(self):
        for key in self._data:
            yield key
    
    def __len__(self):
        return len(self._data)
    
    def __repr__(self):
        repr_str = "QUERY\n"
        count = 0
        for key in self._data:
            repr_str += "  {0}: {1}\n".format(key, self._data[key])

            count += 1
        
        if count == 0:
            return "QUERY: (empty)"
        else:
            return repr_str[:-1]
    
    __str__ = __repr__

class Headers(HeadersBase):
    def __init__(self, data: dict):
        self._data = data
    
    def take(self, headers: Iterable) -> None:
        count = 0
        for key in headers:
            self[key] = headers[key]
            count += 1

        print("Took ({0}) headers".format(count))
        
    def __repr__(self):
        repr_str = "HEADERS:\n"

        count = 0
        for header in self._data:
            repr_str += "  {0}: {1}\n".format(
                header["name"], header["value"])

            count += 1
        
        if count == 0:
            return "HEADERS: (empty)"
        else:
            return repr_str[:-1]

        return repr_str

    __str__ = __repr__
    
class Endpoint:
    def __init__(self, workspace: 'Workspace', name: str):
        self._workspace = workspace
        self._name = name

        path = os.path.join(
            self._workspace._path, "endpoints", self._name + ".json")

        with open(path, "r") as f:
            data = json.load(f)

        req_url = urlparse(data["url"])
        self._data = {
            "base": req_url.netloc + req_url.path,
            "method": data["method"],
            "headers": Headers(data["headers"]),
            "query": Query(req_url.query)
        }

        if "body" in data:
            self._data["body"] = data["body"]

        # TEMPORARY SOLUTION
        self.protocol = "http://"

    @staticmethod
    def new(workspace: 'Workspace', name: str, entry: dict) -> 'Endpoint':
        data = entry["request"]

        path = os.path.join(
            workspace._path, "endpoints", name + ".json")
        with open(path, "w") as f:
            json.dump(data, f)

        endpoint = Endpoint(workspace, name)

        print("Added endpoint: '{0}'".format(name))

        return endpoint

    def encode(self) -> str:
        url_string = self._data["base"] + "?"
        url_string += self._data["query"].encode()

        return url_string
    
    def to_dict(self) -> dict:
        obj = {
            "url": self.encode(),
            "method": self.method,
            "headers": self.headers.to_dict()
        }
        if self.method == "POST":
            obj["body"] = self.body

        return obj
    
    def send(self) -> None:
        obj = self.to_dict()
        headers = {}
        for entry in obj["headers"]:
            headers[entry["name"]] = entry["value"]
        
        sess = requests.Session()
        if obj["method"] == "GET":
            req = requests.Request(
                obj["method"], 
                self.protocol + obj["url"], # <- TEMPORARY SOLUTION
                headers=headers
            )
        else:
            req = requests.Request(
                obj["method"], 
                self.protocol + obj["url"], # <- TEMPORARY SOLUTION
                body=obj["body"], 
                headers=headers
            )

        prepped = req.prepare()
        try:
            response = sess.send(prepped, timeout=5)
        except:
            req = requests.Request(
                obj["method"], 
                "https://" + obj["url"], # <- TEMPORARY SOLUTION
                headers=headers
            )
            prepped = req.prepare()
            response = sess.send(prepped, timeout=5)
            #raise TimeoutError("request timed out")

        return response
    
    def save(self):
        path = os.path.join(
            self._workspace._path, "endpoints", self._name + ".json")

        obj = self.to_dict()
        with open(path, "w") as f:
            json.dump(obj, f)
        
        print("Saved endpoint: '{0}'".format(self._name))
    
    def __getattr__(self, key: str) -> Any:
        if key not in self._data:
            raise AttributeError
        
        return self._data[key]

    def __repr__(self):
        repr_str = "URL: {0}\n".format(self._data["base"])
        repr_str += "METHOD: {0}\n".format(self._data["method"])
        repr_str += str(self._data["headers"]) + "\n"
        repr_str += str(self._data["query"]) + "\n"
        
        if self._data["method"] == "POST":
            repr_str += "BODY: {...} ({0})".format(len(str(self._data["body"])))
        else:
            repr_str = repr_str[:-1]

        return repr_str
    
    __str__ = __repr__

                    

