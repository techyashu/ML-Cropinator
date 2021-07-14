#!/usr/bin/env python
# coding: utf-8

# In[17]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors
from sklearn import preprocessing
from mlxtend.plotting import plot_decision_regions
import codecs
import paho.mqtt.client as paho
import queue
import lcddriver
import time
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
#Select GPIO mode
GPIO.setmode(GPIO.BCM)
#Set buzzer - pin 23 as output
buzzer=23
GPIO.setup(buzzer,GPIO.OUT)

display = lcddriver.lcd()
q=queue.Queue(2)

broker="192.168.0.106" #IP of your Raspberry Pi
display.lcd_clear()
display.lcd_display_string(" ML  Cropinator ", 1)
display.lcd_display_string("----------------", 2)
sleep(2)

x=0
def func():
    global x
    x=x+1
    if x == 2:
        crop (int(q.get()),float(q.get()))
        x=0
    


# In[18]:


def disp(s):
    time.sleep(1)
    display.lcd_clear()
    GPIO.output(buzzer,GPIO.LOW)
    display.lcd_display_string("Crop to be Grown :", 1) # Write line of text to first line of display
    display.lcd_display_string("->>> "+s.upper(), 2) # Write line of text to second line of display
    time.sleep(5)                                     # Give time for the message to be read
        

def crop(p,q):
    #importing the csv file or dataset
    display.lcd_clear()
    GPIO.output(buzzer,GPIO.HIGH)
    display.lcd_display_string("ML Model Running", 1)
    display.lcd_display_string("Predicting...", 2)
    sleep(3)
    crops = pd.read_csv(r'/home/pi/crop2.csv',error_bad_lines=False,encoding='utf-8')
    crop_feature_name = ['rainfall','fav_temp']
    x_crops = crops[crop_feature_name]       #naming the parameters
    y_crops = crops['crop_label']            #naming the 5 labels
    crop_name = ['rice','maize','wheat','millet','rabi']
    crops_plot = crops
    #crops.head()    #un-comment to print first 5 rows of dataset


    # In[19]:


    #train-test splitting of available data
    # 75:25 train:test division
    x_crops2d = crops[crop_feature_name]
    y_crops2d = crops['crop_label']
    X_train, X_test, y_train, y_test = train_test_split(x_crops2d, y_crops2d, random_state=1)

    #rescaling features
    #Creating a minimum and maximum processor object
    scaler = MinMaxScaler()
    x_plot = scaler.fit_transform(x_crops2d)
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    df_normalized = pd.DataFrame(x_plot)

    df_normalized.columns = ["rainfall","fav_temp"]
    df_normalized1= df_normalized*4
    #knn model
    knn = KNeighborsClassifier(n_neighbors = 3)
    knn.fit(X_train_scaled, y_train)               #fitting done

    #MAIN FEATURE OF THE MODEL : PREDICTING THE TYPE OF CROP BY TAKING REAL TIME INPUT THROUGH SENSORS
    rain =p           #variable for rainfall (in mm) eg 750
    temp =q             #temperature variable (deg C) eg 25
    example_crop = [[rain,temp]]
    example_crop_scaled = scaler.transform(example_crop)
    #Making an prediction based on the 2 parameters
    print('Predicted crop type for ', example_crop, ' is ',
              crop_name[knn.predict(example_crop_scaled)[0]-1])    #HERE IS THE ACTUAL OUTPUT
    
    disp(crop_name[knn.predict(example_crop_scaled)[0]-1])
   
    


def on_message(client, userdata, message):
    #print("received message =",str(message.payload.decode("utf-8")))
    #p=int(message.payload.decode("utf-8"))
    #crop(p)
    #print ("in the function last")
    q.put(message.payload.decode("utf-8"))
    func()
    #xyz()
    #while not q.empty():
    #print (q.get())
    #loop.stop()
   


client= paho.Client("client-001")
client.on_message=on_message
print("connecting to broker ",broker)
client.connect(broker)
print("subscribing ")
client.subscribe("sensor_data")
client.subscribe("temp")
client.loop_forever()
#client.loop_start()