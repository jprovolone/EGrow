import os
import sys
sys.path.append('/usr/local/lib/python3.7/dist-packages')
# Import Firebase Libraries
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
#Import Firebase storage and camera
from google.cloud import storage
from firebase import firebase
from picamera import PiCamera
import random
#import datetime
import time
import datetime
from time import sleep
import serial
#DHT11Libraries
# import adafruit_dht
# from board import *
# #set DHT11Pin
# dhtPin = 17

#set DHT Device @ dhtPin
#dht_device = adafruit_dht.DHT11(dhtPin)

# Firebase Database Configuration
config = {
  "apiKey": "********", #----- Change to customize! -----
  "authDomain": "egrow-20d1c.firebaseapp.com", #----- Change to customize! -----
  "databaseURL": "https://egrow-20d1c.firebaseio.com", #----- Change to customize! -----
  "storageBucket": "egrow-20d1c.appspot.com" #----- Change to customize! -----
}


#Firebase firestore cred && initialize
cred = credentials.Certificate('/home/pi/Desktop/egrow-20d1c-firebase-adminsdk-3ui0t-c35f384d1c.json')
firebase_admin.initialize_app(cred)

# Firebase Database Intialization
fireDb = firestore.client()

def takePicture(date, time):
    
    camera = PiCamera()
    camera.rotation = 180
    camera.resolution = (1920, 1355)
    camera.start_preview()
    sleep(5)
    camera.capture('/home/pi/Desktop/{} {}.jpg'.format(date, time))
    camera.stop_preview()
    sleep(3)

    #FIREBASE CRAP
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/home/pi/Desktop/egrow-20d1c-firebase-adminsdk-3ui0t-c35f384d1c.json'

    #firebase = firebase.FirebaseApplication('https://egrow-20d1c.firebaseio.com/')

    client = storage.Client()
    bucket = client.get_bucket('egrow-20d1c.appspot.com')

    #posting to firebase storage

    imageBlob = bucket.blob("/")

    imagePath = "/home/pi/Desktop/{} {}.jpg".format(date, time)
    imageBlob = bucket.blob("{} {}".format(date, time))

    imageBlob.upload_from_filename(imagePath)
    os.remove(imagePath)

def sendToNoah():
    if __name__ == '__main__':
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.flush()

#         ser.write(date.encode('utf-8'))
#         ser.write(b"%")
        ser.write(str(humidity.encode('utf-8')))
        ser.write(b"%")
#         ser.write(temperature.encode('utf-8'))
        ser.write(b"\n")
        
        line = ser.readline().decode('utf-8').rstrip()
        print(line)

def main(humidity, temperature, soilMoisture, date, time):
    errNum = 0
    while(errNum == 0):
        takePicture(date, time)
        print("Success taking and uploading photo!")
        
        #add a document
        doc_ref = fireDb.collection(u'historical data').document(date+" "+time)
        doc_ref.set({
        u'humidity': humidity,
        u'temperature': temperature,
        u'soilMoisture': soilMoisture,
        u'date': date,
        u'time': time
        })
        print("success in updating firestore!")
        #sendToNoah()
        errNum = errNum + 1
#     except Exception as e:
#         print("There seems to have been an error:")
#         print(e)
#         sys.exit(0)

        
        


