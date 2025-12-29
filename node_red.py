import base64
import cv2
import json
import logging
import numpy as np
import paho.mqtt.client as mqtt

from datetime import datetime


imagedata = None
description = None
color = None
bay = None
confidence = None
duration = None
client = None
string = None
ts = None


def mqtt_client_forever():
    global imagedata, description, color, bay, confidence, duration, client, string, ts
    client = mqtt.Client("mqtt_client")
    client.connect('127.0.0.1',2883,60)
    #client.on_message=on_message
    #client.subscribe("#")
    client.loop_forever()
    return client


def get_client():
    global imagedata, description, color, bay, confidence, duration, client, string, ts
    return client


def publish(imagedata, description, color, bay, confidence, duration):
    global client, string, ts
    string = '{{ "ts":"{}", "description":"{}", "color":"{}", "bay":"{}", "confidence":"{}", "data":"{}", "duration":"{}" }}'.format(timestamp(), description, color, bay, confidence, imagedata, duration)
    logging.debug("sending...")
    ret = client.publish("i/cam",string)


def timestamp():
    global imagedata, description, color, bay, confidence, duration, client, string, ts
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    return ts


