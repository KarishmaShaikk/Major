import pyrebase
from collections import OrderedDict
from flask import jsonify
import requests
#import pandas as pd
from flask import *
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from flask import Flask, request, render_template, redirect, url_for, flash
import pyrebase
import os
from werkzeug.utils import secure_filename
#from sklearn.metrics.pairwise import linear_kernel
#from django.shortcuts import render
#from PIL import Image
#import re
import random
from string import ascii_uppercase
from flask_socketio import join_room, leave_room, send, SocketIO, rooms
from flask import Flask, render_template, session , redirect, request ,url_for
from openai import OpenAI
client = OpenAI()
config = {
  "apiKey": "AIzaSyAg2Q-Td8JBGcjr3YX7f1KsOujBMRanF5c",
  "authDomain": "innovationhub-ec820.firebaseapp.com",
  "databaseURL": "https://innovationhub-ec820-default-rtdb.firebaseio.com",
  "projectId": "innovationhub-ec820",
  "storageBucket": "innovationhub-ec820.appspot.com",
  "messagingSenderId": "965727480908",
  "appId": "1:965727480908:web:200a990ef103906d5ed8e9",
  "measurementId": "G-J5Y0ZVJ6SY"
}
firebase = pyrebase.initialize_app(config)
auth=firebase.auth()
storage = firebase.storage()
db = firebase.database()
#person = {type:False}
app = Flask(__name__) # initialize
app.secret_key='_5#y2L"F4Q8z\n\xec]/'
person = {"type":False}
# TF-IDF Vectorization
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
tfidf = TfidfVectorizer(stop_words='english')
socketio = SocketIO(app)
rooms={}
def generate_unique_code(length):
  while True:
    code = ""
    for _ in range(length):
      code += random.choice(ascii_uppercase)
    if code not in rooms:
      break
  return code
@app.route('/', methods=['GET'])
def choose():
  return render_template('Welcome.html')
@app.route('/Entresult', methods=["POST","GET"])
def eresult():
  if request.method == "POST":
    email = request.form['email']
    password = request.form['password']
    try:
      user = auth.sign_in_with_email_and_password(email,password)
      person["id"] = user["localId"]
      person["type"] = "Entrepreneur"
      data = db.child("InnovationHub").child("Users").child("EntReg").get().val()
      entuser = data[person["id"]]
      person['name']=entuser['firstname']+" "+entuser['lastname']
      person['budget']=entuser['budget']
      person['contact']=entuser['mobileNumber']
      person['email'] = entuser['email']
      person['age']=entuser['age']
      person['budget']=entuser['budget']
      person['address']=entuser['address']
      person['probStmt']=entuser['problemStatement']
      person['website']=entuser['companyWebsite']
      print(entuser)
    except:
      flash('please use valid credentials', 'danger')
      return redirect(url_for('elogin'))
    return redirect(url_for('enthome'))
@app.route('/Invresult', methods=["POST", "GET"])
def iresult():
  if request.method == "POST":
    email = request.form['email']
    password = request.form['password']
    try:
      user = auth.sign_in_with_email_and_password(email, password)
      person["id"]=user["localId"]
      person["type"]="Investor"
      data=db.child("InnovationHub").child("Users").child("InvReg").get().val()#whole investors data
      invuser=data[person["id"]]#current user
      person['name'] = invuser['firstname'] + " " + invuser['lastname']
      person['contact'] = invuser['mobileNumber']
      person['email'] = invuser['email']
      person['age'] = invuser['age']
      person['budget'] = invuser['budget']
      person['address'] = invuser['address']
      #person['website'] = invuser['companyWebsite']
      print(invuser)
      for i in invuser:
        person[i]=invuser[i]
      #print(person)
    except Exception as e:
      print("Exception occured!!")
      print(e)
      flash('please use valid credentials', 'danger')
      return redirect(url_for('ilogin'))
    return (redirect(url_for('ihome')))
@app.route('/Leancan', methods=["POST","GET"])
def leancanvas():
    # Assuming you've retrieved the Lean Canvas data from the database
    #person["type"]="Entrepreneur"
    entuser = db.child("InnovationHub").child("Users").child("EntReg").child("LocalId").get().val()
    #print(entuser)
    #print(entuser["age"])
    #print(entuser)

    #print(ent_id)


    lean_data = entuser.get("lean", {})  # Retrieve the lean data stored in the database
    print(lean_data)

    return render_template('leancanvas.html', lean_data=lean_data)



@app.route('/genrate',methods=["POST", "GET"])
def genrate():
  resdata = db.child("InnovationHub").child("Users").child("EntReg").child(person["id"]).get().val()
  problemStatement = resdata["problemStatement"]
  print(resdata)
  response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={"type": "json_object"},
    messages=[
      {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
      {"role": "user",
       "content": "Generate lean canvas model consisting of the problemstatement,solution,key metrics,unique value proposition,Unfair Advantage,Channels,Customer Segments,Cost Structure,Revenue stremas as fields " + problemStatement + "with the following information {'ProblemStatement': '', 'Solution': '', 'KeyMetrics': [], 'UniqueValueProposition': [], 'UnfairAdvantage': [], 'Channels': [], 'CustomerSegments': [], 'CostStructure': [], 'RevenueStreams': []}"}
    ]
  )
  chatres = (response.choices[0].message.content)
  res = json.loads(chatres)
  #print(res)
  return render_template('lean1.html',chatres=res)
@app.route("/post",methods=['POST'])
def post():
  if request.method=='POST':
    #print(request.form)
    lean = request.form['jsonData']
    #print(lean)
    lean = lean.replace("&#39;","")
    print(lean)
    resdata = db.child("InnovationHub").child("Users").child("EntReg").child(str(person["id"]))
    data = {"lean":lean}
    resdata.update(data)
  return redirect(url_for('enthome'))
@app.route('/Login', methods=["POST","GET"])
def login():
  return render_template('Login.html')
@app.route('/EntLogin', methods=["POST","GET"])
def elogin():
  return render_template('EntLogin.html')
@app.route('/InvLogin', methods=["POST","GET"])
def ilogin():
  return render_template('InvLogin.html')
@app.route('/Register')
def register():
  return render_template('Register.html')
def render(request, param, param1):
  pass

@app.route('/EntHome')
def enthome():
  investor_data = db.child("InnovationHub").child("Users").child("InvReg").get().val()
  ent_data = db.child("InnovationHub").child("Users").child("EntReg").get().val()
  # Fetch profile image URL for the current entrepreneur
  #user_id = person["id"]
  #user_type = "EntReg"
  image_url = db.child('InnovationHub').child('Users').child("EntReg").child("LocalId").child('image_url').get().val()
  # Pass investor data and profile image URL to the template
  return render_template('EntHome.html', investors=investor_data, person=person, file_url=image_url)
@app.route("/chatei", methods=["POST", "GET"])
def home():
  session.clear()
  if request.method == "POST":
    name = request.form.get("name")
    code = request.form.get("code")
    join = request.form.get("join", False)
    create = request.form.get("create", False)
    if not name:
      return render_template("home.html", error="Please enter a name.", code=code, name=name)
    if join != False and not code:
      return render_template("home.html", error="Please enter a room code.", code=code, name=name)
    room = code
    if create != False:
      room = generate_unique_code(4)
      rooms[room] = {"members": 0, "messages": []}
    elif code not in rooms:
      return render_template("home.html", error="Room does not exist.", code=code, name=name)
    session["room"] = room
    session["name"] = name
    return redirect(url_for("room"))
  return render_template("home.html")
@app.route("/room")
def room():
  room = session.get("room")
  if room is None or session.get("name") is None or room not in rooms:
    return redirect(url_for("home"))
  return render_template("room.html", code=room, messages=rooms[room]["messages"])
@socketio.on("message")
def message(data):
  room = session.get("room")
  if room not in rooms:
    return
  content = {
    "name": session.get("name"),
    "message": data["data"]
  }
  send(content, to=room)
  rooms[room]["messages"].append(content)
  print(f"{session.get('name')} said: {data['data']}")
@socketio.on("connect")
def connect(auth):
  room = session.get("room")
  name = session.get("name")
  if not room or not name:
    return
  if room not in rooms:
    leave_room(room)
    return
  join_room(room)
  send({"name": name, "message": "has entered the room"}, to=room)
  rooms[room]["members"] += 1
  print(f"{name} joined room {room}")
@socketio.on("disconnect")
def disconnect():
  room = session.get("room")
  name = session.get("name")
  leave_room(room)
  if room in rooms:
    rooms[room]["members"] -= 1
    if rooms[room]["members"] <= 0:
      del rooms[room]
  send({"name": name, "message": "has left the room"}, to=room)
  print(f"{name} has left the room {room}")
@app.route('/InvHome')
def ihome():
  investor_data = db.child("InnovationHub").child("Users").child("InvReg").get().val()
  user_id = person["id"]
  image_url = storage.child("images/" + person['id']).get_url(None)
  #person["type"] = "Entrepreneur"
  #person['name'] = investor_data ['firstname'] + " " + investor_data ['lastname']
  ent_data=db.child("InnovationHub").child("Users").child("EntReg").get().val()
  filtered_data = OrderedDict()
  print(ent_data)
  for i in ent_data:
    print(i)
    if "lean" in ent_data[i] :
      filtered_data[i] = (ent_data[i])
  #filtered_data = json.dumps(filtered_data)
  print(filtered_data)
  return render_template( 'InvHome.html',entrepreneurs=ent_data,person=person,image_url=image_url)
@app.route('/EntReg',methods=['GET','POST'])
def ent_registration():
  return render_template('EntReg.html')
@app.route('/InvReg', methods=['GET', 'POST'])
def inv_registration():
  #if request.method == 'POST':
    # Call InvReg function to handle investor registration
    #return InvReg()
  return render_template('InvReg.html')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
  return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=['POST'])
def upload():
  #user=db.child('InnovationHub').child('Users').child("EntReg").child("LocalId").get().val()
  #person["id"] = user["localId"]
  person["type"] = "Entrepreneur"
  data = db.child("InnovationHub").child("Users").child("EntReg").get().val()
  entuser = data[person["id"]]
  person['name'] = entuser['firstname'] + " " + entuser['lastname']
  person['budget'] = entuser['budget']
  person['contact'] = entuser['mobileNumber']
  person['email'] = entuser['email']
  person['age'] = entuser['age']
  person['budget'] = entuser['budget']
  person['address'] = entuser['address']
  person['probStmt'] = entuser['problemStatement']
  person['website'] = entuser['companyWebsite']
  if 'file' not in request.files:
    return redirect(request.url)
  #file = request.files['file']
  file = request.files['file']
  filename = file.filename
  if filename == '':
    flash('No image selected')
    return redirect(request.url)
  if file:
    storage.child("images/" + person['id']).put(file)
    print("ID------------------------------------------------")
    print(person['id'])
    url = storage.child("images/" + person['id']).get_url(None)
    print("Original Url-------------------------------------------------------------------")
    print(url)
    person['image_url'] = url
    f = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('EProfile.html',person=person, fname=url)
  else:
    return render_template('EProfile.html',person=person)
@app.route('/get_image_url', methods=['POST'])
def get_image_url():
  # Retrieve the entrepreneur ID from the POST request
  user=db.child('InnovationHub').child('Users').child("EntReg").child("LocalId").get().val()
  ent_id = request.form['ent_id']
  # Assuming entrepreneurs is a dictionary containing entrepreneur information with image URLs
  image_url = user[ent_id]['image_url']
  # Return the image URL as JSON
  return {'image_url': image_url}
@app.route('/delete_image', methods=['POST'])
def delete_image():
  image_url = request.form.get('image_url')
  # Delete the image from the storage or perform necessary action
  # Example: storage.child("images/" + person['id']).delete()
  # Clear the image URL from the 'person' dictionary
  person['image_url'] = None
  # Redirect back to the profile page
  return redirect('/Eprofile')
@app.route('/Eprofile',methods=['GET','POST'])
def eprofile():
  #entdata=db.child("InnovationHub").child("Users").child("EntReg").get().val()
  return render_template('EProfile.html',person=person)
@app.route('/Posts')
def posts():
  return render_template('Posts.html')
@app.route('/Iprofile',methods=['GET','POST'])
def iprofile():
  return render_template('IProfile.html')
@app.route('/iLean',methods=['GET','POST'])
def lean():
  resdata = db.child("InnovationHub").child("Users").child("EntReg").child(str(person["id"])).get().val()
  problemStatement = resdata["problemStatement"]
  print(resdata)
  response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={"type": "json_object"},
    messages=[
      {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
      {"role": "user",
       "content": "Generate lean canvas model consisting of the problemstatement,solution,key metrics,unique value proposition,Unfair Advantage,Channels,Customer Segments,Cost Structure,Revenue stremas as fields " + problemStatement + "with the following information {'ProblemStatement': '', 'Solution': '', 'KeyMetrics': [], 'UniqueValueProposition': [], 'UnfairAdvantage': [], 'Channels': [], 'CustomerSegments': [], 'CostStructure': [], 'RevenueStreams': []}"}
    ]
  )
  chatres = (response.choices[0].message.content)
  res = json.loads(chatres)
  # print(res)
  return render_template('Leancanvas.html',chatres=res)
@app.route('/DataEntry', methods=['POST'])
def EntReg():
  firstname = request.form['firstname']
  lastname = request.form['lastname']
  email = request.form['email']
  password = request.form['password']
  mobileNumber = request.form['mobileNumber']
  address = request.form['address']
  age = request.form['age']
  problemStatement = request.form['problemStatement']
  companyWebsite = request.form['companyWebsite']
  budget= request.form['budget']
  try :
    auth.create_user_with_email_and_password(email,password)
    user = auth.sign_in_with_email_and_password(email,password)
    print("anand")
    db.child("InnovationHub").child("Users").child("EntReg").child(user["localId"]).set({
      "firstname": firstname,
      "lastname": lastname,
      "email": email,
      "mobileNumber": mobileNumber,
      "address": address,
      "age": age,
      "problemStatement": problemStatement,
      "companyWebsite": companyWebsite,
      "budget": budget
    })
    flash('Registration successful!', 'success')
    return redirect(url_for('elogin'))
    #return render_template('EntReg.html', success_message='Registration successful!')
  except Exception as e:
    #error_message = 'Email already exists. Please use a different email address.'
    return redirect(url_for('ent_registration'))
    #return render_template('EntReg.html', error_message=error_message)
@app.route('/IDataEntry', methods=["POST", "GET"])
def InvReg():
  firstname = request.form['firstname']
  lastname = request.form['lastname']
  email = request.form['email']
  password = request.form['password']
  mobileNumber = request.form['mobileNumber']
  address = request.form['address']
  age = request.form['age']
  interests = request.form['interests']
  budget= request.form['budget']
  try :
    auth.create_user_with_email_and_password(email, password)
    user = auth.sign_in_with_email_and_password(email, password)
    db.child("InnovationHub").child("Users").child("InvReg").child(user["localId"]).set({
      "firstname": firstname,
      "lastname": lastname,
      "email": email,
      "mobileNumber": mobileNumber,
      "address": address,
      "age": age,
      "interests": interests,
      "budget": budget
    })
    flash('Registration successful!', 'success')
    return redirect(url_for('ilogin'))
    #return render_template('InvReg.html', success_message='Registration successful!')
  except Exception as e:
    #er_message = 'Email already exists. Please use a different email address.'
    return redirect(url_for('inv_registration'))
    #return render_template('InvReg.html', error
    # _message=error_message)
@app.route('/SEProfile',methods=['GET','POST'])
def seprofile():
    #person["type"] = "Entrepreneur"
    #data = db.child("InnovationHub").child("Users").child("EntReg").get().val()
    #entuser = data[person["id"]]
    #person["type"] = "Entrepreneur"
    data = db.child("InnovationHub").child("Users").child("EntReg").get().val()
    #entuser = data["LocalId"]

    #entuser=db.child("InnovationHub").child("Users").child("EntReg").child("LocalId").get().val()
    #print("DATA====================================================")

    ent_id = request.form.get('ent_id')
    print("ID=============================================")
    print(ent_id)

    ent = data[ent_id]

    url = storage.child("images/" + str(ent_id)).get_url(None)
    print("Showing Url------------------------------------------------------")
    print(url)
    return render_template('SEProfile.html', entrepreneurs=ent, image_url=url)

@app.route('/SIProfile',methods=['GET','POST'])
def siprofile():
    invdata = db.child("InnovationHub").child("Users").child("InvReg").get().val()
    investor_id = request.form.get('investor_id')
    if investor_id in invdata:
        invd= invdata[investor_id]
    print(invd)
    return render_template('SIProfile.html',investors=invd)



if __name__ == '__main__':
  app.run(debug=True)



























