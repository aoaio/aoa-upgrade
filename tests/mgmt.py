#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from tests import utils


# 设置管理中的升级合约
def send_request(mgnt_contract_address, account, new_address):
    # old_address = ''
    # new_address = logic_contract_address[3:]
    params = (new_address,)
    func_name_params = 'SendRequest(address)'
    result_obj = utils.contract_call(mgnt_contract_address, account, func_name_params, params)
    order_id = -1
    if result_obj.get('error'):
        print(result_obj['error']['message'])
    else:
        tx_hash = result_obj['result']
        status, receipt = utils.query_receipt(tx_hash)
        if status:
            logs = receipt['result']['logs']
            if len(logs) >= 1:
                topics = logs[len(logs) - 1]['topics']
                order_id = int(topics[1], 16)
                print('order_id: ', order_id)
    return order_id


# 投票
def vote(mgnt_contract_address, account):
    params = ()
    func_name_params = 'vote()'
    result_obj = utils.contract_call(mgnt_contract_address, account, func_name_params, params)
    vote_ended = False
    if result_obj.get('error'):
        print(result_obj['error']['message'])
    else:
        tx_hash = result_obj['result']
        status, receipt = utils.query_receipt(tx_hash)
        if status:
            logs = receipt['result']['logs']
            # print(logs)
            for log in logs:
                topics = log['topics']
                if len(topics) >= 3:
                    order_id = int(topics[1], 16)
                    print('order_id: ', order_id)
            if len(logs) >= 2:
                print("管理合约投票己结束！")
                vote_ended = True
            else:
                print("管理合约投票未结束！")
    return vote_ended


# 撤销投票
def revoke_vote(mgnt_contract_address, account):
    params = ()
    func_name_params = 'revokeVote()'
    result_obj = utils.contract_call(mgnt_contract_address, account, func_name_params, params)
    if result_obj.get('error'):
        print(result_obj['error']['message'])
    else:
        tx_hash = result_obj['result']
        status, receipt = utils.query_receipt(tx_hash)
        if status:
            logs = receipt['result']['logs']
            for log in logs:
                topics = log['topics']
                if len(topics) >= 2:
                    upgrade_order_id = topics[1]
                    order_id = int(upgrade_order_id, 16)
                    print('order_id: ', order_id)
