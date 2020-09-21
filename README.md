# HyperHire
HyperHire is a hiring portal built on the Hyperledger fabric using a flask web application. It allows candidates to upload their resumes in a PDF format to HyperHire. Data is then extracted from the resumes and pushed onto the Hyperledger. The extracted data is divided into 2 parts:
<ol>
<li> Sensitive content - Name, Age, Sex, etc.
<li> General content - Skills, Work Experience, Extra-Curriculars etc.
</ol>
On the recruiter side of the application the general content is converted back to a PDF format with the sensitive content redacted. Upon selection of the candidate for further consideration, a transaction on the ledger leads to the uncovering of the sensitive data. The expectation from HyperHire is the removal of racial, gender or any other sort of bias from the hiring process facilitated through the security, anonymity, and decentralization offered by Hyperledger. HyperHire, allows the Hyperledger to be abstracted away offering the same usability offered by other hiring portals. The applica- tion will have a web-based frontend that allows candidates and recruiters to login and use basic functionalities like applying for jobs and selecting/rejecting applicants. The backend will be built on Hyperledger Fabric.

### Backend Applications
HyperHire consists of 2 distinct, though related, backend applications.
#### 1. Resume Parser
An application that seamlessly converts the candidate's resume from PDF format to an asset that is pushed on to the ledger. On the recruiter side of the application, the general content part of the asset is converted back to PDF format and served to the user. This application consists of a parser that uses sectionizing to extract relevant data while maintaining context.
#### 2. Hyperledger Application
The Hyperledger application is the most important part of our project as it provides the anonymity, security and decentralization which makes HyperHire useful. The ledger consists of the world state that contains data that has been extracted from the PDF and the blockchain that contains the transactions made by the candidates and recruiters. The chaincode of the hyperledger allows the data marked as sensitive to be hidden when a query for the candidate's information is processed. Upon selection of the candidate, through a suitable transaction, the sensitive content becomes visible to the recruiter.






### Requirements
Ensure that Docker, docker-compose, Python3, Python3-dev are installed on your system <br>
Python Library Requirements: ast opencv-python pdf2image nltk tesserocr pillow imutils numpy flask flask-login utils

### Usage
Give execution permissions to start script. Run <code>./startHyperHire.sh</code> (script may take upto 5 minutes to finish, in case of errors re-run script).
