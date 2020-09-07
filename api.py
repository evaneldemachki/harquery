import time
import os
import shutil
import json
from haranalyze.core import Profile
from selenium import webdriver
from browsermobproxy import Server

pwd = os.path.dirname(__file__)
if not os.path.exists(pwd+"/dump"):
    os.mkdir(pwd+"/dump")
if not os.path.exists(pwd+"/profile"):
    os.mkdir(pwd+"/profile")

def fetch_har_by_url(url):
    server = Server("./browsermob-proxy-2.1.4//bin//browsermob-proxy")
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
    print(har) # returns a HAR JSON blob

    pwd = os.path.dirname(__file__)
    if not os.path.exists("./URLdump"):
        os.mkdir("./URLdump")
    if not os.path.exists("./URLdump/" + url):
        os.mkdir("./URLdump/" + url)

    with open('./URLdump/' + url + '/source.har', 'w') as json_file:
        json.dump(har, json_file)

    server.stop()
    driver.quit()

def create_profile(name):
    if len(os.listdir(pwd+"/dump")) == 0:
        print("listening for HAR file...")
        while len(os.listdir(pwd+"/dump")) == 0:
            time.sleep(1)

    try:
        if os.listdir(pwd+"/dump")[0].split(".")[-1] == "har":
            fpath = pwd+"/dump/" + os.listdir(pwd+"/dump")[0]
        else:
            raise ValueError("incorrect file extension")
    except:
        raise ValueError("no file extension")

    profile_path = pwd+"/profile/{0}".format(name)
    os.mkdir(profile_path)
    shutil.move(fpath, profile_path + "/source.har")
    with open(profile_path + "/filters.json", "w") as f:
        json.dump([], f)

    print("created profile: {0}".format(name))
    return Profile(name)
