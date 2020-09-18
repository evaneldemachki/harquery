from urllib.parse import urlparse, parse_qs, parse_qsl
import pprint

class QueryArray:
    def __init__(self, entry):
        self._data = entry

    def __getitem__(self, i):
        try:
            return self._data[i]
        except:
            raise KeyError
 
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
    
    def __repr__(self):
        repr_str = "QUERY\n"
        for key in self._data:
            repr_str += "  {0}: {1}\n".format(key, self._data[key])
        
        return repr_str
    
    __str__ = __repr__

class Headers:
    def __init__(self, headers):
        self._data = headers
    
    def __getitem__(self, key):
        for entry in self._data:
            if entry["name"] == key:
                return entry["value"]
        
        raise KeyError
    
    def __setitem__(self, key, value):
        for entry in self._data:
            if entry["name"] == key:
                try:
                    entry["value"] = str(value)
                    return
                except:
                    raise TypeError 

        raise KeyError
    
    def __repr__(self):
        repr_str = "HEADERS\n"
        for header in self._data:
            repr_str += "  {0}: {1}\n".format(
                header["name"], header["value"])
        
        return repr_str

    __str__ = __repr__     
    
    
class Endpoint:
    def __init__(self, entry):
        self._source = entry

        req_url = urlparse(entry["request"]["url"])
        self._url = req_url.netloc + req_url.path
        self._method = entry["request"]["method"]
        self._headers = Headers(entry["request"]["headers"])
        self._query = Query(req_url.query)
    
    @property
    def url(self):
        return self._url
    @property
    def method(self):
        return self._method
    @property
    def headers(self):
        return self._headers
    @property
    def query(self):
        return self._query
    
    def __repr__(self):
        repr_str = "URL: {0}\n".format(self._url)
        repr_str += "METHOD: {0}\n".format(self._method)
        repr_str += str(self._headers)
        repr_str += str(self._query)

        return repr_str
    
    __str__ = __repr__

                    

