import time
import os
import shutil
import json
from haranalyze.core import Profile
from selenium import webdriver
from browsermobproxy import Server
import urllib.request
import urllib.robotparser
import hashlib

if os.name == 'nt':
    # add geckoDriver.exe to PATH
    os.environ["PATH"] += os.path.dirname(__file__)

def parse_url(url):
    for leader in ("https://", "http://", "www."):
        if url[:len(leader)] == leader:
            url = url[len(leader):]

    if url[-1] == "/":
        url = url[:-1]

    return url.split("/")

#Delete any har or json that may exist from a pervious run on the same URL
def clear_last(path):
    if os.path.exists(os.path.join(path, "source.har")):
        try:
            os.remove(os.path.join(path, "source.har"))
        except OSError as error:
            raise error

#Just a simple function to call for creating a class to clean up the constant if, try, except code from other functions
def create_path(path):
    if not os.path.exists(path):
         try:
             os.mkdir(path)
         except OSError as error:
             raise error

# Creates any missing paths that are needed for this program
def auto_index(segments):
    bin_path = os.path.join(os.getcwd(), "har.bin")
    create_path(bin_path)


    prof_path = os.path.join(bin_path, "profile")
    create_path(prof_path)

    root_path = os.path.join(prof_path, segments[0])
    create_path(root_path)

    index_path = os.path.join(root_path, "index.json")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = {}

    index_cursor = index
    file_cursor = root_path
    for node in segments[1:]:
        if node not in index_cursor:
            index_cursor[node] = {}

        index_cursor = index_cursor[node]

        fn_hash = hashlib.sha1(node.encode("utf-8")).hexdigest()
        file_cursor = os.path.join(file_cursor, fn_hash)
        create_path(file_cursor)

    with open(index_path, "w") as f:
        json.dump(index, f)

    return file_cursor

def get_robots_list(url) -> list:
    print(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url("{0}/robots.txt".format(url))
    rp.read()
    rrate = rp.request_rate("*")
    return rp.__str__().split("\n")

def fetch_har_by_url(url):
    segments = parse_url(url)
    curr_path = auto_index(segments)

    project_dir = os.path.dirname(__file__)
    bpm_path = os.path.join(project_dir, "browsermob-proxy-2.1.1/bin/browsermob-proxy")

    server = Server(bpm_path)
    server.start()
    proxy = server.create_proxy()

    profile  = webdriver.FirefoxProfile()
    profile.set_proxy(proxy.selenium_proxy())
    driver = webdriver.Firefox(firefox_profile=profile)

    proxy.new_har(url, options={'captureHeaders': True, 'captureContent': True, 'captureBinaryContent': True})

    #TODO: Justin - I don't think we need this wait, anyone have any thoughts?
    proxy.wait_for_traffic_to_stop(2000, 10000)

    driver.get(url)

    har = proxy.har
    path = os.path.join(curr_path, "source.har")
    with open(path, 'w') as json_file:
        json.dump(har, json_file)

    server.stop()
    driver.quit()

    return os.path.join(
        os.getcwd(), "har.bin",
        "profile", segments[0]
    )

def create_profile(url):
    #TODO: delete old files first
    robotsTxt = get_robots_list(url)
    path = fetch_har_by_url(url)

    filters_path = os.path.join(path, "filters.json")
    with open(filters_path, "w") as f:
        json.dump([], f)

#    print("created profile: {0}".format(name))
#    return Profile(name)
