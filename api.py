import time
import os
import shutil
import json
from haranalyze.core import Profile
from selenium import webdriver
from browsermobproxy import Server

#Creates any missing paths that are needed for this program
def create_missing_paths(path):
        if not os.path.exists(os.path.join(os.getcwd(), "/haranalyze")):
            try:
                os.mkdir(os.getcwd() + "/haranalyze")
            except OSError as error:
                print(error)


        if not os.path.exists(os.path.join(os.getcwd(), "/haranalyze/profile")):
            try:
                os.mkdir(os.path.join(os.getcwd(), "/haranalyze/profile"))
            except OSError as error:
                print(error)

        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError as error:
                print(error)

#Delete any har or json that may exist from a pervious run on the same URL
def clear_old_files(path):
        if os.path.exists(path + "/source.har"):
            print("Source found")
            try:
                os.remove(path + "/source.har")
            except OSError as error:
                print(error)

        if os.path.exists(path + "/filters.json"):
            print("Source found")
            try:
                os.remove(path + "/filters.json")
            except OSError as error:
                print(error)


def fetch_har_by_url(url):
    siteName = ''.join([i for i in url if i.isalpha() or i.isnumeric()])
    path = os.getcwd() + "/haranalyze/profile/{0}/".format(siteName)

    create_missing_paths(path)
    clear_old_files(path)

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

    with open(path + "source.har", 'w') as json_file:
        json.dump(har, json_file)

    server.stop()
    driver.quit()

    #TODO: Justin - We should add checks to make sure this path exists incase the har fetch failed.
    return path

def create_profile(url):
    #TODO: delete old files first
    path = fetch_har_by_url(url)

    with open(path + "/filters.json", "w") as f:
        json.dump([], f)

#    print("created profile: {0}".format(name))
#    return Profile(name)
