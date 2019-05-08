#!/usr/bin

#pass tag name of code in param 1
GIT_URL=$1
TAG_NAME=$2
START_MOD=$3
REMODE_MODE=$4
echo "REMOTE_MODE="${REMODE_MODE}
echo "START_MOD="${START_MOD}
echo "===================prepare_aoa.sh gogogo!!!"
echo "download start at $(date +%Y-%m-%d\ %H:%M:%S)">>/home/aoadata/upgradetime.txt
#user info for downloading from git repository
CODE_ROOT="/go/src/github.com/Aurorachain"
AOA_ROOT=${CODE_ROOT}/go-aoa

#check code dir, clear if not empty
# CODE_DIR_LINE=`ls -l ${CODE_ROOT}|wc -l`
# echo "CODE_DIR_LINE=${CODE_DIR_LINE}, before download."
# if [${CODE_DIR_LINE} -ne 1]
# then
#     echo "CODE_ROOT clear."
#     rm -rf ${CODE_ROOT}/*
# fi

#check dir
echo "/etc/rc.d/init.d/"
ls -l /etc/rc.d/init.d/
echo "/home/"
ls -l /home/
echo "/home/aoachain/"
ls -l /home/aoachain/
echo "/home/aoadata/"
ls -l /home/aoadata
echo "${CODE_ROOT}"
ls -l ${CODE_ROOT}

if [ "${REMODE_MODE}"x = "local"x ]; then
    echo "===== LOCAL MODE ====="
    cd ${AOA_ROOT}
else
    #download code
    echo "===== REMOTE MODE ====="
    echo "download aoa source code from git, url=${GIT_URL}, tagname=${TAG_NAME}"
    echo "make code root before downloading aoa source code."
    rm -rf ${CODE_ROOT}
    mkdir -p ${CODE_ROOT}
    cd ${CODE_ROOT}
    echo "pwd is "`pwd`
    echo "git clone start."
    git clone ${GIT_URL}
    echo "git clone end."

    cd ${AOA_ROOT}
    echo "checkout tag "${TAG_NAME}
    git checkout ${TAG_NAME}
    echo "download code from git repository finished."
fi

echo "ls -l ${CODE_ROOT}"
ls -l ${CODE_ROOT}
echo "cd to ${AOA_ROOT}"
echo "ls -l /home/aoachain/"
ls -l /home/aoachain/
echo "start to make aoa"
# cd cmd/aoa
# go build .
make aoa
echo "finish doing make aoa"
AOA_BIN=${AOA_ROOT}/build/bin
ls -l ${AOA_ROOT}/build/bin/
# ls -l ${AOA_ROOT}/cmd/aoa/
echo "move aoa binary to /home/aoachain/"
mv ${AOA_BIN}/aoa /home/aoachain/aoa
cd /home/aoachain/
touch aoa.log
echo "change aoa binary to executable mod"
chmod 777 aoa
echo "preparing aoa finish."
echo "start aoa chain in prepare_aoa.sh\n\n\n"
# nohup ./aoa --datadir "/home/aoadata" --port 30303 --rpc --rpcaddr 127.0.0.1 --rpcport 8545 --${START_MOD}#> /dev/null 2>&1 &
# ./aoa --datadir "/home/aoadata/" --port 30303 --rpc --rpcaddr 0.0.0.0 --rpcport 8545 --rpcapi "db,aoa,net,web3,personal" --dev
nohup ./aoa --datadir "/home/aoadata/" --port 30303 --rpc --rpcaddr 0.0.0.0 --rpcport 8545 --rpcapi "db,aoa,net,web3,personal" --"${START_MOD}" > aoa.log 2>&1
# tail -100f aoa.log
# nohup ./aoa --datadir "/home/aoadata/" --port 30303 --rpc --rpcaddr 0.0.0.0 --rpcport 8545 --rpcapi "db,aoa,net,web3,personal" --"${START_MOD}"