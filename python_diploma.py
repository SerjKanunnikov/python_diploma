import requests
import json
import time

API_TOKEN = '5dfd6b0dee902310df772082421968f4c06443abecbc082a8440cb18910a56daca73ac8d04b25154a1128'
USER_ID = '39075499'
VERSION = "5.68"


def make_params(**kwargs):
    params = {
        "access_token": API_TOKEN,
        "v": VERSION,
        **kwargs
    }
    return params


def get_friends_list():
    """Получение списка друзей пользователя"""
    print("Получаем список друзей пользователя...")
    response = requests.get('https://api.vk.com/method/friends.get', make_params(user_id=USER_ID))
    friend_list = response.json().get('response').get('items')
    friends_ids = set(friend_list)
    print(friends_ids)
    return friends_ids


def get_user_groups():
    """Получение множества групп пользователя"""
    print("Получаем группы пользователя...")
    response = requests.get("https://api.vk.com/method/groups.get", make_params(user_id=USER_ID))
    user_groups = response.json().get("response").get("items")
    user_groups_set = set(user_groups)
    return user_groups_set


def get_friends_groups(friends_ids):
    """Получение групп друзей пользователя"""
    print("Получаем группы друзей пользователя...")
    groups_of_user_friends = []
    for friend_id in friends_ids:
        response = requests.get('https://api.vk.com/method/groups.get', make_params(user_id=friend_id))
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
    groups_to_get_info = []
    for group in user_groups_set:
        if group not in common_groups:
            groups_to_get_info.append(group)
    return groups_to_get_info


def get_group_info(groups_to_get_info):
    """Получение информации о непересекающихся группах"""
    response = requests.get('https://api.vk.com/method/groups.getById',
                            make_params(group_ids=",".join(str(group_id) for group_id in groups_to_get_info),
                                        fields="members_count"))
    print(response.json())
    group_info = response.json()["response"]
    output = []
    with open("groups.json", "w", encoding="utf-8") as f:
        for group in group_info:
            try:
                group_id = group["id"]
                group_name = group["name"]
                group_members_count = group["members_count"]
                output.append({"id": group_id, "name": group_name, "members_count": group_members_count})
            except:
                continue
        json.dump(output, f, ensure_ascii=False)
    print("Результат сохранен в файле groups.json")


if __name__ == "__main__":
    get_group_info(intersect_groups(get_user_groups(), get_ids_of_friends_groups(get_friends_groups(get_friends_list()))))
    # intersect_groups(get_user_groups(), get_friends_list())