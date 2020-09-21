import getpass
import json
import os
import random
import string
import subprocess
from pdf2image import convert_from_path
import ast
import cv2
import imutils
import math
import numpy as  np
from PIL import Image, ImageDraw, ImageFont

import flask_login
from flask import Flask, request, redirect, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin

import utils
UPLOAD_FOLDER = './temp/'
app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
FABRIC_DIR = "./"
NODE_PATH = "node"
DEBUG = True
SEND_OTP = False
candidateId = ""
companyId = ""
loginCandidate = -1
loginCompany = -1

def logoutCompany():
    global loginCompany
    global companyId
    loginCompany = -1
    companyId = ""

def logoutCandidate():
    global loginCompany
    global companyId
    loginCompany = -1
    companyId = ""

def registerCompany(user):
    global loginCompany
    output = "dummya"

    try:
        output = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "registerCompany.js", user]).decode().split()
    except:
        pass

    if DEBUG:
        print(' '.join(output))

    if output != "dummy" and output[len(output) - 1] == "wallet":
        loginCompany = 2
        return 0
    else:
        return 1


def registerCandidate(user):
    global loginCandidate
    output = "dummya"

    try:
        output = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "registerCandidate.js", user]).decode().split()
    except:
        pass

    if DEBUG:
        print(' '.join(output))

    if output != "dummy" and output[len(output) - 1] == "wallet":
        loginCandidate = 2
        return 0
    else:
        return 1

@app.route('/upload', methods = ['POST'])
def success():
    if(loginCandidate==-1):
        return render_template("candidate.html", login = 0)
    if request.method == 'POST':
        f = request.files['myPdf']
        f.save('./temp/'+f.filename)
        path = './temp/'+f.filename
        doc = convert_from_path(path,500)
        doc[0].save('./static/0.jpg', 'JPEG')
        return render_template("candidate.html", uploaded = 1, result = loginCandidate, uid = candidateId)

@app.route('/applyJob', methods = ['POST'])
def parse():
    output = "nah"
    try:
        output = subprocess.check_output(
            ["python3", FABRIC_DIR + "sectionizer.py"])
    except:
        pass
    cid = request.form.get('companyId')
    try:
        output = subprocess.check_output(
            ["node", FABRIC_DIR + "invoke", "applyJob", cid, candidateId]).decode().split()
    except:
        pass
    if output[len(output) - 1] == "submitted":
        return render_template("candidate.html", uploaded = 2, result = loginCandidate, uid = candidateId)
    else:
        return render_template("candidate.html", uploaded = -1, result = loginCandidate, uid = candidateId)

@app.route('/candidate')
def candidate():
    return render_template('candidate.html', result = loginCandidate, uid = candidateId)

@app.route('/register_candidate', methods=['POST'])
def register_candidate():
    global candidateId
    uid = request.form.get('candidate_uid')
    registerCandidate(uid)
    candidateId = uid
    return render_template("candidate.html",result = 0, uid = uid)

@app.route('/logoutCompany')
def logoutCompany():
    global loginCompany
    global companyId
    loginCompany = -1
    companyId = ""
    return render_template("company.html")

@app.route('/logoutCandidate')
def logoutCandidate():
    global loginCompany
    global companyId
    loginCompany = -1
    companyId = ""
    return render_template("candidate.html")
#functions to handle company side

@app.route('/register_company', methods=['POST'])
def register_company():
    global companyId
    uid = request.form.get('company_uid')
    registerCompany(uid)
    companyId = uid
    return render_template("company.html",result = 0, uid = uid, query = 0)

def font_size(text, w, h):
    i=0.1
    (t_w, t_h), baseline = cv2.getTextSize(text, 2, i , 2)
    while(t_w*t_h<w*h and t_w<w):
        i+=0.01
        (t_w, t_h), baseline = cv2.getTextSize(text, 2, i , 2)
    return(i-0.01)

def create(asset):
    img = 255 * np.ones((2924,2066,3), np.uint8)
    font = 2
    color = (0,0,0)
    thickness = 2
    for l1 in asset:
        text = l1[0]
        org = l1[1][0:2]
        area = l1[1][2:4]
        if not area:
            continue
        font_scale = font_size(text, area[0], area[1]) #w,h
        org = tuple(org)
        img = cv2.putText(img, text, org, font, font_scale, color, thickness, cv2.LINE_AA)
    return img

def recreate(output):
    output = output[output.find('['):-8]
    asset = ast.literal_eval(output)
    if(type(asset) is dict):
        general = ast.literal_eval(asset.get('generalInfo'))
        if(asset.get('accepted')==1):
            temp = ast.literal_eval(asset.get('sensitiveInfo'))
            for t in temp:
                if not t[1]:
                    continue
                for i in range(len(t[0])):
                    l = []
                    l.append(t[0][i])
                    l.append(t[1][i])
                    general.append(l)
        img = create(general)
        cv2.imwrite("./static/r1.jpg", img)
    else:
        if(len(asset)>0):
            i=1
            for a in asset:
                general = ast.literal_eval(a.get('appInfo').get('generalInfo'))
                if(a.get('appInfo').get('accepted')==1):
                    temp = ast.literal_eval(a.get('appInfo').get('sensitiveInfo'))
                    for t in temp:
                        if not t[1]:
                            continue
                        for k in range(len(t[0])):
                            l = []
                            l.append(t[0][k])
                            l.append(t[1][k])
                            general.append(l)
                img = create(general)
                cv2.imwrite("./static/r"+str(i)+".jpg", img)
                i+=1

def statusArr(output):
    output = output[output.find('['):-8]
    output = ast.literal_eval(output)
    status = []
    if(len(output)>0):
        for a in output:
            status.append(a.get('appInfo').get('accepted'))
    return status

def candidateArr(output):
    output = output[output.find('['):-8]
    output = ast.literal_eval(output)
    status = []
    if(len(output)>0):
        for a in output:
            status.append(a.get('Key').get('attributes')[1])
    return status

@app.route('/queryAll')
def query_all():
    if(loginCompany==-1):
        return render_template("company.html", login = 0)
    output = "nah"
    try:
        output = subprocess.check_output(
            ["node", FABRIC_DIR + "query", "queryAllCandidates", companyId]).decode()
    except:
        pass
    output_arr = output.split()
    status = statusArr(output)
    candidates = candidateArr(output)
    res = {candidates[i]: status[i] for i in range(len(candidates))}
    recreate(output)
    if output_arr[len(output_arr) - 1] == "success":
        return render_template("company.html", result = loginCompany, uid = companyId, query = 1, candidates = res)
    else:
        return render_template("company.html", result = loginCompany, uid = companyId, query = -1)

@app.route('/query_candidate', methods = ['POST'])
def query_candidate():
    if(loginCompany==-1):
        return render_template("company.html", login = 0)
    output = "nah"
    cid = request.form.get('candidateId')
    try:
        output = subprocess.check_output(
            ["node", FABRIC_DIR + "query", "queryCandidate", companyId, cid]).decode()
    except:
        pass
    output_arr = output.split()
    if output_arr[len(output_arr) - 1] == "success":
            output = output[output.find('{'):-8]
            asset = ast.literal_eval(output)
            res = {cid:asset.get('accepted')}
            return render_template("company.html", result = loginCompany, uid = companyId, query = 1, candidates = res)
    else:
        return render_template("company.html", result = loginCompany, uid = companyId, query = -1)

@app.route('/')
def company():
    return render_template('company.html', result = loginCompany, uid = companyId, query = 0)

@app.route('/callAccept/<string:uid>')
def callAccept(uid):
    try:
        output = subprocess.check_output(
            ["node", FABRIC_DIR + "invoke", "acceptCandidate", companyId, uid]).decode().split()
    except:
        pass
    if output[len(output) - 1] == "submitted":
        return render_template('company.html', result = loginCompany, uid = companyId, query = 0, success = 1)
    else:
        return render_template('company.html', result = loginCompany, uid = companyId, query = 0, success = 0)

@app.route('/callReject/<string:uid>')
def callReject(uid):
    try:
        output = subprocess.check_output(
            ["node", FABRIC_DIR + "invoke", "rejectCandidate", companyId, uid]).decode().split()
    except:
        pass
    if output[len(output) - 1] == "submitted":
        return render_template('company.html', result = loginCompany, uid = companyId, query = 0, success = 2)
    else:
        return render_template('company.html', result = loginCompany, uid = companyId, query = 0, success = 0)

if __name__ == '__main__':
    company()
