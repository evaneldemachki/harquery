from typing import Tuple, Union, Any
from copy import deepcopy

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
    
    raw_str = False
    if directive[0] == "$": # object to raw string
        directive = directive[1:]
        raw_str = True

    reserved = ["!", "#", "=", "@", "->", "$"]
    if any(key in directive for key in reserved):
        raise QueryError("'{0}' is an invalid directive".format(directive))
    
    directive = directive.split(".")
    if raw_str:
        directive.append("$")
    
    return directive

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

    for i in range(len(query_terms)):
        term, op = query_terms[i], logical_terms[i]

        if op in ["!=", "=", "!#", "#"]:
            obj.append( (op, parse_literal(term)) )
        elif op == "@":     
            obj.append( ("@", parse_directive(term)) )
        elif op == "->": 
            obj.append( ("->", parse_directive(term)) )

    return obj

def compare(query: str):
    if query == "!=":
        return lambda a,b: a != b
    elif query == "=":
        return lambda a,b: a == b
    elif query == "!#":
        return lambda a,b: (b not in a) if a is not None else False
    elif query == "#":
        return lambda a,b: (b in a) if a is not None else False

def get_nested(entry: dict, keys: list) -> Any:
    item = entry
    for i in range(len(keys)):
        key = keys[i]
        if key == "$":
            if i != len(keys) - 1:
                raise QueryError("invalid directive")
            
            if not isinstance(item, str):
                item = json.dumps(item)
        else:
            if key in item:
                item = item[key]
            else:
                return None

    return item
    
def execute(obj: list, query: list, mode: str = "focus") -> list:
    cursor = []
    for i in range(len(obj)):
        focus = obj[i]
        locator = None
        response = None
        for key, ix in query:
            if key == "?":
                if locator is not None:
                    raise RuntimeError

                focus = get_nested(focus, ix)
                if mode == "focus":
                    response = focus
                else:
                    response = obj[i]
            elif key == "@":
                if locator is not None:
                    raise RuntimeError

                try:
                    locator = focus
                    focus = []
                    for item in locator:
                        focus_item = get_nested(item, ix)
                        focus.append(focus_item)
                    
                    if mode == "focus":
                        response = focus
                    else:
                        response = obj[i]
                except:
                    raise QueryError("invalid directive '{0}'".format(ix))
            elif key in ["!=", "=", "!#", "#"]:
                # (default) focus:   Any            -> direct comparison -> return
                #           locator: None           -> ignore
                # (after @) focus:   list           -> element-wise comparison
                #           locator: Iterable[dict] -> focus = locator -> reduce -> return
                if locator is None:
                    if compare(key)(focus, ix):
                        if mode == "focus":
                            response = True
                        else:
                            response = obj[i]
                    else:
                        if mode == "focus":
                            response = False
                        else:
                            response = None
                else:
                    # ex. if @ directive was: x and ix = A
                    #   locator = [{x:A, y:1}, {x:B, y:3}, {x:A, y:4}]
                    #   focus   = [A, B, A]
                    match = [] # indices where comparison is True
                    for j in range(len(focus)):
                        if compare(key)(focus[j], ix):
                            match.append(True)
                        else:
                            match.append(False)

                    focus = match
                    if mode == "focus":
                        response = focus
                    else:
                        if not any(focus):
                            response = None
                        else:
                            response = obj[i]
            elif key == "->": 
                # ex. focus   = [True, False, True]
                #     locator = [{x:A, y:1}, {x:B, y:3}, {x:A, y:4}]
                if not isinstance(focus, list):
                    raise QueryError("expected type '{0}', got '{1}'".format(list, type(focus)))
                if locator is None:
                    raise QueryError("got '->' before locator")

                match = []
                for j in range(len(locator)):
                    if focus[j]:
                        focus_item = get_nested(locator[j], ix)
                        match.append(focus_item)
                    else:   
                        match.append(None)

                focus = match
                if mode == "focus":
                    response = [fi for fi in focus if fi is not None]
                else:
                    if not any(focus):
                        response = None
                    else:
                        response = obj[i]

        
        if response is not None:
            cursor.append(response)
    
    return cursor

def parse(query: str) -> dict:
    x, y = reformat(query)
    x, y = process(x, y)
    instructions = build(x, y)

    if instructions[0][1][-1] == "$":
        interpreted = "$" + ".".join(instructions[0][1][:-1])
    else:
        interpreted = ".".join(instructions[0][1])

    for ref in instructions[1:]:
        interpreted += ref[0]

        if isinstance(ref[1], str):
            interpreted += "'" + ref[1] + "'"
        elif isinstance(ref[1], list):
            if ref[1][-1] == "$":
                interpreted += "$" + ".".join(ref[1][:-1])
            else:
                interpreted += ".".join(ref[1])

    doc = {
        "string": interpreted,
        "object": instructions
    }

    return doc

