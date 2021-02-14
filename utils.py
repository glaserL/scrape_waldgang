import pathlib
import urllib.request
from random import gauss
from time import sleep
import os
from typing import Dict, Any


def wait(mu, sigma=3.0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            time_to_sleep = abs(gauss(mu, sigma))
            sleep(time_to_sleep)
            return ret

        return wrapper

    return decorator

@wait(8.0, 2.0)
def download_user_image(url, target_path):
    urllib.request.urlretrieve(url, target_path)

def download_user_images(user_dicts: Dict[Any, Any], path_to_user_images):
    pathlib.Path(path_to_user_images).mkdir(parents=True, exist_ok=True)
    for user in user_dicts:
        user_name = user["user"]["username"]
        target_path = pathlib.Path(path_to_user_images, f"{user_name}.jpg")
        if not os.path.exists(target_path):
            download_user_image(user["user"]["profile_pic_url"], target_path)
