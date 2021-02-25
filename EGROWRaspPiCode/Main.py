import threading
# Import Firebase Libraries
import pyrebase
#import datetime
import time
import datetime
import random
#import gpio stuff
import gpiozero
import FBfirestoreupdate
#soil moisture library
import spidev
#DHT11Libraries
import adafruit_dht
from board import *

#set DHT11Pin & Relay Pins
dhtPin = 17
heatingFanRelayPin = 27
fanRelayPin = 16
plant1RelayPin = 22
plant2RelayPin = 5
plant3RelayPin = 6
hoseRelayPin = 26
floatSwitchPin = 25
#Relay Setup
heatingFanRelay = gpiozero.OutputDevice(heatingFanRelayPin, active_high=False, initial_value=True)
fanRelay = gpiozero.OutputDevice(fanRelayPin, active_high=False, initial_value=True)
plant1Relay = gpiozero.OutputDevice(plant1RelayPin, active_high=False, initial_value=True)
plant2Relay = gpiozero.OutputDevice(plant2RelayPin, active_high=False, initial_value=True)
plant3Relay = gpiozero.OutputDevice(plant3RelayPin, active_high=False, initial_value=True)
hoseRelay = gpiozero.OutputDevice(hoseRelayPin, active_high=False, initial_value=True)
floatSwitch = gpiozero.InputDevice(floatSwitchPin, active_state=None)

#set DHT Device @ dhtPin
dht_device = adafruit_dht.DHT11(dhtPin)
# Firebase Database Configuration
config = {
  "apiKey": "AIzaSyAfAAQdELCHn_sVD14nKEh3DA2aKw7mJ-U", #----- Change to customize! -----
  "authDomain": "egrow-20d1c.firebaseapp.com", #----- Change to customize! -----
  "databaseURL": "https://egrow-20d1c.firebaseio.com", #----- Change to customize! -----
  "storageBucket": "egrow-20d1c.appspot.com" #----- Change to customize! -----
}
firebase = pyrebase.initialize_app(config)
# Firebase Database Intialization
db = firebase.database()

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

def getSoilMoistureValues():
    try:
        val1 = spi.xfer2([1,(8+0)<<4,0])
        data1 = ((val1[1]&3) << 8) + val1[2]

        val2 = spi.xfer2([1,(8+1)<<4,0])
        data2 = ((val2[1]&3) << 8) + val2[2]
        
        val3 = spi.xfer2([1,(8+2)<<4,0])
        data3 = ((val3[1]&3) << 8) + val3[2]

    except:
        print("Couldn't find any soil moisture sensors. Help me!")
        data1 = 500
        data2 = 500
        data3 = 500
    
    soilMoistureValues = convertSMToPercent(data1, data2, data3)
    
    return soilMoistureValues

def convertSMToPercent(data1, data2, data3):
    values = [data1, data2, data3]
    index = 0
    for sensorValue in values:
        sensorValue = _map(sensorValue, 1023,0,0,1023)
        percentValue = round((sensorValue-1)*100/(645-1),0)
        percentValue = int(percentValue)
        if percentValue < 10:
            percentValue = str(percentValue)
            percentValue = percentValue.zfill(2)
        elif percentValue >= 100:
            percentValue = 99
        values[index] = percentValue
        index += 1
    return values

def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def getSensorValues():
    #DHT11
    try:
        temperatureInC = dht_device.temperature
        temperature = (temperatureInC * (1.8)) + 32
        temperature = round(temperature, 4)
        humidity = dht_device.humidity
    except:
        print("Couldn't find the DHT11 device! hElP!!!!")
        temperature = 0
        humidity = 0
    
    #Soil Moisture
    soilMoisture = getSoilMoistureValues()
    
    soilMoisture1 = soilMoisture[0]
    soilMoisture2 = soilMoisture[1]
    soilMoisture3 = soilMoisture[2]
    
    #Water Level
        
    waterLevel = floatSwitch.value
    
    return temperature, humidity, waterLevel, soilMoisture1, soilMoisture2, soilMoisture3

def updateFBdatabase(temperature, humidity, waterLevel, soilMoisture1, soilMoisture2, soilMoisture3):
    #updating value in firebase
    db.child("temperature").update({"temperature": temperature})
    db.child("humidity").update({"humidity": humidity})
    db.child("soilmoisture1").update({"soilmoisture1": soilMoisture1})
    db.child("soilmoisture2").update({"soilmoisture2": soilMoisture2})
    db.child("soilmoisture3").update({"soilmoisture3": soilMoisture3})

    if waterLevel < 3:
        db.child("waterlevel").update({"waterlevel": waterLevel})
    print("----success in updating realtime database!")

def getProgramMode():
    mode = db.child("mode").child("mode").get().val()
    #1 = automatic mode
    #2 = manual mode
    return mode


def waterPlant1():
    print("watering plant 1")
    plant1Relay.off()
    time.sleep(30)
    plant1Relay.on()
    
def waterPlant2():
    print("watering plant 2")
    plant2Relay.off()
    time.sleep(30)
    plant2Relay.on()

def waterPlant3():
    print("watering plant 3")
    plant3Relay.off()
    time.sleep(30)
    plant3Relay.on()
    
def turnOnHose(errNum):
    db.child("waterlevel").update({"waterlevel": 2})
    print("attempting to fill the water tank")
    fillTime = 0
    while floatSwitch.value == 0:
        if fillTime < 30:
            print("filling tank")
            hoseRelay.off()
            time.sleep(1)
            fillTime += 1
        elif fillTime >= 30:
            hoseRelay.on()
            break
        
    print("checking water level again")
    sensorValues = getSensorValues()
    print(sensorValues)
    waterLevel = sensorValues[2]
    time.sleep(2)
    if waterLevel != 1:
        if errNum < 2:
            print("the tank is still not full")
            errNum = errNum + 1
            turnOnHose(errNum)
        else:
            waterLevel = 3 ##Error code for something is wrong with the hose fill
            db.child("waterlevel").update({"waterlevel": waterLevel})
            print("There was an error when attempting to fill the tank. The program is now closing")
            sys.exit(0)
    print("water level is ok")
    db.child("waterlevel").update({"waterlevel": waterLevel})
    errNum = 0
    return

def turnOnFan():
    fanRelay.off()
    time.sleep(60)
    fanRelay.on()

def turnOnHeatingFan():
    heatingFanRelay.off()
    time.sleep(120)
    heatingFanRelay.on()

def fbFirestoreUpdate(humidity, temperature, soilMoisture1, soilMoisture2, soilMoisture3, date, time, now):
    FBfirestoreupdate.main(humidity, temperature, soilMoisture1, soilMoisture2, soilMoisture3, date, time, now)

def getDesiredSMvalues():
    desiredSM1 = db.child("desiredSM1").child("desiredSM1").get().val()
    desiredSM2 = db.child("desiredSM2").child("desiredSM2").get().val()
    desiredSM3 = db.child("desiredSM3").child("desiredSM3").get().val()
    desiredSM = [desiredSM1, desiredSM2, desiredSM3]

    return desiredSM
    
#############-----------------BEGIN ACTUAL CODE


def automaticMode():
    now = datetime.datetime.now()
    nowFormatted = now.strftime("%b %d %Y %H:%M:%S")
    date = now.strftime("%b %d %Y")
    time = now.strftime("%H:%M:%S")
    hour = now.strftime("%H")
    minute = now.strftime("%M")
    print("Time that this code ran: "+nowFormatted)
    #Get Sensor Values
    sensorValues = getSensorValues()
    temperature = sensorValues[0]
    humidity = sensorValues[1]
    waterLevel = sensorValues[2]
    soilMoisture1 = sensorValues[3]
    soilMoisture2 = sensorValues[4]
    soilMoisture3 = sensorValues[5]

    print(sensorValues)

    #Thread setup
    dbThread = threading.Thread(target=updateFBdatabase, args=(temperature, humidity, waterLevel, soilMoisture1, soilMoisture2, soilMoisture3))
    firestoreThread = threading.Thread(target=fbFirestoreUpdate, args=(humidity, temperature, soilMoisture1, soilMoisture2, soilMoisture3, date, time, now))
    waterPlant1Thread = threading.Thread(target=waterPlant1)
    waterPlant2Thread = threading.Thread(target=waterPlant2)
    waterPlant3Thread = threading.Thread(target=waterPlant3)
    fanThread = threading.Thread(target=turnOnFan)
    heatingFanThread = threading.Thread(target=turnOnHeatingFan)
    
    if hour == "15" and minute == "34":
        firestoreThread.start()

    #start DB thread
    dbThread.start()

    #check water level in tank
    errNum = 0
    if waterLevel != 1:
       turnOnHose(errNum)

    #check temperature, humidity, soil moisture and act accordingly
    if temperature > 90 or humidity > 70:
        print("fan on")
        fanThread.start()
    elif temperature < 40:
        heatingFanThread.start()
    
    #get desired soil moisture values
    desiredSM = getDesiredSMvalues()
    
    if soilMoisture1 < desiredSM[0]:
        waterPlant1Thread.start()
    
    if soilMoisture2 < desiredSM[1]:
        waterPlant2Thread.start()
    
    if soilMoisture3 < desiredSM[2]:
        waterPlant3Thread.start()

def manualMode():
    now = datetime.datetime.now()
    nowFormatted = now.strftime("%b %d %Y %H:%M:%S")
    date = now.strftime("%b %d %Y")
    time = now.strftime("%H:%M:%S")
    hour = now.strftime("%H")
    minute = now.strftime("%M")
    print("Time that this code ran: "+nowFormatted)
    #Get Sensor Values
    sensorValues = getSensorValues()
    temperature = sensorValues[0]
    humidity = sensorValues[1]
    waterLevel = sensorValues[2]
    soilMoisture1 = sensorValues[3]
    soilMoisture2 = sensorValues[4]
    soilMoisture3 = sensorValues[5]

    print(sensorValues)

    #Thread setup
    dbThread = threading.Thread(target=updateFBdatabase, args=(temperature,humidity,waterLevel, soilMoisture1, soilMoisture2, soilMoisture3))
    firestoreThread = threading.Thread(target=fbFirestoreUpdate, args=(humidity, temperature, soilMoisture1, soilMoisture2, soilMoisture3, date, time, now))
    waterPlant1Thread = threading.Thread(target=waterPlant1)
    waterPlant2Thread = threading.Thread(target=waterPlant2)
    waterPlant3Thread = threading.Thread(target=waterPlant3)
    fanThread = threading.Thread(target=turnOnFan)
    heatingFanThread = threading.Thread(target=turnOnHeatingFan)

    if hour == "15" and minute == "34":
        firestoreThread.start()

    #start DB thread
    dbThread.start()

    #check water level in tank
    errNum = 0
    if waterLevel != 1:
        turnOnHose(errNum)

    #check temperature, humidity, soil moisture and act accordingly
    if temperature > 90 or humidity > 70:
        print("fan on")
        fanThread.start()
    elif temperature < 40:
        heatingFanThread.start()
    
    #get watermyplants value
    waterMyPlants = db.child('watermyplants').child('watermyplants').get().val()
    
    soilMoistureAvg = int((soilMoisture1+soilMoisture2+soilMoisture3)/3)
    #get desired soil moisture values
    desiredSM = getDesiredSMvalues()
    
    if soilMoisture1 >= desiredSM[0] and soilMoisture2 >= desiredSM[1] and soilMoisture3 >= desiredSM[2]:
        print("Plants are sufficiently watered. Updating the DB now.")
        db.child("watermyplants").update({"watermyplants": 0})
        waterMyPlants = 0
    
    if waterMyPlants == 1:
        if soilMoisture1 < desiredSM[0]:
            waterPlant1Thread.start()
        
        if soilMoisture2 < desiredSM[1]:
            waterPlant2Thread.start()
        
        if soilMoisture3 < desiredSM[2]:
            waterPlant3Thread.start()

    

#Begin Main, catch errors
try:
    errNum = 0
    mode = getProgramMode()
    print("mode: "+str(mode))
    if mode == 1:
        automaticMode()
    if mode == 2:
        manualMode()
except Exception as e:
    if errNum < 1:
        errNum = errNum + 1
        print("There was an error"+e)
        print("trying again in 1 second")
        time.sleep(1)
        Main()
    else:
        print("There was a catastrophic error. Something is definitley not right!")
        sys.exit(0)
        

