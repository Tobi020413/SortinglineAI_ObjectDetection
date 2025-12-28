import base64
import cv2
import datetime
import logging
import numpy as np
import subprocess
import time

from datetime import datetime
from fischertechnik.camera.VideoStream import VideoStream
from fischertechnik.controller.Motor import Motor
from fischertechnik.machine_learning.ObjectDetector import ObjectDetector
from lib.camera import *
from lib.controller import *
from lib.display import *
from lib.node_red import *
from lib.node_red import *

import lib.ki_integration as ki
from collections import Counter




tag = None
value = None
num = None
color = None
ts = None
filename = None
sat = None
hue = None
duration = None
prob = None
keytext = None
pos = None
frame = None
ts_process0 = None
detector = None
result = None
ts_proces = None
key = None
log = None


def MakePictureRunKiReturnFoundPart():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, ts_process0, detector, result, ts_proces, key, log
    reset_inteface()
    TXT_SLD_M_O4_led.set_brightness(int(512))
    time.sleep(0.2)
    TXT_SLD_M_O4_led.set_brightness(int(30))
    time.sleep(0.8)
    duration = (time.time() * 1000)
    num = 4
    prob = 0
    keytext = 'No feature found'
    pos = ''
    display.set_attr("part_pass_fail.text", str(containInHTML('i', 'processing')))
    frame = TXT_SLD_M_USB1_1_camera.read_frame()
    # Neue KI aufrufen
    detections, img_resized = ki.run_inference(frame)

    print("Detections aus neuer KI: {}".format(detections))


    #get color from frame
    color = (np.mean(frame[ 80:120,  100:240], axis=(0, 1)))
    color = cv2.cvtColor(np.uint8([[[color[0],color[1],color[2]]]]),cv2.COLOR_BGR2HLS)[0][0]
    
    print("Color: {}" .format(color))
    
    hue = color[0] # range 0-180
    sat = color[2] # range 0-255
    TXT_SLD_M_C1_motor_step_counter.reset()
    TXT_SLD_M_M1_encodermotor.set_speed(int(160), Motor.CCW)
    TXT_SLD_M_M1_encodermotor.set_distance(int(200))
    ts_process0 = (time.time() * 1000)
    #detector = ObjectDetector('/opt/ft/workspaces/machine-learning/object-detection/sorting_line/model.tflite', '/opt/ft/workspaces/machine-learning/object-detection/sorting_line/labels.txt')
    #result = detector.process_image(frame)
    ts_proces = (time.time() * 1000)
    print('processing time: {:.0f} ms'.format(ts_proces - ts_process0))
    color = get_color()

    print("Color: {}" .format(color))
    
    TXT_SLD_M_O4_led.set_brightness(int(0))

    feature_counts = Counter(det["label"] for det in detections)
    print("Feature-Counts:", feature_counts)

    num_Drillhole = feature_counts.get("Drillhole", 0)  # Label ggf. anpassen
    num_Slot      = feature_counts.get("Slot", 0)
    num_DamagedDrillhole = feature_counts.get("DamagedDrillhole",0 )
    num_Crack = feature_counts.get("Crack", 0)

    if num_Drillhole == 1 and color == 1 and num_Slot == 0 and num_DamagedDrillhole == 0 and num_Crack == 0:
        num = 1
        display.set_attr("white.active", str(True).lower())
        display.set_attr(
            "part_pass_fail.text",
            str(containInHTML('b', "Workpiece <font color='#88ff88'> PASSED</font>"))
        )

    elif num_Slot == 2 and color == 2 and num_DamagedDrillhole == 0 and num_Crack == 0:
        num = 2
        display.set_attr("red.active", str(True).lower())
        display.set_attr(
            "part_pass_fail.text",
            str(containInHTML('b', "Workpiece <font color='#88ff88'> PASSED</font>"))
        )

    elif num_Drillhole == 1 and num_Slot == 2 and color == 3 and num_DamagedDrillhole == 0 and num_Crack == 0:
        num = 3
        display.set_attr("blue.active", str(True).lower())
        display.set_attr(
            "part_pass_fail.text",
            str(containInHTML('b', "Workpiece <font color='#88ff88'> PASSED</font>"))
        )

    elif num_Drillhole <= 1 and color == 1 and num_Slot == 0 and num_DamagedDrillhole == 0 and num_Crack == 0:
        num = 4
        display.set_attr("fail.active", str(True).lower())
        display.set_attr(
            "part_pass_fail.text",
            str(containInHTML('b', "Workpiece <font color='#ff8888'>FAILED</font>"))
        )

    elif num_Drillhole == 0 and num_Slot <= 2 and color == 2 and num_DamagedDrillhole == 0 and num_Crack == 0:
        num = 4
        display.set_attr("fail.active", str(True).lower())
        display.set_attr(
            "part_pass_fail.text",
            str(containInHTML('b', "Workpiece <font color='#ff8888'>FAILED</font>"))
        )

    elif num_Drillhole <= 1 and num_Slot <= 2 and color == 3 and num_DamagedDrillhole == 0 and num_Crack == 0:
        num = 4
        display.set_attr("fail.active", str(True).lower())
        display.set_attr(
            "part_pass_fail.text",
            str(containInHTML('b', "Workpiece <font color='#ff8888'>FAILED</font>"))
        )
    else:
        num = 5
        display.set_attr("fail.active", str(True).lower())
        display.set_attr(
            "part_pass_fail.text",
            str(containInHTML('b', "Workpiece <font color='#ff8888'>FAILED</font>"))
        )

    # Bild für Ausgabe vorbereiten: auf Basis von img_resized (320x320)
    annotated = img_resized.copy()

    for det in detections:
        x1, y1, x2, y2 = det["position"]
        label = det["label"]
        score = det["score"]

        # Rechteck zeichnen (rot)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # Text: Label + Score
        text = "{} {:.2f}".format(label, score)
        cv2.putText(
            annotated,
            text,
            (x1, max(y1 - 5, 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 255),
            1,
            cv2.LINE_AA
        )

    # globales frame durch das annotierte Bild ersetzen,
    # damit saveFileandPublish() das richtige Bild speichert/anzeigt
    frame = annotated


    duration = (time.time() * 1000) - duration
    saveFileandPublish()
    return num


def reset_inteface():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, ts_process0, detector, result, ts_proces, key, log
    display.set_attr("part_pass_fail.text", str(containInHTML('i', 'Not analysed yet')))
    display.set_attr("red.active", str(False).lower())
    display.set_attr("white.active", str(False).lower())
    display.set_attr("blue.active", str(False).lower())
    display.set_attr("fail.active", str(False).lower())


def containInHTML(tag, value):
    global num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, ts_process0, detector, result, ts_proces, key, log
    return ''.join([str(x) for x in ['<', tag, '>', value, '</', tag, '>']])


def get_color():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, ts_process0, detector, result, ts_proces, key, log
    if hue >= 85 and hue < 130 and sat >= 40:
        color = 3
    elif (hue >= 130 and hue <= 180 or hue >= 0 and hue < 15) and sat >= 40:
        color = 2
    else:
        color = 1
    return color


def timestamp():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, ts_process0, detector, result, ts_proces, key, log
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return ts


def saveFileandPublish():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, ts_process0, detector, result, ts_proces, key, log
    filename = '/opt/ft/workspaces/last-image.png'
    if(pos != ""):
        image = cv2.rectangle(frame, (pos[0], pos[1]), (pos[2], pos[3]), (180,105,0), 2)
    logging.debug("write png file: ", filename)
    cv2.imwrite(filename, frame)
    subprocess.Popen(['chmod', '777', filename])

    with open(filename, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    imgb64 = "data:image/jpeg;base64," + (my_string.decode('utf-8'))
    time.sleep(0.2)
    publish(imgb64,keytext,color,num,prob,duration)
    displaystr= "<img width='200' height='150' src='" +  imgb64  + "'>"
    display.set_attr("img_label.text", str(displaystr))


