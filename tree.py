
import os
import hashlib
import json

def segments_to_path(index, segments):
    index_cursor = index
    path = os.path.join(
        os.getcwd(), "har.bin", "profile", segments[0])

    for key in segments[1:]:
        index_cursor = index_cursor[key]
        seg_hash = index_cursor["{hash}"]
        path = os.path.join(path, seg_hash)
    
    return path

def index_profile(segments):
    base_path = os.path.join(
        os.getcwd(), "har.bin", "profile", segments[0])

    filters_path = os.path.join(base_path, "filters.json")
    with open(filters_path, "w") as f:
        json.dump([], f)
    
    index_path = os.path.join(base_path, "index.json")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = {}

    index_cursor = index
    file_cursor = base_path
    for seg in segments[1:]:
        if seg not in index_cursor:
            index_cursor[seg] = {}
            index_cursor = index_cursor[seg]

            fn_hash = hashlib.sha1(seg.encode("utf-8")).hexdigest()
            index_cursor["{hash}"] = fn_hash

            file_cursor = os.path.join(file_cursor, fn_hash)
            os.mkdir(file_cursor)

            filters_path = os.path.join(file_cursor, "filters.json")
            with open(filters_path, "w") as f:
                json.dump([], f)
        else:
            index_cursor = index_cursor[seg]
            file_cursor = os.path.join(file_cursor, index_cursor["{hash}"])

    with open(index_path, "w") as f:
        json.dump(index, f)
    
    return index

def profile_tree(index, n=0):
    tree_string = ""
    for key in index:
        if key == "{hash}":
            continue

        child = index[key]
        prefix = "|" + "-" * (n * 2) + " "
        tree_string += prefix + key + "\n"

        if len(child) > 1:
            tree_string += profile_tree(child, n + 1)
    
    return tree_string
