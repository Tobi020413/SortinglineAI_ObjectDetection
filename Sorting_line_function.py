import logging
import os
import time

from fischertechnik.controller.Motor import Motor
from lib.controller import *
from lib.machine_learning import *


BeltSpeed = None
BeltSteps = None
MovementSpeed = None
PositionBay1 = None
PositionBay2 = None
j = None
PositionBay3 = None
i = None
state_code = None
PositionBay4 = None
PositionCamera = None
dubblepart = None
num = None


def thread_SLD():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    logging.debug('starting thread SLD')
    MovementSpeed = min(max(300, 1), 512)
    PositionBay1 = 195
    PositionBay2 = 280
    PositionBay3 = 360
    PositionBay4 = 443
    PositionCamera = 105
    dubblepart = False
    num = -1
    while True:
        try:
        	mainSLDexternal_th()
        except Exception as e:
        	print(e)
        	clean_exit()


def mainSLDexternal_th():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    if PartInGoodsReceipt():
        reset_inteface()
        logging.debug('start')
        TXT_SLD_M_M1_encodermotor.set_speed(int(MovementSpeed * 0.5), Motor.CCW)
        TXT_SLD_M_M1_encodermotor.start_sync()
        for i in range(401):
            if not PartInGoodsReceipt():
                break
            if i >= 399:
                TXT_SLD_M_M1_encodermotor.stop_sync()
                raise Exception("Insertion fault, workpiece did not clear the lightbeam in expected Time. [Trubleshoot:  Is the workpiece stuck somewhere?]")
            time.sleep(0.01)
        TXT_SLD_M_M1_encodermotor.stop_sync()
        SetBeltSpeedSteps(MovementSpeed, PositionCamera)
        AwaitBeltToReachPosition()
        num = MakePictureRunKiReturnFoundPart()
        if num == 1:
            SetBeltSpeedSteps(MovementSpeed, (PositionBay1 - PositionCamera) - (TXT_SLD_M_C1_motor_step_counter.get_count()))
            AwaitBeltToReachPosition()
            ejectWhite()
        elif num == 2:
            SetBeltSpeedSteps(MovementSpeed, (PositionBay2 - PositionCamera) - (TXT_SLD_M_C1_motor_step_counter.get_count()))
            AwaitBeltToReachPosition()
            ejectRed()
        elif num == 3:
            SetBeltSpeedSteps(MovementSpeed, (PositionBay3 - PositionCamera) - (TXT_SLD_M_C1_motor_step_counter.get_count()))
            AwaitBeltToReachPosition()
            ejectBlue()
        elif num == 4:
            SetBeltSpeedSteps(MovementSpeed, (PositionBay4 - PositionCamera) - (TXT_SLD_M_C1_motor_step_counter.get_count()))
            AwaitBeltToReachPosition()
            ejectFAIL()
        else:
            print("ich will auswerfen")
            SetBeltSpeedSteps(MovementSpeed, 500)
            AwaitBeltToReachPosition()
            ejectFAIL
        if (state_code == 0):
        	raise Exception("Ejection fault, workpiece did not reach storage bay in expected time. [Trubleshoot: Did the workpiece reach the bay? Is it stuck somewhere?]")


def AwaitBeltToReachPosition():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    while True:
        if (not TXT_SLD_M_M1_encodermotor.is_running()):
            break
        time.sleep(0.010)


def SetBeltSpeedSteps(BeltSpeed, BeltSteps):
    global MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    if BeltSteps < 0:
        TXT_SLD_M_M1_encodermotor.set_speed(int(BeltSpeed), Motor.CW)
        TXT_SLD_M_M1_encodermotor.set_distance(int(BeltSteps * -1))
    else:
        TXT_SLD_M_M1_encodermotor.set_speed(int(BeltSpeed), Motor.CCW)
        TXT_SLD_M_M1_encodermotor.set_distance(int(BeltSteps))


def ejectWhite():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    TXT_SLD_M_O3_compressor.on()
    logging.debug('WHITE')
    TXT_SLD_M_O5_magnetic_valve.on()
    for j in range(151):
        state_code = 0
        if isWhite():
            if j <= 30:
                time.sleep((300 - 10 * j) / 1000)
            state_code = 1
            break
        time.sleep(0.01)
    TXT_SLD_M_O5_magnetic_valve.off()
    TXT_SLD_M_O3_compressor.off()


def ejectRed():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    TXT_SLD_M_O3_compressor.on()
    logging.debug('RED')
    TXT_SLD_M_O6_magnetic_valve.on()
    for j in range(151):
        state_code = 0
        if isRed():
            if j <= 30:
                time.sleep((300 - 10 * j) / 1000)
            state_code = 2
            break
        time.sleep(0.01)
    TXT_SLD_M_O6_magnetic_valve.off()
    TXT_SLD_M_O3_compressor.off()


def ejectBlue():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    TXT_SLD_M_O3_compressor.on()
    logging.debug('BLUE')
    TXT_SLD_M_O7_magnetic_valve.on()
    for j in range(151):
        state_code = 0
        if isBlue():
            if j <= 30:
                time.sleep((300 - 10 * j) / 1000)
            state_code = 3
            break
        time.sleep(0.01)
    TXT_SLD_M_O7_magnetic_valve.off()
    TXT_SLD_M_O3_compressor.off()


def ejectFAIL():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    TXT_SLD_M_O3_compressor.on()
    logging.debug('FAIL')
    TXT_SLD_M_O8_magnetic_valve.on()
    for j in range(151):
        state_code = 0
        if isFAIL():
            if j <= 30:
                time.sleep((300 - 10 * j) / 1000)
            state_code = 4
            break
        time.sleep(0.01)
    TXT_SLD_M_O8_magnetic_valve.off()
    TXT_SLD_M_O3_compressor.off()


def isWhite():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    return TXT_SLD_M_I8_photo_transistor.is_dark()


def isRed():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    return TXT_SLD_M_I7_photo_transistor.is_dark()


def isBlue():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    return TXT_SLD_M_I6_photo_transistor.is_dark()


def isFAIL():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    return TXT_SLD_M_I5_photo_transistor.is_dark()


def PartInGoodsReceipt():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    return TXT_SLD_M_I4_photo_transistor.is_dark()


def clean_exit():
    global BeltSpeed, BeltSteps, MovementSpeed, PositionBay1, PositionBay2, j, PositionBay3, i, state_code, PositionBay4, PositionCamera, dubblepart, num
    TXT_SLD_M_O4_led.set_brightness(int(0))
    TXT_SLD_M_O3_compressor.off()
    TXT_SLD_M_M1_encodermotor.stop_sync()
    TXT_SLD_M_O5_magnetic_valve.off()
    TXT_SLD_M_O6_magnetic_valve.off()
    TXT_SLD_M_O7_magnetic_valve.off()
    TXT_SLD_M_O8_magnetic_valve.off()
    os._exit(os.EX_OK)


