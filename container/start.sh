#!/usr/bin

START_MOD=$1
REMODE_MODE=$2
START_PLACE=$3

echo "===================start.sh gogogo!!!\n"

file=/home/aoachain/aoa
if [ ! -f "$file" ]; then
    echo "aoa not exist, make aoa from source code."
    GIT_URL="http://tangchaoyu:aoawin2019@git.aoainside.com/Aurora/go-aoa.git"
    TAG_NAME="release_0_2_0"
    sh /etc/rc.d/init.d/prepare_aoa.sh ${GIT_URL} ${TAG_NAME} ${START_PLACE} ${START_MOD} ${REMODE_MODE}
else
    echo "start aoa chain in start.sh"
    cd /home/aoachain/
    echo "cd to /home/aoachain/"
    # ./aoa --datadir "/home/aoadata/" --port 30303 --rpc --rpcaddr 0.0.0.0 --rpcport 8545 --rpcapi "db,aoa,net,web3,personal" --"${START_MOD}"
    # nohup ./aoa --datadir="/home/aoadata" --port 30303 --rpc --rpcaddr 127.0.0.1 --rpcport 8545 --${START_MOD}#> /dev/null 2>&1 &
fi