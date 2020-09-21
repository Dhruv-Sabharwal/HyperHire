/*
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const {FileSystemWallet, Gateway} = require('fabric-network');
const fs = require('fs');
const path = require('path');

const ccpPath = path.resolve(__dirname, '..', 'basic-network', 'connection.json');
const ccpJSON = fs.readFileSync(ccpPath, 'utf8');
const ccp = JSON.parse(ccpJSON);
let candidateID, companyID, choice, generalInfo, sensitiveInfo;

process.argv.forEach(function (val, index, array) {
    // console.log(index + ': ' + val);
    choice = array[2];
    companyID = array[3];
    candidateID = array[4];
});

fs.readFile('general.txt', (err, data) => {
    if (err) throw err;
    generalInfo = data.toString();
})

fs.readFile('sensitive.txt', (err, data) => {
    if (err) throw err;
    sensitiveInfo = data.toString();
})

async function main() {
    try {

        // Create a new file system based wallet for managing identities.
        const walletPath = path.join(process.cwd(), 'wallet');
        const wallet = new FileSystemWallet(walletPath);
        console.log(`Wallet path: ${walletPath}`);

        // Check to see if we've already enrolled the candidate.
        const candidateExists = await wallet.exists(candidateID);
        if (!candidateExists) {
            console.log(`An identity for the candidate ${candidateID} does not exist in the wallet`);
            console.log('Run the registerCandidate.js application before retrying');
            return;
        }
	// Check to see if we've already enrolled the company.
	const companyExists = await wallet.exists(companyID);
        if (!companyExists) {
            console.log(`An identity for the company ${companyID} does not exist in the wallet`);
            console.log('Run the registerCompany.js application before retrying');
            return;
        }

        // Create a new gateway for connecting to our peer node.
	var gateway;
	if (choice === 'applyJob') {
            gateway = new Gateway();
            await gateway.connect(ccp, {wallet, identity: candidateID, discovery: {enabled: false}});
	} else {
	    gateway = new Gateway();
            await gateway.connect(ccp, {wallet, identity: companyID, discovery: {enabled: false}});
	}

        // Get the network (channel) our contract is deployed to.
        const network = await gateway.getNetwork('mychannel');

        // Get the contract from the network.
        const contract = network.getContract('hyperhire');

        // Submit the specified transaction.
        // createMsg transaction - requires 5 argument, ex: ('createMsg', 'CAR12', 'Honda', 'Accord', 'Black', 'Tom')
        // flagMsg transaction - requires 2 args , ex: ('flagMsg', 'CAR10', 'Dave')
        if (choice === 'applyJob') {
	    var timestamp = Date.now()
            await contract.submitTransaction('applyJob', companyID, candidateID, generalInfo, sensitiveInfo, timestamp.toString());
            console.log(`${choice} Transaction has been submitted`);
        } else if (choice === 'acceptCandidate') {
            await contract.submitTransaction('acceptCandidate', companyID, candidateID);
            console.log(`${choice} Transaction has been submitted`);
        } else if (choice === 'rejectCandidate') {
            await contract.submitTransaction('rejectCandidate', companyID, candidateID);
            console.log(`${choice} Transaction has been submitted`);
        } else {
            console.log(`${choice} is invalid!`);
        }

        // Disconnect from the gateway.
        await gateway.disconnect();

    } catch (error) {
        console.error(`Failed to submit transaction: ${error}`);
        // process.exit(1);
    }
}

main();
