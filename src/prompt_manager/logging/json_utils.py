from typing import Any


def iterate_dict(data: dict):
    new_dict = {}
    for key, value in data.items():
        new_dict[key] = normalize(value)
    return new_dict
def iterate_list(items: list):
    new_list = []
    for item in items:
        new_list.append(normalize(item))
    return new_list


def normalize(obj: Any) -> Any:
    """
    Function that tries to convert a given object to JSON
    """

    # check if the object is a primitive
    if isinstance(obj, int) or isinstance(obj, str) or obj is None or isinstance(obj, float):
        return obj
    elif isinstance(obj, list):
        return iterate_list(obj)
    elif isinstance(obj, dict):
        return iterate_dict(obj)
    elif isinstance(obj, tuple):
        return iterate_list(list(obj))
    elif hasattr(obj, "__dict__"):
        return iterate_dict(obj.__dict__)
    else:
        return str(obj)
