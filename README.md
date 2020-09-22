# HyperHire
HyperHire is a hiring portal built on the Hyperledger fabric using a flask web application. It allows candidates to upload their resumes in a PDF format to HyperHire. Data is then extracted from the resumes and pushed onto the Hyperledger. The extracted data is divided into 2 parts:
<ol>
<li> Sensitive content - Name, Age, Sex, etc.
<li> General content - Skills, Work Experience, Extra-Curriculars etc.
</ol>
On the recruiter side of the application the general content is converted back to a PDF format with the sensitive content redacted. Upon selection of the candidate for further consideration, a transaction on the ledger leads to the uncovering of the sensitive data. The expectation from HyperHire is the removal of racial, gender or any other sort of bias from the hiring process facilitated through the security, anonymity, and decentralization offered by Hyperledger. HyperHire, allows the Hyperledger to be abstracted away offering the same usability offered by other hiring portals. The application will have a web-based frontend that allows candidates and recruiters to login and use basic functionalities like applying for jobs and selecting/rejecting applicants. The backend will be built on Hyperledger Fabric.

### Backend Applications
HyperHire consists of 2 distinct, though related, backend applications.
#### 1. Resume Parser
An application that seamlessly converts the candidate's resume from PDF format to an asset that is pushed on to the ledger. On the recruiter side of the application, the general content part of the asset is converted back to PDF format and served to the user. This application consists of a parser that uses sectionizing to extract relevant data while maintaining context.
#### 2. Hyperledger Application
The Hyperledger application is the most important part of our project as it provides the anonymity, security and decentralization which makes HyperHire useful. The ledger consists of the world state that contains data that has been extracted from the PDF and the blockchain that contains the transactions made by the candidates and recruiters. The chaincode of the hyperledger allows the data marked as sensitive to be hidden when a query for the candidate's information is processed. Upon selection of the candidate, through a suitable transaction, the sensitive content becomes visible to the recruiter.

### Implementation
#### 1. Resume Parser
Built using CV2 and a custom classification library. The data on the PDF is sectionized while keeping spatial context. These sections are parsed using a custom classification library and the data is converted into key-value pairs of the form - <em>{key: [extracted text, coordinates of section]}</em>, for example - <em>{"name": "[Dhruv Sabharwal, (x1; x2; y1; y2)]"</em>. These key value pairs are then combined and converted into an asset (along with other data), that can be pushed onto the ledger. Certain key value pairs are marked as sensitive by the classification library and all such sensitive fields are combined and converted into a separate asset that will remain hidden to recruiters. On the recruiter side of the application, the coordinates and extracted text of the general data are used to recreate a pdf that is served to the recruiters.
<strong> Demonstration of the resume parser </strong> <br>
<img src="images/parser.png" alt="parser-image"> <br>
In the above example, the sensitiveInfo data field will comprise of a nested list containing all the sections that were determined to be sensitive:
<em>{[Name:Pranay Yadav,(54,58,588,104)], [Address:2 Nangloi Nazafgarh road Delhi 110041,(56,108,262,124)],[Mobile:+918743943900,(264,108,358,124)],[Email:pranay.yadav@outlook.com,(360,108,510,124)]}</em> <br>
(Note: Current proposal for sensitive data is Name, Gender, Email, Address, and Mobile Number) <br>
Similarly, the generalInfo field will contain a nested list of all non-sensitive data.

#### 2. The Chaincode
The chaincode uses the following global variables:
<ol>
  <li><b>candidates</b> : an array that stores <candidateID> of all registered candidates (Initially empty).
  <li><b>companies</b> : an array that stores <companyID> of all registered companies (Initially empty).
</ol>
An <b> asset (key, value)</b> is <b>(concernedIDs, appInfo)</b> where:
<b>concernedIDs</b> &#8658 (companyID, candidateID) : Composite key
<b>appInfo</b> &#8658 {generalInfo : List of key-value pairs as explained earlier, sensitiveInfo : List of key-value pairs as explained earlier, timestamp : UNIX time, accepted : 0 initially, 1 if accepted and 2 if rejected}





### Requirements
Ensure that Docker, docker-compose, Python3, Python3-dev are installed on your system <br>
Python Library Requirements: ast opencv-python pdf2image nltk tesserocr pillow imutils numpy flask flask-login utils

### Usage
Give execution permissions to start script. Run <code>./startHyperHire.sh</code> (script may take upto 5 minutes to finish, in case of errors re-run script).
