# HyperHire
HyperHire is a hiring portal built on the Hyperledger fabric using a flask web application. It allows candidates to upload their resumes in a PDF format to HyperHire. Data is then extracted from the resumes and pushed onto the Hyperledger. The extracted data is divided into 2 parts:
<ol>
<li> Sensitive content - Name, Age, Sex, etc.
<li> General content - Skills, Work Experience, Extra-Curriculars etc.
</ol>







### Requirements
Ensure that Docker, docker-compose, Python3, Python3-dev are installed on your system
Python Library Requirements: ast opencv-python pdf2image nltk tesserocr pillow imutils numpy flask flask-login utils

### Usage
Give execution permissions to start script. Run ./startHyperHire.sh (script may take upto 5 minutes to finish, in case of errors re-run script).
