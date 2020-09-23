import os
import json

from harquery.core import Profile, Filters, fetch_har_by_url, parse_url
from harquery.tree import segments_to_path, index_profile
from harquery.endpoint import Endpoint

# if os.name == 'nt':
#     # add geckodriver.exe to PATH
#     os.environ["PATH"] += os.path.dirname(__file__)
#     print(os.path.dirname(__file__))

# Creates any missing paths that are needed for this program
def touch():
    bin_path = os.path.join(os.getcwd(), ".hq")
    if not os.path.exists(bin_path):
        os.mkdir(bin_path)

    prof_path = os.path.join(bin_path, "profiles")
    if not os.path.exists(prof_path):
        os.mkdir(prof_path)

    ep_path = os.path.join(bin_path, "endpoints")
    if not os.path.exists(ep_path):
        os.mkdir(ep_path)

    presets_path = os.path.join(bin_path, "presets")
    if not os.path.exists(presets_path):
        os.mkdir(presets_path)

def scan(url):
    #robotsTxt = get_robots_list(url)
    segments = parse_url(url)
    url = "http://" + "/".join(segments)

    root_path = os.path.join(os.getcwd(), ".hq", "profiles", segments[0])
    if not os.path.exists(root_path):
        os.mkdir(root_path)

    index = index_profile(segments)

    har = fetch_har_by_url(url, segments, index)

    curr_path = segments_to_path(index, segments)
    source_path = os.path.join(curr_path, "source.har")
    with open(source_path, 'w') as json_file:
        json.dump(har, json_file)
    
    print("created profile for: {0}".format(url))

    profile = Profile(segments)
    return profile

def load(name):
    profile_path = os.path.join(os.getcwd(), ".hq", "profiles")
    if name in os.listdir(profile_path):
        profile = Profile([name])
        return profile
    else:
        print("Profile for '{0}' does not exist".format(name))
        return

def add_endpoint(entry):
    try:
        return Endpoint(entry)
    except:
        raise

# TODO
def load_endpoint(entry):
    pass

def add_preset(name: str, filters: Filters):
    preset_path = os.path.join(os.getcwd(), ".hq", "presets", name + ".json")
    if os.path.exists(preset_path):
        raise FileExistsError

    with open(preset_path, "w") as f:
        json.dump(filters._obj, f)
    
    print("Added new filters preset: {0}".format(name))

def update_preset(name: str, filters: Filters):
    preset_path = os.path.join(os.getcwd(), ".hq", "presets", name + ".json")
    if not os.path.exists(preset_path):
        raise FileNotFoundError

    with open(preset_path, "w") as f:
        json.dump(filters._obj, f)
    
    print("Updated filters preset: {0}".format(name))        

