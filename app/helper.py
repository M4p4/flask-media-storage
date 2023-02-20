import os
import shutil
import string
import random
import uuid


def create_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def delete_directory(path: str):
    try:
        dir_path = os.path.dirname(os.path.abspath(path))
        shutil.rmtree(dir_path)
        return True
    except Exception as e:
        print(str(e))
        return False


def delete_file(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            return True
    except Exception as e:
        print(str(e))
        return False
    return False


def get_random_id(length):
    letters = string.ascii_lowercase + string.digits
    return "".join(random.choice(letters) for i in range(length))


def get_uuid():
    return uuid.uuid1()
