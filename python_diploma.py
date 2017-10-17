import requests
import json
import time
from config import API_TOKEN, USER_ID, VERSION

TOO_MANY_REQUESTS = 6
USER_IS_BANNED = 18


def make_params(**kwargs):
    """Формирование словаря с параметрами запроса"""
    params = {
        "access_token": API_TOKEN,
        "v": VERSION,
        **kwargs
    }
    return params


def make_request(url, params):
    """Создание запроса и обработка ошибок"""
    response = requests.get(url, params)
    response.raise_for_status()
    res = response.json()
    if res.get("response"):
        return res.get("response")
    elif res.get("error"):
        if res["error"]["error_code"] == TOO_MANY_REQUESTS:
            print(res.get("error"))
            print("Превышен лимит запросов, повторяем...")
            time.sleep(1)
            return make_request(url, params)
        elif res["error"]["error_code"] == USER_IS_BANNED:
            print(res.get("error"))
            print("Пользователь заблокирован в группе, пропускаем...")


def get_friends_list():
    """Получение списка друзей пользователя"""
    print("Получаем список друзей пользователя...")
    friends = make_request("https://api.vk.com/method/friends.get", params=make_params(user_id=USER_ID))
    friends_ids = set(friends.get('items'))
    return friends_ids


def get_user_groups():
    """Получение множества групп пользователя"""
    print("Получаем группы пользователя...")
    user_groups_response = make_request("https://api.vk.com/method/groups.get", params=make_params(user_id=USER_ID))
    user_groups_set = set(user_groups_response.get("items"))
    return user_groups_set


def get_friends_groups(friends_ids):
    """Получение групп друзей пользователя"""
    print("Получаем группы друзей пользователя...")
    groups_of_user_friends = []
    for friend_id in friends_ids:
        try:
            friend_groups_response = make_request('https://api.vk.com/method/groups.get',
                                                  make_params(user_id=friend_id))
            groups_of_user_friends.append(friend_groups_response["items"])
            print(".")
        except TypeError:
            pass
    print()
    return groups_of_user_friends


def get_ids_of_friends_groups(groups_of_user_friends):
    """Получение множества идентификаторов групп друзей"""
    friends_groups_set = set()
    for friend in groups_of_user_friends:
        friends_groups_set.update(friend)
    return friends_groups_set


def group_difference(user_groups_set, friends_groups_set):
    """Поиск групп, в которых состоит пользователь, но не состоят друзья"""
    different_groups = user_groups_set - friends_groups_set
    return different_groups


def get_group_info(groups_to_get_info):
    """Получение информации о непересекающихся группах"""
    group_info = make_request('https://api.vk.com/method/groups.getById',
                            make_params(group_ids=",".join(str(group_id) for group_id in groups_to_get_info),
                                        fields="members_count"))
    output = []
    with open("groups.json", "w", encoding="utf-8") as f:
        for group in group_info:
            group_id = group["id"]
            group_name = group["name"]
            group_members_count = group["members_count"]
            output.append({"id": group_id, "name": group_name, "members_count": group_members_count})
        json.dump(output, f, ensure_ascii=False)
    print("Результат сохранен в файле groups.json")


if __name__ == "__main__":
    get_group_info(group_difference(get_user_groups(),
                                    get_ids_of_friends_groups(get_friends_groups(get_friends_list()))))
