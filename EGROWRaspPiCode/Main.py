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
  "apiKey": "******", #----- Change to customize! -----
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
    val1 = spi.xfer2([1,(8+0)<<4,0])
    data1 = ((val1[1]&3) << 8) + val1[2]

    val2 = spi.xfer2([1,(8+1)<<4,0])
    data2 = ((val2[1]&3) << 8) + val2[2]
    
    val3 = spi.xfer2([1,(8+2)<<4,0])
    data3 = ((val3[1]&3) << 8) + val3[2]
    
    soilMoistureValues = convertSMToPercent(data1, data2, data3)
    
    return soilMoistureValues

def convertSMToPercent(data1, data2, data3):
    values = [data1, data2, data3]
    print(values)
    index = 0
    for sensorValue in values:
        sensorValue = _map(sensorValue, 1023,0,0,1023)
        percentValue = round((sensorValue-1)*100/(645-1),0)
        values[index] = percentValue
        index += 1
    return values

def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def getSensorValues():
    #DHT11
    temperatureInC = dht_device.temperature
    temperature = (temperatureInC * (1.8)) + 32
    temperature = round(temperature, 4)
    humidity = dht_device.humidity
    
    #Soil Moisture
    soilMoisture = getSoilMoistureValues()
    
    soilMoisture1 = soilMoisture[0]
    soilMoisture2 = soilMoisture[1]
    soilMoisture3 = soilMoisture[2]
    
    soilMoistureAvg = soilMoisture1#round((soilMoisture1 + soilMoisture2 + soilMoisture3) / 3,0)
    #Water Level
        
    waterLevel = floatSwitch.value
    
    return temperature, humidity, waterLevel, soilMoistureAvg

def updateFBdatabase(temperature, humidity, waterLevel, soilMoisture):
    #updating value in firebase
    db.child("temperature").update({"temperature": temperature})
    db.child("humidity").update({"humidity": humidity})
    db.child("soilmoisture").update({"soilmoisture": soilMoisture})
    if waterLevel < 3:
        db.child("waterlevel").update({"waterlevel": waterLevel})
    print("----success in updating realtime database!")
    
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
    time.sleep(60)
    heatingFanRelay.on()

def fbFirestoreUpdate(humidity, temperature, soilMoisture, date, time):
    FBfirestoreupdate.main(humidity, temperature, soilMoisture, date, time)
    
#############-----------------BEGIN ACTUAL CODE


def Main():
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
    soilMoistureAvg = sensorValues[3]

    print(sensorValues)
    print(soilMoistureAvg)

    #Thread setup
    dbThread = threading.Thread(target=updateFBdatabase, args=(temperature,humidity,waterLevel,soilMoistureAvg))
    firestoreThread = threading.Thread(target=fbFirestoreUpdate, args=(humidity, temperature, soilMoistureAvg, date, time))
    waterPlant1Thread = threading.Thread(target=waterPlant1)
    waterPlant2Thread = threading.Thread(target=waterPlant2)
    waterPlant3Thread = threading.Thread(target=waterPlant3)
    fanThread = threading.Thread(target=turnOnFan)
    heatingFanThread = threading.Thread(target=turnOnHeatingFan)
    
    if hour == "07" and minute == "00":
        firestoreThread.start()
    
    if hour == "16" and minute == "00":
        firestoreThread.start()

    #start DB thread
    dbThread.start()

    #check water level in tank
    errNum = 0
    if waterLevel != 1:
        turnOnHose(errNum)

    #check temperature, humidity, soil moisture and act accordingly
    if temperature > 85 or humidity > 70:
        fanThread.start()
    elif temperature < 50:
        heatingFanThread.start()
        
    if soilMoistureAvg < 21:
        waterPlant1Thread.start()
        waterPlant2Thread.start()
        waterPlant3Thread.start()

#Begin Main, catch errors
try:
    errNum = 0
    Main()
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
        

