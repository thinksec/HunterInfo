#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    : util.py
@Desc    : desc
@Author  : thinksec
@Date    : 2022/9/8 
"""


def check_target_in_black_list(target, black_list):
    """
    检查target是否有黑名单black_list中的关键字
    :return: True为在黑名单中, False则反之
    """
    for black_target in black_list:
        if black_target in target:
            return True
    return False
