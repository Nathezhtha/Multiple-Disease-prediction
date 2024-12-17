import csv
import os
import random
import shutil
import time

import sample_data
import voice
from PIL import ImageTk, Image, ImageFilter
# from cgitb import reset
from datetime import date, timedelta
import re
from difflib import SequenceMatcher
from random import randint, randrange
import uuid
from datetime import datetime
from urllib import request
import cv2
from cnn_mlp import MLP
import numpy as np
from numpy import asarray
import pymysql
from werkzeug.utils import secure_filename, redirect
import socket
import ar_master
from flask import Flask, render_template, request, session, Response, current_app, send_from_directory, url_for
dd = voice.voice_call()
app = Flask(__name__, static_folder='static',template_folder='templates',static_url_path='/static')
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
mm = ar_master.master_flask_code('python_multi_disease_prediction')
@app.route("/")
def homepage():
    return render_template('index.html')
@app.route("/admin")
def admin():
    return render_template('admin.html')
@app.route("/user")
def user():
    return render_template('user.html')
@app.route("/user_login",methods = ['GET', 'POST'])
def user_login():
    msg=None
    if request.method == 'POST':
        n = request.form['username']
        g = request.form['password']
        n1=str(n)
        g1=str(g)
        q=("SELECT * from user_details where name='" + str(n1) + "' and password='" + str(g) + "'")
        data=mm.select_direct_query(q)
        data=len(data)
        if data==0:
            return render_template('user.html',flash_message=True,data="Failed")
        else:
            msg='Success'
            session['user'] =n
            return render_template('user_home.html',sid=n)
    return render_template('user.html',error=msg)
@app.route("/user_home")
def user_home():
    return render_template('user_home.html')
@app.route("/user_register", methods=['GET', 'POST'])
def user_register():
    return render_template('user_register.html')
@app.route("/user_register1",methods = ['GET', 'POST'])
def user_register1():
    if request.method == 'POST':
        name = request.form['applicant_name']
        contact = request.form['contact']
        email = request.form['email']
        address = request.form['address']
        dob = request.form['dob']
        password = request.form['password']
        maxid = mm.find_max_id("user_details")
        qry=("insert into user_details values('" + str(maxid) + "','" + name + "','" + contact + "','" + email + "','" + address + "','" + dob + "','" + password + "','0','0')")
        result=mm.insert_query(qry)
        if (result == 1):
            return render_template('user.html')
        else:
            return render_template('user_register.html')
@app.route("/admin_login", methods = ['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['pass'] == 'admin':
            return render_template('admin_home.html',flash_message=True,data="Success")
        else:
            return render_template('admin.html', error=error)
@app.route("/admin_home")
def admin_home():
    return render_template('admin_home.html')
def write_dataset(query,answer):
    file ='training-dataset.py'
    pr_chk=0
    with open(file) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            t1 = row['query']
            if t1==query:
                pr_chk+=1
    if pr_chk==0:
        file1 = 'training-dataset1.csv'
        with open(file) as f, open('training-dataset1.csv', 'w', encoding='utf-8', newline='')as csvfile:
            reader = csv.DictReader(f, delimiter=',')
            filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(
                ['query', 'answer'])
            for row in reader:
                t1 = row['query']
                t2 = row['answer']
                filewriter.writerow([t1, t2])
            filewriter.writerow([query, answer])
        shutil.copy('training-dataset1.csv', file)
        os.remove(file1)
        return "success"
    else:
        return "Already Trained"
@app.route("/admin_train_query", methods=['GET', 'POST'])
def admin_train_query():
    if request.method == 'POST':
        query = request.form['query']
        answer = request.form['answer']
        msg=write_dataset(query=query,answer=answer)
        return render_template('admin_train_query.html',data=msg)
    return render_template('admin_train_query.html')
def roi():
    image = cv2.imread('data\\morphological.png')
    original = image.copy()
    blank = np.zeros(image.shape[:2], dtype=np.uint8)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (127, 127), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = max(contours, key=lambda x: cv2.contourArea(x))
    cv2.drawContours(image, [contours], -1, (255, 255, 0), 1)
    ar_read = 0
    ar_x = []
    ar_y = []
    hull = cv2.convexHull(contours, returnPoints=False)
    defects = cv2.convexityDefects(contours, hull)
    flag = not np.any(defects)
    if flag == False:
        for i in range(defects.shape[0]):
            _, _, farthest_point_index, distance = defects[i, 0]
            farthest_point = contours[farthest_point_index][0]
            if distance > 50_000:
                ar_x.append(farthest_point[0])
                ar_y.append(farthest_point[1])
                (x, y), (MA, ma), ellipse_angle = cv2.fitEllipse(contours)
                x1 = int((int(x) + int(MA) * np.sin(ellipse_angle * np.pi / 180.0)))
                y1 = int((int(y) - int(MA) * np.cos(ellipse_angle * np.pi / 180.0)))
                x2 = int((int(x) - int(MA) * np.sin(ellipse_angle * np.pi / 180.0)))
                y2 = int((int(y) + int(MA) * np.cos(ellipse_angle * np.pi / 180.0)))
                color = (255, 0, 0)
            else:
                sample_data.student.bpnn -= 1
    # plt.imsave('Detected.png', image)
def find_feature_value(file_path):
    img = Image.open(file_path).convert('L')
    img.save('data/greyscale.png')
    ################################
    im1 = Image.open(r"data/greyscale.png")
    im2 = im1.filter(ImageFilter.MedianFilter(size=3))
    im2.save('data/dct.png')
    ################################################
    image = cv2.imread('data/dct.png')
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(image, -1, kernel)
    cv2.imwrite('data/sharpened.png', sharpened)
    ############################################################
    src = cv2.imread("data\\dct.png", 1)
    img = src
    s = 128
    img = cv2.resize(img, (s, s), 0, 0, cv2.INTER_AREA)
    def apply_watershed_segment(input_img, brightness=0, contrast=0):
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow
            buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
        else:
            buf = input_img.copy()
        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)
            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)
        return buf
    font = cv2.FONT_HERSHEY_SIMPLEX
    fcolor = (0, 0, 0)
    blist = [0]
    clist = [64]
    out = np.zeros((s * 2, s * 3, 3), dtype=np.uint8)
    for i, b in enumerate(blist):
        c = clist[i]
        out = apply_watershed_segment(img, b, c)
    cv2.imwrite('data/watershed.png', out)
    #####################################################
    image = Image.open(r"data/watershed.png")
    image = image.convert("L")
    image = image.filter(ImageFilter.FIND_EDGES)
    image.save(r"data/morphological.png")
    ################################################
    img = cv2.imread('data\\morphological.png', 0)
    numpydata = asarray(img)
    z = []
    for x in numpydata:
        for y in x:
            z.append(int(y))
    nn = MLP([2, 2, 1])
    nn.glcm_extract(z)
    sample_data.student.bpnn = nn.result()
    roi()
    return sample_data.student.bpnn
@app.route("/admin_train_image", methods=['GET', 'POST'])
def admin_train_image():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join("static/uploads/", secure_filename(f.filename)))
        value=find_feature_value(os.path.join("static/uploads/", secure_filename(f.filename)))
        answer = request.form['answer']
        msg=write_dataset(query=value,answer=answer)
        return render_template('admin_train_image.html',data=msg)
    return render_template('admin_train_image.html')
@app.route("/user_query", methods=['GET', 'POST'])
def user_query():

    if request.method == 'POST':
        type = request.form['type']
        print(type)
        if type=="Text":
            return redirect(url_for("query_text"))
        elif type=="Voice":
            return redirect(url_for("query_voice"))
        elif type=="Image":
            return redirect(url_for("query_image"))

    return render_template('user_query.html')


def  get_result(qry):
    file1 = 'training-dataset.csv'
    with open(file1) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            t1 = str(row['query']).lower()
            t2 = row['answer']
            if t1==str(qry).lower():
                return t2
            else:
                # print(str(t1).lower(), str(qry).lower())
                t1=str(t1).lower()
                qry=str(qry).lower()
                dd = find_overlap(t1, qry)
                # print(dd)
                if dd:
                    return t2
                elif qry in t1:
                    return t2
    return "Not Found"
def find_overlap(s1, s2):
    for i in range(len(s1)):
        test1, test2 = s1[i:], s2[:len(s1) - i]
        if test1 == test2:
            return test1
def  get_result1(qry):
    file1 = 'training-dataset.csv'
    with open(file1) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            t1 = row['query']
            t2 = row['answer']
            if str(t1)==str(qry):
                return t2
            else:
                dd = find_overlap(str(t1).lower(), str(qry).lower())
                if dd:
                    return t2
                elif str(qry) in str(t1):
                    return t2

    return "Not Found"

@app.route("/query_text", methods=['GET', 'POST'])
def query_text():
    if request.method == 'POST':
        result_dict={}
        i=0
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        query = request.form['query']

        qry="select * from disease_details"

        full_data=mm.select_direct_query(qry)
        filter_data=[]
        # print(full_data)
        for x in full_data:
            d_l1=x[6]
            d_l2=x[7]
            disease=x[2]
            # print(disease,query)
            if disease in query:
                filter_data.append(x)
                dist=mm.haversine_distance(latitude,longitude,d_l1,d_l2)
                pp=list(x)
                pp.append(dist)
                result_dict[dist]=pp
                i+=1
                break
        sorted_dict = dict(sorted(result_dict.items()))
        values_list = list(sorted_dict.values())
        # print(values_list)

        result=get_result(query)
        return render_template('query_text.html',query=query,result=result,values_list=values_list)
    return render_template('query_text.html')




@app.route("/query_voice", methods=['GET', 'POST'])
def query_voice():
    if request.method == 'POST':

        result_dict = {}
        i = 0
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        query = request.form['query']

        qry = "select * from disease_details"

        full_data = mm.select_direct_query(qry)
        filter_data = []
        for x in full_data:
            d_l1 = x[6]
            d_l2 = x[7]
            disease = x[2]
            if disease in query:
                filter_data.append(x)
                dist = mm.haversine_distance(latitude, longitude, d_l1, d_l2)
                pp = list(x)
                pp.append(dist)
                result_dict[dist] = pp
                i += 1
        sorted_dict = dict(sorted(result_dict.items()))
        values_list = list(sorted_dict.values())
        print(values_list)
        result=get_result(query)
        dur=len(result)/8

        la = 'en'
        dd = voice.voice_call()
        dd.speak(str(result), la)

        dd.play_sound()
        time.sleep(dur)
        dd.delete_file()
        return render_template('query_voice.html',query=query,result=result,values_list=values_list)

    return render_template('query_voice.html')

@app.route("/query_image", methods=['GET', 'POST'])
def query_image():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join("static/uploads/", secure_filename(f.filename)))
        value = find_feature_value(os.path.join("static/uploads/", secure_filename(f.filename)))
        print(value)
        result = get_result1(value)
        print(result)
        result_dict = {}
        i = 0
        latitude = request.form['latitude']
        longitude = request.form['longitude']


        qry = "select * from disease_details"

        full_data = mm.select_direct_query(qry)
        filter_data = []
        for x in full_data:
            d_l1 = x[6]
            d_l2 = x[7]
            disease = x[2]
            print(disease)
            if disease in result:
                filter_data.append(x)
                dist = mm.haversine_distance(latitude, longitude, d_l1, d_l2)
                pp = list(x)
                pp.append(dist)
                result_dict[dist] = pp
                i += 1
        sorted_dict = dict(sorted(result_dict.items()))
        values_list = list(sorted_dict.values())
        print(values_list)

        return render_template('query_image.html',result=result,values_list=values_list)
    return render_template('query_image.html')

@app.route("/doctor")
def doctor():
    return render_template('doctor.html')
@app.route("/doctor_login",methods = ['GET', 'POST'])
def doctor_login():
    msg=None
    if request.method == 'POST':
        n = request.form['username']
        g = request.form['password']
        n1=str(n)
        g1=str(g)
        q=("SELECT * from doctor_details where name='" + str(n1) + "' and password='" + str(g) + "'")
        data=mm.select_direct_query(q)
        data=len(data)
        if data==0:
            return render_template('doctor.html',flash_message=True,data="Failed")
        else:
            msg='Success'
            session['doctor'] =n
            return render_template('doctor_home.html',sid=n)
    return render_template('user.html',error=msg)


@app.route("/doctor_home")
def doctor_home():
    return render_template('doctor_home.html')

@app.route("/doctor_train_data",methods = ['GET', 'POST'])
def doctor_train_data():
    doctor=session['doctor']
    if request.method == 'POST':
        disease = request.form['disease']
        fees = request.form['fees']
        duration = request.form['duration']
        location = request.form['location']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        maxid = mm.find_max_id("disease_details")
        qry = ("insert into disease_details values('" + str(maxid) + "','" + doctor + "','" + disease + "','" + fees + "','" + duration + "','" + location + "','" + latitude + "','" + longitude + "','0','0')")
        result = mm.insert_query(qry)
        if (result == 1):
            return render_template('doctor_train_data.html',msg="Success")
        else:
            return render_template('doctor_train_data.html')
    return render_template('doctor_train_data.html')


@app.route("/doctor_register", methods=['GET', 'POST'])
def doctor_register():
    return render_template('doctor_register.html')
@app.route("/doctor_register1",methods = ['GET', 'POST'])
def doctor_register1():
    if request.method == 'POST':
        name = request.form['name']
        qualification = request.form['qualification']
        age = request.form['age']
        specialization = request.form['specialization']
        experiance = request.form['experiance']

        address = request.form['address']
        mail = request.form['mail']
        password = request.form['password']

        maxid = mm.find_max_id("doctor_details")
        qry=("insert into doctor_details values('" + str(maxid) + "','" + str(name) + "','" + str(qualification) + "','" + str(age) + "','" + str(specialization) + "','" + str(experiance) + "','" + str(address) + "','" + str(mail) + "','" + str(password) + "','0','0')")
        result=mm.insert_query(qry)
        if (result == 1):
            return render_template('doctor.html')
        else:
            return render_template('user_register.html')




@app.route("/doctor_chat_first", methods=['GET', 'POST'])
def doctor_chat_first():
    doctor=session['doctor']
    data=mm.select_direct_query("select distinct user  from chat where doctor='"+str(doctor)+"'")
    print(data)
    return render_template('doctor_chat_first.html',items=data)




@app.route("/doctor_chat/<user>", methods=['GET', 'POST'])
def doctor_chat(user):
    session['user']=user
    return redirect(url_for("doctor_chat1"))

@app.route("/doctor_chat1", methods=['GET', 'POST'])
def doctor_chat1():
    doctor=session['doctor']
    user=session['user']

    if request.method == 'POST':
        message = request.form['message']
        mm.insert_query("insert into chat values('"+str(user)+"','"+str(doctor)+"','"+str(message)+"','"+str(doctor)+"')")
    data = mm.select_direct_query("select * from chat where user='" + str(user) + "' and doctor='" + str(doctor) + "'")
    return render_template('doctor_chat1.html',user=user,doctor=doctor,data=data)



@app.route("/user_chat_first", methods=['GET', 'POST'])
def user_chat_first():
    user=session['user']
    data=mm.select_direct_query("select distinct doctor from chat where user='"+str(user)+"'")
    print(data)
    return render_template('user_chat_first.html',items=data)


@app.route("/user_chat/<doctor>", methods=['GET', 'POST'])
def user_chat(doctor):
    session['doctor']=doctor
    return redirect(url_for("user_chat1"))

@app.route("/user_chat1", methods=['GET', 'POST'])
def user_chat1():
    doctor=session['doctor']
    user=session['user']
    data=mm.select_direct_query("select * from chat where user='"+str(user)+"' and doctor='"+str(doctor)+"'")
    if request.method == 'POST':
        message = request.form['message']
        mm.insert_query("insert into chat values('"+str(user)+"','"+str(doctor)+"','"+str(message)+"','"+str(user)+"')")
    return render_template('user_chat1.html',user=user,doctor=doctor,data=data)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

