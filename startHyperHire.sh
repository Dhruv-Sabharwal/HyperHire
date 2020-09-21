#!/bin/bash

# don't rewrite paths for Windows Git Bash users
export MSYS_NO_PATHCONV=1
CC_RUNTIME_LANGUAGE=node # chaincode runtime language is node.js
CC_SRC_PATH=/opt/gopath/src/github.com/hyperhire/javascript

# clean the keystore
sudo rm -rf ./hfc-key-store
sudo rm -rf flask/wallet
sudo service docker restart
# launch network; create channel and join peer to channel
sudo chmod a+x bin/configtxgen
sudo chmod a+x bin/cryptogen
sudo chmod a+x basic-network/teardown.sh
cd basic-network
./teardown.sh
sudo rm -rf config
sudo rm -rf crypto-config
mkdir config
mkdir crypto-config
sudo ../bin/cryptogen generate --config=./crypto-config.yaml
sudo ../bin/configtxgen -profile OneOrgOrdererGenesis -outputBlock ./config/genesis.block
sudo ../bin/configtxgen -profile OneOrgChannel -outputCreateChannelTx ./config/channel.tx -channelID mychannel
cd crypto-config/peerOrganizations/org1.example.com/ca/
key1=$(sudo ls| head -n 1)
key2=$(sudo ls| head -n 2|tail -1)
l1=${#key1}
l2=${#key2}
if [ $l1 -gt $l2 ]
then
  key=$key1
else
  key=$key2
fi
cd ..
cd ..
cd ..
cd ..
key_replace="\      \- FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/"$key
echo $key_replace
sudo sed -i "18 c $key_replace" docker-compose.yml
sudo docker-compose -f docker-compose.yml up -d ca.example.com orderer.example.com peer0.org1.example.com couchdb cli
sleep 3
sudo docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org1.example.com/msp" peer0.org1.example.com peer channel create -o orderer.example.com:7050 -c mychannel -f /etc/hyperledger/configtx/channel.tx
sleep 1
sudo docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org1.example.com/msp" peer0.org1.example.com peer channel join -b mychannel.block
sleep 1
sudo docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode install -n hyperhire -v 1.0 -p "/opt/gopath/src/github.com/hyperhire/javascript" -l "node"
sleep 1
sudo docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode instantiate -o orderer.example.com:7050 -C mychannel -n hyperhire -l "node" -v 1.0 -c '{"Args":[]}' -P "OR ('Org1MSP.member','Org2MSP.member')"
echo Success!
sleep 10
sudo docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode invoke -o orderer.example.com:7050 -C mychannel -n hyperhire -c '{"function":"initLedger","Args":[]}'
sleep 2
cd ../flask
mkdir temp
npm install
sleep 5
node enrollAdmin
sleep 5
flask run
