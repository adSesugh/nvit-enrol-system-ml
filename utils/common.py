# get a number of total registered users
import os
from datetime import date, datetime

import cv2
import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier


# Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")

# If these directories don't exist, create them
if not os.path.isdir('app/Attendance'):
    os.makedirs('app/Attendance')
if not os.path.isdir('app/static'):
    os.makedirs('app/static')
if not os.path.isdir('app/static/faces'):
    os.makedirs('app/static/faces')
if f'Attendance-{datetoday}.csv' not in os.listdir('app/Attendance'):
    with open(f'app/Attendance/Attendance-{datetoday}.csv', 'w') as f:
        f.write('StudentNo,FirstName,MiddleName,LastName,Course,Time')

nimgs = 10

# Initializing VideoCapture object to access WebCam
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


def totalreg():
    return len(os.listdir('app/static/faces'))


# extract the face from an image
def extract_faces(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return face_points
    except:
        return []


# Identify face using ML model
def identify_face(facearray):
    model = joblib.load('app/static/face_recognition_model.pkl')
    return model.predict(facearray)


# A function which trains the model on all the faces available in faces folder
def train_model():
    faces = []
    labels = []
    userlist = os.listdir('app/static/faces')
    for user in userlist:
        for imgname in os.listdir(f'app/static/faces/{user}'):
            img = cv2.imread(f'app/static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (50, 50))
            faces.append(resized_face.ravel())
            labels.append(user)
    faces = np.array(faces)
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(faces, labels)
    joblib.dump(knn, 'app/static/face_recognition_model.pkl')


# Extract info from today's attendance file in attendance folder
def extract_attendance():
    df = pd.read_csv(f'app/Attendance/Attendance-{datetoday}.csv')
    mats = df['StudentNo']
    names = f'{df["LastName"]} {df["FirstName"]}'
    courses = df['Course']
    times = df['Time']

    l = len(df)
    return mats, names, courses, times, l


# Add Attendance of a specific user
def add_attendance(name):
    username = name.split('_')[0]
    userid = name.split('_')[1]
    current_time = datetime.now().strftime("%H:%M:%S")
    df = pd.read_csv(f'app/Attendance/Attendance-{datetoday}.csv')
    if int(userid) not in list(df['Roll']):
        with open(f'app/Attendance/Attendance-{datetoday}.csv', 'a') as f:
            f.write(f'\n{username},{userid},{current_time}')


def getallusers():
    userlist = os.listdir('app/static/faces')
    numbers = []
    names = []
    rolls = []
    l = len(userlist)

    for i in userlist:
        roll, name = i.split('_')
        names.append(name)
        rolls.append(roll)

    return userlist, names, rolls, l


def deletefolder(duser):
    pics = os.listdir(duser)
    for i in pics:
        os.remove(duser + '/' + i)
    os.rmdir(duser)


courses = [
    {'name':'Applied AI and ML Engineering for Business Transformation and Real-world Applications', 'code': 'AIML'},
    {'name': 'Applied Cloud and DevOps Engineering', 'code': 'ACDE'},
    {'name':'Applied Data Science and Engineering', 'code':'ADSE'},
    {'name':'Applied Enhanced Human-Centered UX/UI Product Design', 'code':'UIUX'},
    {'name': 'Applied Full-Stack Python Development Track', 'code':'FSPD'},
    {'name':'Applied IT Technical Support & Operations Engineering', 'code':'ITSO'}
]


def course_code(course):
    code = ''
    for cor in courses:
        if cor['name'] == course:
            code = cor['code']
            break

    return code
