import json, sys
from tqdm import tqdm
from utils import download_user_images

with open(sys.argv[1], encoding="utf-8") as f:
    users = json.load(f)

if len(sys.argv) > 2:
    path = sys.argv[2]
else:
    path = "img"

download_user_images(tqdm(users.values()), path)
