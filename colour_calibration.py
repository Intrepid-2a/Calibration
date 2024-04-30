#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Colour calibration for monocular/colour glasses presentation.
TWCF IIT vs PP experiment 2a piloting
Authors: Clement Abbatecola, Belén María Montabes de la Cruz, Marius 't Hart
    Code version:
        0.1 # 2022/10/06
"""

import sys, os
sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import localizeSetup, EyeTracker



# import LiveTrack
import math
import time
import random
import copy
import os
import numpy as np
# from LT import LTcal, LTrefix

from psychopy import core, visual, event, gui, monitors

from psychopy.hardware import keyboard
from pyglet.window import key


def doColorCalibration(ID=None, task=None):

    expInfo = {}
    askQuestions = False
    if ID == None:
        ## files
        expInfo['ID'] = ''
        askQuestions = True
    if task == None:
        expInfo['task'] = ['distance', 'area', 'curvature']
        askQuestions = True

    if askQuestions:
        dlg = gui.DlgFromDict(expInfo, title='Infos')

    if ID == None:
        ID = expInfo['ID']
    if task == None:
        task = expInfo['task']

    ## path
    data_path = "../data/%s/color/"%(task)
    os.makedirs(data_path, exist_ok=True)

    filename = ID.lower() + '_col_cal_'

    glasses = 'RG' # NO CHOICE !


    # colors will come from the localizeSetup function, depending on things

    # if glasses == 'RG':
    #     back_col   = [ 0.5, 0.5,  -1.0]
    #     red_col    = [0.5, -1.0,  -1.0]
    #     blue_col   = [ -1.0, 0.5, -1.0]
    # elif glasses == 'RB':
    #     back_col   = [ 0.5, -1.0,  0.5]
    #     red_col    = [ 0.5, -1.0, -1.0] #Flipped back 
    #     blue_col   = [-1.0, -1.0,  0.5] 


    track_eyes = 'none'    # NO CHOICE !
    trackEyes = [False,False]

    # need location
    if os.sys.platform == 'linux':
        location = 'toronto'
    else:
        location = 'glasgow'

    # filefoder needs to be specified? maybe not for color calibration? no eye-tracking files will be written...
    # not sending colors to localize setup, since we're still determining them here: use defaults for now!
    setup = localizeSetup(location=location, glasses=glasses, trackEyes=trackEyes, filefolder=None, filename=None) # data path is for the mapping data, not the eye-tracker data!

    cfg = {}
    cfg['hw'] = setup

    # since these values will be changed and stored in a file, let's make them available locally:
    back_col = cfg['hw']['colors']['back'] # technically, this one will not need to be changed, it should be a constant?
    red_col  = cfg['hw']['colors']['red']
    blue_col = cfg['hw']['colors']['blue'] # actually green?

    print(cfg['hw']['colors'])

    # print(cfg['hw']['win'].monitor.getGammaGrid())
    # print(cfg['hw']['win'].color)

    # open file here:
    x = 1
    while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
    respFile = open(data_path + filename + str(x) + '.txt','w')

    # add pyglet keyboard stuff:
    pyg_keyboard = key.KeyStateHandler()
    cfg['hw']['win'].winHandle.push_handlers(pyg_keyboard)

    dot_blue_left  = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [-7, 7], fillColor = cfg['hw']['colors']['blue'], colorSpace = 'rgb', lineColor = None)
    dot_red_left   = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [-7,-7], fillColor = cfg['hw']['colors']['red'],  colorSpace = 'rgb', lineColor = None)
    dot_both_left  = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [ 0,-9], fillColor = cfg['hw']['colors']['back'], colorSpace = 'rgb', lineColor = None)

    dot_blue_right = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [ 7,-7], fillColor = cfg['hw']['colors']['blue'], colorSpace = 'rgb', lineColor = None)
    dot_red_right  = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [ 7, 7], fillColor = cfg['hw']['colors']['red'],  colorSpace = 'rgb', lineColor = None)
    dot_both_right = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [ 0, 9], fillColor = cfg['hw']['colors']['back'], colorSpace = 'rgb', lineColor = None)

    # fixation = visual.ShapeStim(cfg['hw']['win'], vertices = ((0, -1), (0, 1), (0,0), (-1, 0), (1, 0)), lineWidth = 5, units = 'deg', size = (1, 1), closeShape = False, lineColor = 'white')


    step = 0.0015 # RGB color space has 256 values so the step should be 2/256, but that moves too fast

    frameN = 0
    while 1:

        # k = event.getKeys(['left', 'right', 'up', 'down' ,'escape', 'space', '1', 'q'])
        k = event.getKeys(['escape', 'space', 'q'])

        if k:
            if k[0] in ['q']:
                calibration_triggered
            if k[0] in ['space','escape']:
                break

            # if k[0] == 'left':
            #     red_col[2]  = max(-1, red_col[2]  - step)
            # if k[0] == 'right':
            #     red_col[2]  = min( 1, red_col[2]  + step)
            # if k[0] == 'up':
            #     blue_col[0] = min( 1, blue_col[0] + step)
            # if k[0] == 'down':
            #     blue_col[0] = max(-1, blue_col[0] - step)

            if k[0] == '1':
                print("red: " + str(red_col))
                print("blue: " + str(blue_col))


        # check fixation
        allow_calibration = True

        # if cfg['hw']['tracker'].gazeInFixationWindow():
        #     allow_calibration = True
        # else:
        #     allow_calibration = False



        if allow_calibration:
            if glasses == 'RG':
                if pyg_keyboard[key.LEFT]:
                    red_col[0]  = max(-1, red_col[0]  - step)
                if pyg_keyboard[key.RIGHT]:
                    red_col[0]  = min( 1, red_col[0]  + step)
                if pyg_keyboard[key.UP]:
                    blue_col[1] = min( 1, blue_col[1] + step)
                if pyg_keyboard[key.DOWN]:
                    blue_col[1] = max(-1, blue_col[1] - step)
                if pyg_keyboard[key.R]:
                    print('threshold found', red_col)
                if pyg_keyboard[key.B]:
                    print('threshold found', blue_col)
            elif glasses == 'RB':
                if pyg_keyboard[key.LEFT]:
                    red_col[0]  = max(-1, red_col[0]  - step)
                if pyg_keyboard[key.RIGHT]:
                    red_col[0]  = min( 1, red_col[0]  + step)
                if pyg_keyboard[key.UP]:
                    blue_col[2] = min( 1, blue_col[2] + step)
                if pyg_keyboard[key.DOWN]:
                    blue_col[2] = max(-1, blue_col[2] - step)


        dot_red_left.fillColor   = red_col
        dot_red_right.fillColor  = red_col
        dot_blue_left.fillColor  = blue_col
        dot_blue_right.fillColor = blue_col

        if frameN >= 0 and frameN < 12:
            dot_both_left.fillColor   = red_col
            dot_both_right.fillColor  = red_col
        else:
            dot_both_left.fillColor  = blue_col
            dot_both_right.fillColor = blue_col

        frameN+=1

        if frameN >23:
            frameN = 0

        # fixation.draw()
        cfg['hw']['fixation'].draw()
        # dot_both_left.draw()
        dot_blue_left.draw()
        dot_red_left.draw()
        # dot_both_right.draw()
        dot_blue_right.draw()
        dot_red_right.draw()

        event.clearEvents(eventType='mouse')
        event.clearEvents(eventType='keyboard')

        cfg['hw']['win'].flip()


        # if calibration_triggered:

        #     cfg['hw']['tracker'].stopcollecting()

        #     cfg['hw']['tracker'].calibrate()

        #     cfg['hw']['tracker'].startcollecting()

        #     calibration_triggered = False


    respFile.write('background:\t[{:.8f},{:.8f},{:.8f}]\nred:\t[{:.8f},{:.8f},{:.8f}]\ngreen:\t[{:.8f},{:.8f},{:.8f}]'.format( \
    back_col[0], back_col[1], back_col[2], \
    red_col[0],  red_col[1],  red_col[2],  \
    blue_col[0], blue_col[1], blue_col[2]))
    respFile.close()


    # to CLI:
    print("background: " + str(back_col))
    print("red: " + str(red_col))
    print("blue: " + str(blue_col))

    # cfg['hw']['tracker'].stopcollecting()
    # cfg['hw']['tracker'].closefile()
    cfg['hw']['tracker'].shutdown()
    cfg['hw']['win'].close() # should be after tracker shutdown, since tracker may use the window still...



