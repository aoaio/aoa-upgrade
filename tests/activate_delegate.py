#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# file name: activate_delegate.py

"""
activate delegate for Aurorachain accounts
"""

from tests import utils

# 获取所有账号，作为测试账号
print(u'\n\n查询accounts...')
accounts = utils.accounts()
account0 = accounts[0]
print(u'accounts地址: ', accounts)


def activate_delegate(address, password):
    result = {
        "jsonrpc": "2.0",
        "method": "personal_activateDelegate",
        "params": [address, password],
        "id": 666
    }
    tx_result = utils.send_json_rpc_request(result)
    print(tx_result['result'])
    return tx_result['result']


# 激活账号
for account in accounts:
    activate_delegate(account, "")
# 激活账号完成
