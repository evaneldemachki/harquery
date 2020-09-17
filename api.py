import os
import json

from harquery.core import Profile, fetch_har_by_url, parse_url
from harquery.tree import segments_to_path, index_profile

if os.name == 'nt':
    # add geckoDriver.exe to PATH
    os.environ["PATH"] += os.path.dirname(__file__)

# Creates any missing paths that are needed for this program
def touch():
    bin_path = os.path.join(os.getcwd(), "har.bin")
    os.mkdir(bin_path)

    prof_path = os.path.join(bin_path, "profile")
    os.mkdir(prof_path)

def create_profile(url):
    #robotsTxt = get_robots_list(url)
    segments = parse_url(url)

    root_path = os.path.join(os.getcwd(), "har.bin", "profile", segments[0])
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

def load_profile(name):
    profile_path = os.path.join(os.getcwd(), "har.bin", "profile")
    if name in os.listdir(profile_path):
        profile = Profile([name])
        return profile
    else:
        print("Profile for '{0}' does not exist".format(name))
        return
