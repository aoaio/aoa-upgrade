#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import time
from tests import *

# 获取account0，作为测试账号
print(u'\n\n查询accounts...')
accounts = utils.accounts()
account0 = accounts[0]
print(u'accounts地址: ', accounts)

# 部署管理合约
status_mgmt, mgmt_contract_address = utils.deploy_mgmt_contract(account0)
# 部署管理合约完成

# 部署升级合约
status, logic_contract_address = utils.deploy_logic_contract(account0)
# 部署升级合约完成


#######
print(u'\n\n发起设置升级合约地址请求...')
new_address = logic_contract_address[3:]
mgmt.send_request(mgmt_contract_address, account0, new_address);
#######


time.sleep(1 * 60)
print(u'\n\n\n====================================测试开始====================================')
# 投票
print(u'\n\n设置升级合约地址请求己过期，发起投票请求...')
mgmt.vote(mgmt_contract_address, account0);
#######
