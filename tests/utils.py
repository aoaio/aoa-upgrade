#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# file name: utils.py

import json
import os
import platform
import subprocess
import time
from urllib import request


# 部署AOAUpgradeLogic合约
def compile_logic_contract(account0):
    sol_file = 'AOAUpgradeLogic.sol'
    print(u'\n\n开始部署合约' + sol_file + '...')
    bin_str = compile_contract(sol_file)
    status, logic_contract_address = deploy_contract(account0, bin_str, sol_file)
    print()
    return status, logic_contract_address


def compile_mgmt_contract(account0):
    # 部署AOAUpgradeMgmt合约
    sol_file = 'AOAUpgradeMgmt.sol'
    print(u'\n\n开始部署合约' + sol_file + '...')
    bin_str = compile_contract(sol_file)
    status, mgmt_contract_address = deploy_contract(account0, bin_str, sol_file)
    print()
    # mgmt_contract_address = "AOA7a9dc1440e297350aaab0a59419b4bb9b186878a"
    return status, mgmt_contract_address


def deploy_contract(from_address, bin_str, sol_file):
    '''部署合约'''
    params = {
        "jsonrpc": "2.0",
        "method": "aoa_sendTransaction",
        "params": [{"from": from_address, "gas": "0x7a012", "data": bin_str, "action": 5}],
        "id": "1"
    }
    result_obj = send_json_rpc_request(params)
    tx_hash = result_obj['result']
    status, receipt = query_contract_receipt(tx_hash)
    contract_address = receipt['result']['contractAddress']
    print(sol_file, u'合约地址: ', contract_address)
    return status, contract_address


def query_contract_receipt(tx_hash):
    '''查询收据'''
    params = {
        "jsonrpc": "2.0",
        "method": "aoa_getTransactionReceipt",
        "params": [tx_hash],
        "id": 1
    }
    print(u'15秒之后开始查询收据...')
    time.sleep(15)
    result_contract_address = send_json_rpc_request(params)
    result = result_contract_address['result']['status']
    result_bool = False
    if result == '0x1':
        result_str = u'成功'
        result_bool = True
    else:
        result_str = u'失败'

    print()
    print('执行结果： ', result_str)
    # print("status:", result)
    return result_bool, result_contract_address


def compile_contract(filename):
    '''编译合约，返回abi和bin'''
    src_dir = os.getcwd()
    system = platform.system()
    father_path = os.path.abspath(os.path.dirname(src_dir) + os.path.sep + ".")
    # print(father_path)
    contract_path = father_path + "/contract"
    out_path = contract_path + "/out"

    file_path = out_path + "/" + filename.split(".")[0] + ".bin"
    if os.path.exists(file_path):
        pass
        os.remove(file_path)
    # cmd_remove_logic_bin = "rm -rf " + file_path
    # run_cmd(cmd_remove_logic_bin)

    solc_cmd = ":/home/aoa 4dfdb58e326a solc --bin --abi /home/aoa/"
    out_cmd = " -o /home/aoa/out"
    uid = os.geteuid();
    print(uid)
    cmd = None
    if system == "Linux":
        cmd = "docker run -u " + str(uid) + " -v " + contract_path + solc_cmd + filename + out_cmd
    else:
        cmd = "docker run -v " + contract_path + solc_cmd + filename + out_cmd
    print(u'合约编译命令: ' + cmd)
    run_cmd(cmd)

    # AOAd8db74f2f68b51dd418869d384e02947a737cb61
    bin_str = ""
    if os.path.exists(file_path):
        f = open(file_path, "r")
        bin_str = '0x' + f.read()
        print(bin_str)
        f.close()
    else:
        print("No such file: %s" % file_path)
        exit(0)
    return bin_str


def run_cmd(cmd):
    # 工具方法，运行一条命令，返回回显
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd(),
        shell=True)
    out, err = p.communicate()
    if p.returncode != 0:
        print("Non zero exit code:%s executing: %s" % (p.returncode, cmd))
        print("Excute CMD Err: {}".format(err.decode()))
    return out.decode()


def send_json_rpc_request(params):
    req_data = json.dumps(params).encode(encoding='utf-8')
    header_dict = {"Content-Type": "application/json", "jsonrpc": "2.0"}
    # url = "http://172.16.4.14:8545"
    url = "http://127.17.0.1:8546"
    # url = "http://172.16.4.128:8546"
    req = request.Request(url=url, data=req_data, headers=header_dict)
    res = request.urlopen(req)
    result = res.read()
    # print(u"响应消息:" + result.decode(encoding='utf-8'))
    result_obj = json.loads(result)
    # if "error" in result_obj:
    #     print(params["nanaerror"] + result.decode(encoding='utf-8'))
    #     print("nanaerror == "+ result.decode(encoding='utf-8'))
    return result_obj


def accounts():
    params = {
        "jsonrpc": "2.0",
        "method": "aoa_accounts",
        "params": [],
        "id": 1
    }
    result_account = send_json_rpc_request(params)
    print(result_account)
    return result_account['result']
