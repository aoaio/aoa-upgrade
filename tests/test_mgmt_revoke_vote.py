#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# =======================  logic goes here  =================================================
from tests import *

# 获取account0，作为测试账号
print(u'\n\n查询account0...')
account0 = utils.accounts()[0]
print(u'account0地址: ', account0)
# unlock_account(get_account0)


# 部署升级合约
status, logic_contract_address = utils.deploy_logic_contract(account0)
# logic_contract_address = "AOA37c61cea55e934926335ae7106fac0d4eb8dcc61"


# 部署管理合约
status, mgmt_contract_address = utils.deploy_mgmt_contract(account0)
# mgmt_contract_address = "AOA7a9dc1440e297350aaab0a59419b4bb9b186878a"


# 设置管理中的升级合约
print(u'\n\n发起设置升级合约地址请求...')
new_address = logic_contract_address[3:]
mgmt.send_request(mgmt_contract_address, account0, new_address);
#######


print(u'\n\n\n====================================测试开始====================================')
# 撤销投票
print(u'\n\n管理合约未投票，发起撤销投票请求......')
mgmt.revoke_vote(mgmt_contract_address, account0)
#######


print(u'\n\n\n#################################投票请求不是一个测试用例#################################')
# 投票
print('管理合约发起投票请求...')
mgmt.vote(mgmt_contract_address, account0);
#######
print('#################################投票请求不是一个测试用例#################################')

# 撤销投票
print(u'\n\n\n管理合约己投票，发起撤销投票...')
mgmt.revoke_vote(mgmt_contract_address, account0)
#######


# 撤销投票
print(u'\n\n管理合约己撤销投票，再次发起撤销投票请求...')
mgmt.revoke_vote(mgmt_contract_address, account0)
#######
