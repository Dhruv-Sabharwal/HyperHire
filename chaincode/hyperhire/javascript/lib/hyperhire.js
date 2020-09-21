/*
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const {Contract} = require('fabric-contract-api');
const ClientIdentity = require('fabric-shim').ClientIdentity;

// To store 'key' part in the ledger
let indexName = 'company~candidate'
let concernedIDs;
// list of users
let candidates = [];
let companies = [];

class hyperhire extends Contract {

//  We are not going to use initLedger

    async initLedger(ctx) {
        console.info('============= START : Initialize Ledger ===========');
/*

        const startKey = '0';
        const endKey = '99999';

        const iterator = await ctx.stub.getStateByRange(startKey, endKey);

        while (true) {
            const res = await iterator.next();

            if (res.value && res.value.value.toString()) {
                // console.log(res.value.value.toString('utf8'));
                let appInfo;
                try {
                    appInfo = JSON.parse(res.value.value.toString('utf8'));

                    // update users array and msgID
                    if (msg.msgText === "$HELLO$") {
                        users.push(msg.userID);
                    }

                    msgID += 1;

                } catch (err) {
                    console.log(err);
                    msg = res.value.value.toString('utf8');
                }
            }

            if (res.done) {
                await iterator.close();
                console.log(`users: ${users}`);
                console.log(`numUsers: ${users.length}`);
                console.log(`lastMsgID: ${msgID}`);
                break;
            }
        } */
        console.info('============= END : Initialize Ledger ===========');
    }

    async applyJob(ctx, companyID, candidateID, generalInfo, sensitiveInfo, timestamp) {
        console.info('============= START : applyJob ===========');

        let cid = new ClientIdentity(ctx.stub);
        let ctxID = cid.getID();   //This is actually the long form of the candidateID
	
	//We have to make sure that a candidate does not apply to a company twice	
	//Follow format "\u0000company~candidate\u0000company1\u0000candidate1\u0000"
	let str1 = "\u0000company~candidate\u0000";
	let str2 = "\u0000";
	let searchkey = str1.concat(companyID.toString(),str2,candidateID.toString(),str2);
	const appInfoAsBytes = await ctx.stub.getState(searchkey)
        if (appInfoAsBytes && appInfoAsBytes.length !== 0) {
            throw new Error(`${candidateID} has already applied to ${companyID}`);
        }

        console.log(`companyID : ${companyID}`);
        console.log(`candidateID  : ${candidateID}`);
	console.log(`generalInfo  : ${generalInfo}`);
        console.log(`sensitiveInfo : ${sensitiveInfo}`);
	console.log(`timestamp : ${timestamp}`);

        const accepted = 0;

	// Have to add Timestamp here
        const appInfo = {
            generalInfo,
            sensitiveInfo,
            accepted,
	    timestamp
        };

        // if new candidate, add candidate to candidates array
        if (!(candidates.includes(candidateID))) {
            console.log(`New candidate! Added to candidates array.`);
            candidates.push(candidateID);
        }
	
	// if new company, add company to companies array
        if (!(companies.includes(companyID))) {
            console.log(`New company! Added to companies array.`);
            companies.push(companyID);
        }

    	concernedIDs = ctx.stub.createCompositeKey(indexName, [companyID, candidateID]);   //Creating composite key
	
        await ctx.stub.putState(concernedIDs.toString(), Buffer.from(JSON.stringify(appInfo)));
        console.info('============= END : applyJob ===========');
    }

    async queryCandidate(ctx, companyID, candidateID) {
        console.info('============= START : queryCandidateByID ===========');
        console.log(`candidateID: ${candidateID}`);

        let cid = new ClientIdentity(ctx.stub);
        let ctxID = cid.getID();  //This is actually the long form of the companyID

	//Follow format "\u0000company~candidate\u0000company1\u0000candidate1\u0000"

	let str1 = "\u0000company~candidate\u0000";
	let str2 = "\u0000";
	let searchkey = str1.concat(companyID.toString(),str2,candidateID.toString(),str2);

        //const appInfoAsBytes = await ctx.stub.getStateByPartialCompositeKey(indexName, [companyID, candidateID]); // get the appInfo from chaincode state
	const appInfoAsBytes = await ctx.stub.getState(searchkey)

        if (!appInfoAsBytes || appInfoAsBytes.length === 0) {
            throw new Error(`${candidateID} does not exist`);
        }
        let appInfo;
        appInfo = JSON.parse(appInfoAsBytes.toString());

/*
        // don't show registration $HELLO$ records
        if (msg.msgText === "$HELLO$") {
            throw new Error(`${msgID} does not exist`);
        }
*/
        // don't show sensitiveInfo if flag is not 1
        if (appInfo.accepted !== 1) {
            delete appInfo.sensitiveInfo;
        }
	
        // if new company, add company to companies array
        if (!(companies.includes(companyID))) {
            console.log(`New company! Added to companies array.`);
            companies.push(companyID);
        }

        console.log(appInfo);
        console.info('============= END : queryCandidateByID ===========');
        return JSON.stringify(appInfo);
    }


    async queryAllCandidates(ctx, companyID) {
        console.info('============= START : queryAllCandidates ===========');

        let cid = new ClientIdentity(ctx.stub);
        let ctxID = cid.getID();  //This is actually the long form of the companyID

        const iterator = await ctx.stub.getStateByPartialCompositeKey(indexName, [companyID]); // get the appInfo from chaincode state

        const allResults = [];
        while (true) {
            const res = await iterator.next();

            if (res.value && res.value.value.toString()) {
                // console.log(res.value.value.toString('utf8'));

                //const Key = res.value.key;
		let objectType;
    		let Key;
		objectType, Key = ctx.stub.splitCompositeKey(res.value.key);
		console.log(Key)
                let appInfo;
                try {
                    appInfo = JSON.parse(res.value.value.toString('utf8'));
/*
                    // don't show registration $HELLO$ records
                    if (msg.msgText === "$HELLO$") {
                        continue;
                    }
*/
		    // don't show sensitiveInfo if flag is not 1
		    if (appInfo.accepted !== 1) {
		        delete appInfo.sensitiveInfo;
		    }

                } catch (err) {
                    console.log(err);
                    appInfo = res.value.value.toString('utf8');
                }
                allResults.push({Key, appInfo});
            }

            // if new company, add company to companies array
            if (!(companies.includes(companyID))) {
                console.log(`New company! Added to companies array.`);
                companies.push(companyID);
            }

            if (res.done) {
                await iterator.close();
                console.info(allResults);
                console.info('============= END : queryAllCandidates ===========');
                return JSON.stringify(allResults);
            }
        }
    }

    async acceptCandidate(ctx, companyID, candidateID) {
        console.info('============= START : acceptCandidate ===========');

        let cid = new ClientIdentity(ctx.stub);
        let ctxID = cid.getID();  //This is actually the long form of the companyID

        console.log(`candidateID: ${candidateID}`);
        console.log(`accepting company  : ${companyID}`);

	//Follow format "\u0000company~candidate\u0000company1\u0000candidate1\u0000"

	let str1 = "\u0000company~candidate\u0000";
	let str2 = "\u0000";
	let searchkey = str1.concat(companyID.toString(),str2,candidateID.toString(),str2);

        //const appInfoAsBytes = await ctx.stub.getStateByPartialCompositeKey(indexName, [companyID, candidateID]); // get the appInfo from chaincode state
	const appInfoAsBytes = await ctx.stub.getState(searchkey)
	
        if (!appInfoAsBytes || appInfoAsBytes.length === 0) {
            throw new Error(`${candidateID} does not exist`);
        }
        const appInfo = JSON.parse(appInfoAsBytes.toString());

        /* accept only if:

			1. flagger is not trying to flag a msg with flag = 1 or 2
        */

        if (appInfo.accepted == 0) { 

            console.log(`candidateID ${candidateID} accepted successfully!`);
            appInfo.accepted = 1;

        } else {
            throw new Error(`Cannot accept candidate!`);
        }

	// if new company, add company to companies array
        if (!(companies.includes(companyID))) {
            console.log(`New company! Added to companies array.`);
            companies.push(companyID);
        }
	
	concernedIDs = ctx.stub.createCompositeKey(indexName, [companyID, candidateID]);   //Creating composite key

        await ctx.stub.putState(concernedIDs, Buffer.from(JSON.stringify(appInfo)));
        console.info('============= END : acceptCandidate ===========');
    }

    async rejectCandidate(ctx, companyID, candidateID) {
        console.info('============= START : rejectCandidate ===========');

        let cid = new ClientIdentity(ctx.stub);
        let ctxID = cid.getID();  //This is actually the long form of the companyID

        console.log(`candidateID: ${candidateID}`);
        console.log(`rejecting company  : ${companyID}`);
	
	//Follow format "\u0000company~candidate\u0000company1\u0000candidate1\u0000"

	let str1 = "\u0000company~candidate\u0000";
	let str2 = "\u0000";
	let searchkey = str1.concat(companyID.toString(),str2,candidateID.toString(),str2);

        //const appInfoAsBytes = await ctx.stub.getStateByPartialCompositeKey(indexName, [companyID, candidateID]); // get the appInfo from chaincode state
	const appInfoAsBytes = await ctx.stub.getState(searchkey)

        if (!appInfoAsBytes || appInfoAsBytes.length === 0) {
            throw new Error(`${candidateID} does not exist`);
        }
        const appInfo = JSON.parse(appInfoAsBytes.toString());

        /* reject only if:
			1. flagger is not trying to flag a msg with flag = 1 or 2
        */
        if (appInfo.accepted == 0) {

            console.log(`candidateID ${candidateID} rejected successfully!`);
            appInfo.accepted = 2;

        } else {
            throw new Error(`Cannot reject candidate!`);
        }

	// if new company, add company to companies array
        if (!(companies.includes(companyID))) {
            console.log(`New company! Added to companies array.`);
            companies.push(companyID);
        }
	
	concernedIDs = ctx.stub.createCompositeKey(indexName, [companyID, candidateID]);   //Creating composite key
        await ctx.stub.putState(concernedIDs, Buffer.from(JSON.stringify(appInfo)));
        console.info('============= END : rejectCandidate ===========');
    }

}

module.exports = hyperhire;
