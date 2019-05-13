#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from tests import *

# 获取account0，作为测试账号
print(u'\n\n查询accounts...')
accounts = utils.accounts()
account0 = accounts[0]
print(u'accounts地址: ', accounts)
# unlock_account(get_account0)


# 部署升级合约
status, logic_contract_address = utils.deploy_logic_contract(account0)
# logic_contract_address = "AOA37c61cea55e934926335ae7106fac0d4eb8dcc61"

# 部署升级合约
status, logic_contract_address_new = utils.deploy_logic_contract(account0)
# logic_contract_address = "AOA37c61cea55e934926335ae7106fac0d4eb8dcc61"


# 部署管理合约
status, mgmt_contract_address = utils.deploy_mgmt_contract(account0)
# mgmt_contract_address = "AOA7a9dc1440e297350aaab0a59419b4bb9b186878a"


# 设置管理中的升级合约
print(u'\n\n升级合约投票未结束，发起设置升级合约地址请求...')
new_address = logic_contract_address[3:]
mgmt.send_request(mgmt_contract_address, account0, new_address);
#######


# 所有账号发起投票请求
print(u'\n\n所有账号发起管理合约投票请求...')
for account in accounts:
    vote_ended = mgmt.vote(mgmt_contract_address, account)
    if vote_ended:
        break
    print()
# 投票结束


#######
print(u'\n\n发起设置升级合约请求后，管理合约投票己结束，发起升级请求...')
version = '1.1'
url = 'test.tar.gz'
md5 = '0ca175b9c0f7d895e2693333333333333333332461'
note = 'upgrade to v1.1'
logic.send_upgrade_request(logic_contract_address, account0, version, url, md5, note);
#######


# 投票结束后，发起请求
print(u'\n\n升级合约投票结束')
for account in accounts:
    vote_ended = logic.vote(logic_contract_address, account)
    if not vote_ended:
        break
    print()
#######


print(u'\n\n\n====================================测试开始====================================')
# 设置管理中的升级合约
print(u'\n\n升级合约投票未结束，再次发起设置升级合约地址请求...')
new_address = logic_contract_address_new[3:]
mgmt.send_request(mgmt_contract_address, account0, new_address);
#######
