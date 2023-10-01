import json
import ast


def get_value_from_data(data, key):
    """
    helper function for getting required value from data by passing key
    :param data:
    :param key:
    :return:
    """
    value = None
    try:
        value = data.get(key)
    except:
        value = None
    finally:
        return value


def dict_keys_values_to_str(data, keys):
    """
    helper function for getting required value from data by passing key
    :param keys:
    :param data:
    :param key:
    :return:
    """
    try:
        for key in keys:
            data.update({key: json.dumps(data.get(key))})
    except:
        data = None
    finally:
        return data


def dict_keys_values_to_list(data, keys):
    """
    helper function for getting required value from data by passing key
    :param keys:
    :param data:
    :param key:
    :return:
    """
    try:
        for key in keys:
            value = ast.literal_eval(data.get(key))
            data.update({key: value})
    except:
        data = None
    finally:
        return data
