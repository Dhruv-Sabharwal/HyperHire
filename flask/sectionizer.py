import cv2
import sys
import imutils
import math
from tesserocr import PyTessBaseAPI, PSM, RIL
from PIL import Image, ImageDraw, ImageFont
import re
import nltk


#TO DO
#auto detect kernel mode
#confidence rating for more accurate column classification
#irregular columns
names = []
names_c = []
phone = []
phone_c = []
email = []
email_c = []
misc = []
misc_c = []
SCALE = 4
AREA_THRESHOLD = 1000
# def boundingBox(image_array, boxes):
#     for box in boxes:
#         box = box[1]
#         x, y, w, h = box['x'], box['y'], box['w'], box['h']
#         cv2.line(image_array, (x, y), (x + w, y), (255, 0, 0), 5)
#         cv2.line(image_array, (x, y), (x, y + h), (255, 0, 0), 5)
#         cv2.line(image_array, (x + w, y), (x + w, y + h), (255, 0, 0), 5)
#         cv2.line(image_array, (x, y + h), (x + w, y + h), (255, 0, 0), 5)
#     fig = plt.imshow(image_array)
#     plt.axis('off')
#     fig.axes.get_xaxis().set_visible(False)
#     fig.axes.get_yaxis().set_visible(False)
#     plt.show()

def show_scaled(name, img):
    try:
        h, w  = img.shape
    except ValueError:
        h, w, _  = img.shape
    cv2.imshow(name, cv2.resize(img, (w // SCALE, h // SCALE)))

def removeDuplicates():
    global names
    global names_c
    names_new = []
    for i in names:
        n = ''
        for j in i:
            n+=str(j)+' '
        names_new.append(n.strip())
    names = list(dict.fromkeys(names_new))
    if(len(names_c)>len(names)):
        names_c = names_c[0]

def main():
    #Loops through images in active folder
    for i in range(1):
        names.clear()
        names_c.clear()
        phone.clear()
        phone_c.clear()
        email.clear()
        email_c.clear()
        misc.clear()
        misc_c.clear()
        img = cv2.imread('./static/'+str(i)+'.jpg')
        img = cv2.resize(img, (2066,2924))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # show_scaled("original", gray) #popup of original image (debugging)
        thresholded = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                    11,
                    1
                )
        # show_scaled('thresholded', thresholded) #popup of adaptiveThreshold image (debugging)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13,3))
        closing = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)
        contours, hierarchy = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # show_scaled("closing", closing) #popup of morphed image (debugging)
        #imS = cv2.resize(img, (2066, 2924)) #Preprocessor converts to image of this resolution
        #show_scaled("contours", imS) #popup of contoured image (debugging)
        # cv2.imwrite("/tmp/contours.png", imS)
        # plt.imshow(img)
        # plt.show()
        # cv2.waitKey() #popup of contoured plot (debugging)
        contours.reverse()
        asset_general = []
        for c in contours:
            x,y,w,h = cv2.boundingRect(c)
            x-=1
            y-=1
            w+=1
            h+=1
            if(w*h>AREA_THRESHOLD):
                if(h<15):
                    continue
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
                crop_img = img[y:y+h, x:x+w]
                cv2.imwrite("temp.jpg",crop_img)
            else:
                continue
            #replace path with path to tessdata
            with PyTessBaseAPI(path='./tessdata/', lang='eng', psm=7) as api:
                found = False
                name_input = []
                img2 = 'temp.jpg'
                image = Image.open(img2)
                api.SetImageFile(img2)
                api.Recognize()
                temp = api.GetUTF8Text()
                p = re.findall(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*)',temp)
                e = re.findall(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)', temp)
                if(e):
                    email.append(temp.strip())
                    email_c.append([x,y,w,h])
                    found = True
                tagged_sent = nltk.tag.pos_tag(temp.split())
                propernouns = [word for word,pos in tagged_sent if pos == 'NN']
                propernouns2 = [word for word,pos in tagged_sent if pos == 'NNP']
                [x.lower() for x in propernouns]
                [x.lower() for x in propernouns2]
                if(propernouns):
                    if(len(propernouns)<=3):
                        name_input.append(propernouns)
                if(propernouns2):
                    if(len(propernouns2)<=3):
                        name_input.append(propernouns2)
                # tags = temp.split()
                # [x.lower() for x in tags]
                # [name_input.append(x) for x in tags]
                fo = open("names.txt", "r")
                names_data = fo.read()
                for name in name_input:
                    flag = 0
                    for n in name:
                        for i in names_data.split('\n'):
                            if n.lower() == i:
                                flag = 1
                        if(flag==1):
                            names.append(name)
                            names_c.append([x,y,w,h])
                            found = True
                            break
                boxes = api.GetComponentImages(RIL.TEXTLINE, True)
                if(p):
                    for j in p:
                        j.replace(' ','')
                        j.replace('(','')
                        j.replace(')','')
                        j.replace('/','')
                        j.replace('-','')
                        if(len(j)>=10):
                            phone.append(j)
                            phone_c.append([x,y,w,h])
                            found = True
                if found==False:
                    if(h<10):
                        continue
                    t = []
                    t.append(temp.strip())
                    t.append([x,y,w,h])
                    asset_general.append(t)
        removeDuplicates()
        # print(names)
        # print(names_c)
        # print(phone)
        # print(phone_c)
        # print(email)
        # print(email_c)
        asset_sensitive = []
        n = []
        n.append(names)
        n.append(names_c)
        p = []
        p.append(phone)
        p.append(phone_c)
        e = []
        e.append(email)
        e.append(email_c)
        asset_sensitive.append(n)
        asset_sensitive.append(p)
        asset_sensitive.append(e)
        print(asset_sensitive)
        print(asset_general)
        f = open("sensitive.txt", "w")
        f.write(str(asset_sensitive))
        f.close()
        f = open("general.txt", "w")
        f.write(str(asset_general))
        f.close()
        # imS = cv2.resize(img, (2066, 2924)) #Preprocessor converts to image of this resolution
        # show_scaled("contours", imS) #popup of columnized image (debugging)
        # plt.imshow(img)
        # plt.show()
        # cv2.waitKey()

if __name__ == '__main__':
    main()
