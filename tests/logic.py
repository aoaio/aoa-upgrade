#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from tests import utils


# 发起请求
def send_upgrade_request(logic_contract_address, account, version, url, md5, note):
    # version = '1.1'
    # url = 'test.tar.gz'
    # md5 = '0ca175b9c0f7d895e2693333333333333333332461'
    # note = 'upgrade to v1.1'
    params = (version, url, md5, note)
    func_name_params = 'SendUpgradeRequest(string,string,string,string)'
    result_obj = utils.contract_call(logic_contract_address, account, func_name_params, params)
    if result_obj.get('error'):
        print(result_obj['error']['message'])
    else:
        tx_hash = result_obj['result']
        status, receipt = utils.query_receipt(tx_hash)

        if status:
            logs = receipt['result']['logs']
            if len(logs) >= 1:
                topics = logs[len(logs) - 1]['topics']
                upgrade_order_id = topics[1]
                order_id = int(upgrade_order_id, 16)
                print('order_id: ', order_id)


# 投票
def vote(logic_contract_address, account):
    params = ()
    func_name_params = 'vote()'
    result_obj = utils.contract_call(logic_contract_address, account, func_name_params, params)
    vote_ended = False;
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
                    upgrade_order_id = topics[1]
                    order_id = int(upgrade_order_id, 16)
                    print('order_id: ', order_id)
            if len(logs) >= 2:
                print("升级合约投票己结束！")
                vote_ended = True
            else:
                print("升级合约投票未结束！")
    return vote_ended


# 撤销投票
def revoke_vote(logic_contract_address, account):
    params = ()
    func_name_params = 'revokeVote()'
    result_obj = utils.contract_call(logic_contract_address, account, func_name_params, params)
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


# 取消升级
def cancel(logic_contract_address, account):
    params = ()
    func_name_params = 'cancel()'
    result_obj = utils.contract_call(logic_contract_address, account, func_name_params, params)
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
                    order_id = int(topics[1], 16)
                    print('order_id: ', order_id)
