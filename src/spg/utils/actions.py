# definitions and functions that provide easy-to-use actions for the user
from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..playground import Playground
from gymnasium import spaces
import collections


def merge_dicts(dict_1: collections.OrderedDict, dict_2: Union[dict, collections.OrderedDict]):
    """
    Merge two dictionaries into one dictionary.
    If the same key is present in both dictionaries, the value from the second dictionary is used.
    """
    if isinstance(dict_2, dict):
        dict_2 = collections.OrderedDict(dict_2)

    for k, v in dict_2.items():

        if k in dict_1 and isinstance(v, (dict, collections.OrderedDict)):
            dict_1[k] = merge_dicts(dict_1.get(k, collections.OrderedDict()), v)
        else:
            dict_1[k] = v

    return dict_1


def replace_values(d):
    for k, v in d.items():
        if isinstance(v, collections.OrderedDict):
            d[k] = replace_values(v)
        else:
            d[k] = d[k] * 0
    return d


def zero_action_space(playground: Playground):

    action = playground.action_space.sample()

    zero_dict = replace_values(action)

    return zero_dict


def fill_action_space(playground: Playground, action: dict):

    zero_action = zero_action_space(playground)

    return merge_dicts(zero_action, action)





