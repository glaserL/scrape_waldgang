import json
from re import findall
import os
from tqdm import tqdm

from utils import wait


class ProfileDict:
    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._dict, f, indent=2, ensure_ascii=False)

    def __init__(self, path, api):
        self.path = path
        self.api = api
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self._dict = json.load(f)
                print(f"Loaded {len(self._dict)} users from disk.")
        else:
            self._dict = {}

    def get(self, user_id):
        if str(user_id) in self._dict.keys():
            return self._dict[str(user_id)]
        elif int(user_id) in self._dict.keys():
            return self._dict[int(user_id)]

        else:
            user = self.get_profile_from_instagram(user_id)
            self.add(user_id, user)
            return user

    def add(self, user_id, user_dict):
        self._dict[user_id] = user_dict
        self.save()

    @wait(8, 4)
    def get_profile_from_instagram(self, user_id):
        result = self.api.user_info(user_id)
        return result



def add_comments(api, posts, config):
    for post in tqdm(posts):
        user_id = post['user']['pk']
        try:
            if post["comment_count"] > 0:
                comments = get_comments(api, post["id"], post["comment_count"])
            else:
                comments = []
            post["comments"] = comments
            if post["comment_count"] > 0:
                break
        except Exception as e:
            print(f"Failed to get comments. {e}")
            break
    return posts


def crawl_users(api, user_ids, target_path_for_profiles, config):
    profiles = ProfileDict(target_path_for_profiles, api)
    for user_ids in tqdm(user_ids):
        _ = profiles.get(user_ids)
    return profiles



@wait(6.0)
def get_comments(api, id, no_of_comments):
    all_comments = []
    comments = api.media_comments(id, count=min(no_of_comments, 20))
    all_comments.extend([comment for comment in comments["comments"]])
    return all_comments


def extract_relevant_from_comments(j):
    result = {
        "name": j["user"]["username"],
        "full_name": j["user"]["full_name"],
        "text": j["text"]
    }
    return result

@wait(8.0)
def request_posts_from_instagram(api, hashtag, rank_token, max_id=None):
    if max_id is None:
        results = api.feed_tag(hashtag, rank_token=rank_token)
    else:
        results = api.feed_tag(hashtag, rank_token=rank_token, max_id=max_id)
    print(f"Successfully requested {len(results.get('items', ''))} more for {hashtag} ({max_id})..")
    return results


@wait(7.5, 2.0)
def request_likers(api, post_id, count):
    return api.media_likers(post_id, count=count)


def add_likers(api, raw_data, config):
    for post in raw_data:
        try:
            like_count = post["like_count"]
            likers = post.get("likers", [])
            if like_count > 0 and len(likers) < like_count:
                num_of_likers_to_get = min(50, post["like_count"])
                new_likers = request_likers(api, post["id"], num_of_likers_to_get)
                likers.extend(new_likers)
            likers = list(set(likers))
            post["likers"] = likers
        except Exception as e:
            print(e)
            break
    return raw_data


def get_posts(api, hashtag, config):
    feed = []
    uuid = api.generate_uuid(return_hex=False, seed='0')
    result = request_posts_from_instagram(api, hashtag, uuid)
    feed.extend(result.get("items", []))
    while result["more_available"] and len(feed) < config['max_collect_media']:
        try:
            next_max_id = result["next_max_id"]
            result = request_posts_from_instagram(api, hashtag, uuid, next_max_id)
            feed.extend(result.get("items", []))
        except Exception as e:
            print(e)
            break
    print(f"Collected {len(feed)} posts for hashtag {hashtag}")
    return feed
