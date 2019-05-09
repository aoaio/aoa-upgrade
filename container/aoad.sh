#!/usr/bin

#close aoa process
echo "doing stop"
PIDS=`ps -ef | grep java | grep "AOA" |awk '{print $2}'`
if [ -z "$PIDS" ]; then
    echo "ERROR: AOA does not started!"
    exit 1
fi
echo -e "Stopping AOA ...\c"
for PID in $PIDS ; do
    kill $PID > /dev/null 2>&1
done
echo "kill aoachain"

#backup old aoa
mv /home/aoachain/aoa /home/aoachain/bak

#move new aoa
mv home/aoachain/new/aoa /home/aoachain/aoa

#start new aoa
cd /home/aoachain/
echo "cd to /home/aoachain/"
chmod +x aoa
echo "start aoachain"
nohup ./aoa --datadir "/home/aoadata/" --port 30303 --rpc --rpcaddr 0.0.0.0 --rpcport 8545 --rpcapi "db,aoa,net,web3,personal" --"dev" > home/aoadata/aoa.log 2>&1
