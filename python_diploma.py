import requests
import json
import time

API_TOKEN = '5dfd6b0dee902310df772082421968f4c06443abecbc082a8440cb18910a56daca73ac8d04b25154a1128'
USER_ID = '39075499'
VERSION = "5.68"


def get_friends_list():
    params = {
        "user_id": USER_ID,
        "fields": "first_name",
        "access_token": API_TOKEN,
        "v": VERSION
    }
    response = requests.get('https://api.vk.com/method/friends.get', params)
    friend_list = response.json().get('response').get('items')
    friends_ids = []
    for friend in friend_list:
        friends_ids.append(friend["id"])
    return friends_ids


def get_user_groups():
    params = {
        "user_id": USER_ID,
        "access_token": API_TOKEN,
        "v": VERSION
    }
    response = requests.get("https://api.vk.com/method/groups.get", params)
    user_groups = response.json()
    user_groups_set = set(user_groups)
    return user_groups_set


def get_friends_groups(friends_ids):
    groups_of_user_friends = []
    for friend_id in friends_ids:
        params = {
            "user_id": friend_id,
            "access_token": API_TOKEN,
            "v": VERSION
        }
        response = requests.get('https://api.vk.com/method/groups.get', params)
        friend_groups = response.json()
        groups_of_user_friends.append(friend_groups)
        time.sleep(0.5)
    return groups_of_user_friends


def get_ids_of_friends_groups(groups_of_user_friends):
    groups_list = []
    for friend in groups_of_user_friends:
        print(friend["response"]["items"])
        groups_list.append(set(friend["response"]["items"]))
    # groups_set = set(groups_list)
    print(groups_list)
    return groups_list


def intersect_groups(user_groups, groups_list):
    spy_games = user_groups & groups_list
    print(spy_games)

# def export_json():


if __name__ == "__main__":
    intersect_groups(get_user_groups(), get_ids_of_friends_groups(get_friends_groups(get_friends_list())))

    # get_groups(get_friends_list())
    # get_user_groups()