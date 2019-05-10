#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# file name: utils.py

import json
import os
import sys
import platform
import stat
import subprocess
import time
from urllib import request

from rlp import encode
# 部署AOAUpgradeLogic合约
from web3 import Web3


def deploy_logic_contract(account0):
    sol_file = 'AOAUpgradeLogic.sol'
    print(u'\n\n开始部署合约' + sol_file + '...')
    bin_str = compile_contract(sol_file)
    status, logic_contract_address = deploy_contract(account0, bin_str, sol_file)
    print()
    return status, logic_contract_address


def deploy_mgmt_contract(account0):
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


def query_receipt(tx_hash):
    '''查询收据'''
    params = {
        "jsonrpc": "2.0",
        "method": "aoa_getTransactionReceipt",
        "params": [tx_hash],
        "id": 1
    }
    print(u'10秒之后开始查询收据...')
    time.sleep(10)
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
    print("status:", result)
    return result_bool, result_contract_address


def compile_contract(filename):
    '''编译合约，返回abi和bin'''
    # current_dir = os.getcwd()
    # print(current_dir)

    # while 'contract' not in os.listdir(current_dir):
    #     current_dir = os.path.abspath(os.path.join(current_dir, '..'))
    #     if len(current_dir) == 1 and current_dir == "/":
    #         break
    #
    # print(current_dir)
    # contract_path = current_dir + "/contract"
    contract_path = sys.argv[1]
    contract_out_dir = contract_path + "/out"
    file_path = contract_out_dir + "/" + filename.split(".")[0] + ".bin"

    # rm ./contract/out dir
    run_cmd("rm -rf " + contract_out_dir)

    # docker run to compile contract
    solc_cmd = ":/home/aoa 4dfdb58e326a solc --bin /home/aoa/"
    out_cmd = " --overwrite -o /home/aoa/out"

    system = platform.system()
    if system == "Linux":
        cmd = "docker run -u " + str(os.geteuid()) + " -v " + contract_path + solc_cmd + filename + out_cmd
    else:
        cmd = "docker run -v " + contract_path + solc_cmd + filename + out_cmd
    print(u'合约编译命令: ' + cmd)
    run_cmd(cmd)

    # change contract_out_dir permission
    os.chmod(contract_out_dir, stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU)
    # os.chown(contract_out_dir, os.geteuid(), os.getegid())

    # read ./out/*.bin file
    bin_str = ""
    if os.path.exists(file_path):
        f = open(file_path, "r")
        bin_str = '0x' + f.read()
        # print(bin_str)
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


def contract_call(contract_address, delegate_address, function_name_params, request_list):
    params = {
        "jsonrpc": "2.0",
        "method": "aoa_sendTransaction",
        "params": [{
            "from": delegate_address,
            "to": contract_address,
            "gas": "0x7a012",
            "data": compose_sol_data(function_name_params, request_list),
            "action": 6}],
        "id": "1"
    }
    hash = send_json_rpc_request(params)
    return hash


def compose_sol_data(method_name_params, params):
    method_name_params = method_name_params.replace('uint,', 'uint256,').replace('uint)', 'uint256)')
    fn_selector = Web3.toHex(Web3.sha3(text=method_name_params))
    fn_selector = fn_selector[0:10]
    print('function: ', method_name_params, ', function selector: ', fn_selector)

    param_types = []
    argstr = method_name_params.split('(')[1].split(')')[0]
    if argstr.strip():
        methodParams = argstr.split(',')
        for i in range(len(methodParams)):
            param_types.append(methodParams[i])
    # print('param_types', param_types, 'len: ', len(param_types))
    print('params', params, 'len: ', len(params))
    if (len(param_types) != len(params)):
        print('!!!parameters number is wrong.')
        return

    params_list = []
    for i in range(len(param_types)):
        params_list.append((param_types[i], params[i]))

    # print('params_list: ', params_list)
    first_list = [fn_selector]
    second_list = {}

    for i in range(len(params_list)):
        item = params_list[i]
        p_type, p_value = item[0], item[1]
        if p_type in ('bytes', 'string'):
            str_len, str_txt = rlp(p_value)
            result = str_len + str_txt
            second_list[i] = result
            pass
        elif '[]' in p_type:
            pass
        else:
            pass

    first_list = []
    param_num = len(param_types)
    start_pos = param_num * 32
    last_len = 0
    for i in range(len(params_list)):
        item = params_list[i]
        p_type, p_value = item[0], item[1]
        if p_type in ('bytes', 'string') or '[]' in p_type:
            # print('last_len=', last_len)
            first_list.append(str(Web3.toHex(start_pos + last_len))[2:].zfill(64))  # 起始位置
            last_len += int(len(second_list[i]) / 2)
            # start_pos += last_len
        elif p_type == 'address':
            first_list.append(p_value.zfill(64))
        else:
            first_list.append(str(Web3.toHex(p_value))[2:].zfill(64))  # 固定类型的值

    # print(first_list)
    # print()
    # print(second_list.values())
    # print()
    first_list += second_list.values()
    result_str = ''
    for part in first_list:
        result_str += part
    # print('final data: ', fn_selector+result_str)
    return fn_selector + result_str


def rlp(str_temp):
    str_temp = encode(str_temp).hex()
    ret1 = str_temp[2:]

    ret2 = hex(int(str_temp[0:2], 16) - int('80', 16))[2:]
    # print(ret2)
    length = len(str_temp)
    if length <= 64:
        ret1 = ret1.ljust(64, '0')
    elif length <= 128:
        ret1 = ret1.ljust(128, '0')
    elif length <= 160:
        ret1 = ret1.ljust(160, '0')
    elif length <= 256:
        ret1 = ret1.ljust(256, '0')
    else:
        pass
    return str(ret2).zfill(64), ret1
