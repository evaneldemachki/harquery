from typing import Tuple, Union
from copy import deepcopy
import json

with open("query-test.json", "r") as f:
    obj = json.load(f)["log"]["entries"]

class QueryError(Exception):
    """Exception raised if invalid query string passed"""
    def __init__(self, message):
        self.message = "Error: " + message
        super().__init__(self.message)

def reformat(query: str) -> Tuple[str, list]:
    functional_str = ""
    str_list = []

    quote = None
    current = ""
    for char in query:
        if quote is None:
            if char in ['"', "'"]:
                quote  = char
            
            functional_str += char
        else:
            if char == quote:
                functional_str += "{" + str(len(str_list)) + "}"
                functional_str += char
                str_list.append(current)

                quote = None
                current = ""
            else:
                current += char
    
    return functional_str, str_list

logicals = ["=", "#", "@"]
def process(query: str, terms: list) -> Tuple[list, list]:
    query_terms = []
    logical_terms = []
    
    skip = False
    last_index = 0
    for i in range(len(query)):
        if skip:
            skip = False
            continue

        char = query[i]
        if char in logicals:
            segment = query[last_index:][:i-last_index]
            query_terms.append(segment.strip())
            logical_terms.append(char)
            last_index = i + 1
        elif char == "!":
            if i == len(query) - 1:
                raise QueryError("invalid query expression")
            elif query[i+1] not in ["=", "#"]:
                 raise QueryError("invalid query expression")
            
            segment = query[last_index:][:i-last_index]
            query_terms.append(segment.strip())
            logical_terms.append(char + query[i+1])
            last_index = i + 2
            skip = True
        elif char == "-":
            if i != len(query) - 1:
                if query[i+1] == ">":
                    segment = query[last_index:][:i-last_index]
                    query_terms.append(segment.strip())
                    logical_terms.append(char + query[i+1])
                    last_index = i + 2
                    skip = True
    
    segment = query[last_index:]
    query_terms.append(segment.strip())

    # re-insert parsed-out quoted strings
    for i in range(len(terms)):
        search_str = "{" + str(i) + "}"
        for j in range(len(query_terms)):
            if search_str in query_terms[j]:
                query_terms[j] = query_terms[j].replace(search_str, terms[i])

    return query_terms, logical_terms

def parse_directive(directive: str) -> list:
    if " " in directive:
        raise QueryError("'{0}' is an invalid directive".format(directive))
    
    reserved = ["!", "#", "=", "@", "->", "$"]
    if any(key in directive for key in reserved):
        raise QueryError("'{0}' is an invalid directive".format(directive))

    return directive.split(".")

def parse_literal(literal: str) -> Union[str, int]:
    if literal[0] == literal[-1] == '"':
        return literal[1:-1]
    elif literal[0] == literal[-1] == "'":
        return literal[1:-1]
    else:
        raise QueryError("'{0}' is an invalid literal".format(literal))
    

def build(query_terms: list, logical_terms: list) -> Tuple[tuple]:
    obj = []
    primary_directive = parse_directive(query_terms.pop(0))
    obj.append( ("?", primary_directive) )

    state = False
    locator = False
    locator2 = False
    for i in range(len(query_terms)):
        term, op = query_terms[i], logical_terms[i]
        if state is False:
            if op in ["!=", "=", "!#", "#"]:
                obj.append( (op, parse_literal(term)) )
                if not locator2 and not locator:
                    state = True

            elif op == "@":
                if i == len(query_terms) - 1:
                    raise QueryError("expected directive following locator")
                
                obj.append( ("@", parse_directive(term)) )
                locator = True
            elif op == "->":
                if not locator:
                    raise QueryError("arrow operator detected but no locator has been declared")
                
                obj.append( ("->", parse_directive(term)) )
                locator = False
                locator2 = True
        elif state is True:
            print(obj)
            raise QueryError("invalid query expression")

    return obj

def query_switch(query):
    if query == "!=":
        return lambda a,b: a != b
    elif query == "=":
        return lambda a,b: a == b
    elif query == "!#":
        return lambda a,b: b not in a
    elif query == "#":
        return lambda a,b: b in a
    else:
        return None, None


def get_nested(entry, keys):
    item = entry
    for key in keys:
        item = item[key]

    return item
    
def run(obj: list, query: list, goal: str = "select"):
    cursor = []
    for i in range(len(obj)):
        focus = obj[i]
        locator = None
        response = None
        arrow = False
        end = False
        for block in query:
            key, ix = block

            if key == "?":
                if locator is not None or end:
                    raise RuntimeError
                try:
                    print(focus.keys())
                    print(ix)
                    focus = get_nested(focus, ix)
                    if goal == "select":
                        response = focus
                    else:
                        response = i
                except:
                    raise QueryError("invalid directive '{0}'".format(ix))
            elif key == "@":
                if locator is not None or end:
                    raise RuntimeError

                try:
                    locator = focus
                    focus = []
                    for item in locator:
                        focus.append(get_nested(item, ix))
                    
                    response = False
                except:
                    raise QueryError("invalid directive '{0}'".format(ix))
            elif key in ["!=", "=", "!#", "#"]:
                if locator is not None:
                    found = None
                    for j in range(len(focus)):
                        item = focus[j]
                        if query_switch(key)(item, ix):
                            found = j
                            break
                    
                    if found is None:
                        response = None
                        break
                    else:
                        focus = locator[found]
                        locator = None
                        arrow = True
                        if goal == "select":
                            response = focus
                        else:
                            response = i
                else:
                    if arrow:
                        raise QueryError("invalid query expression")

                    if query_switch(key)(focus, ix):
                        if goal == "select":
                            response = focus
                        else:
                            response = i
                    else:
                        response = None
                        break
            elif key == "->":
                if not arrow:
                    raise QueryError("invalid query expression")
                
                try:
                    focus = get_nested(focus, ix)
                    arrow = False
                    if goal == "select":
                        response = focus
                    else:
                        response = i
                except:
                    raise QueryError("invalid directive '{0}'".format(ix))
        
        if response is not None and response is not False:
            cursor.append(response)
        elif response is False:
            raise QueryError("incomplete query expression")
    
    return cursor

def execute(obj, query, method):
    x, y = reformat(query)
    x, y = process(x, y)
    instructions = build(x, y)

    interpreted = ".".join(instructions[0][1])
    for ref in instructions[1:]:
        interpreted += ref[0]

        if isinstance(ref[1], str):
            interpreted += "'" + ref[1] + "'"
        elif isinstance(ref[1], list):
            interpreted += ".".join(ref[1])

    doc = {
        "interpreted": interpreted,
        "instructions": instructions,
        "cursor": run(obj, instructions, method)
    }

    return doc

