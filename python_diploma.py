import requests
import json
import time

API_TOKEN = '5dfd6b0dee902310df772082421968f4c06443abecbc082a8440cb18910a56daca73ac8d04b25154a1128'
USER_ID = '1054564'
VERSION = "5.68"


def get_friends_list():
    """Получение списка друзей пользователя"""
    print("Получаем список друзей пользователя...")
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
    """Получение множества групп пользователя"""
    print("Получаем группы пользователя...")
    params = {
        "user_id": USER_ID,
        "access_token": API_TOKEN,
        "v": VERSION
    }
    response = requests.get("https://api.vk.com/method/groups.get", params)
    user_groups = response.json().get("response").get("items")
    user_groups_set = set(user_groups)
    return user_groups_set


def get_friends_groups(friends_ids):
    """Получение групп друзей пользователя"""
    print("Получаем группы друзей пользователя...")
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
        print(".", end="", flush=True)
    print("")
    return groups_of_user_friends


def get_ids_of_friends_groups(groups_of_user_friends):
    """Получение множества идентификаторов групп друзей"""
    friends_groups_set = set()
    for friend in groups_of_user_friends:
        try:
            friends_groups_set.update(friend["response"]["items"])
        except:
            if friend["error"]:
                continue
    return friends_groups_set


def intersect_groups(user_groups_set, friends_groups_set):
    """Поиск групп, в которых состоит пользователь, но не состоят друзья"""
    common_groups = user_groups_set & friends_groups_set
    groups_for_export = []
    for group in user_groups_set:
        if group not in common_groups:
            groups_for_export.append(group)
    return groups_for_export


def get_group_info(groups_for_export):
    groups_ids = ",".join(str(group_id) for group_id in groups_for_export)
    params = {
        "group_ids": groups_ids,
        "fields": "members_count",
        "access_token": API_TOKEN,
        "v": VERSION
    }
    response = requests.get('https://api.vk.com/method/groups.getById', params)
    group_info = response.json()["response"]
    with open("groups.json", "w", encoding="utf-8") as f:
        json.dump(group_info, f, ensure_ascii=False)
    print("Результат сохранен в файле groups.json")


if __name__ == "__main__":
    get_group_info(intersect_groups(get_user_groups(), get_ids_of_friends_groups(get_friends_groups(get_friends_list()))))