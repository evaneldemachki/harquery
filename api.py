import time
import os
import shutil
import json
from haranalyze.core import Profile

pwd = os.path.dirname(__file__)
if not os.path.exists(pwd+"/dump"):
    os.mkdir(pwd+"/dump")
if not os.path.exists(pwd+"/profile"):
    os.mkdir(pwd+"/profile")

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
    
    

            
