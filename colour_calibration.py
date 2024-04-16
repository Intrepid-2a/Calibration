#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Colour calibration for monocular/colour glasses presentation
TWCF IIT vs PP experiment 2a
"""

import sys, os
import math
import time
import random
import copy
import os
import numpy as np

from psychopy import core, visual, event, gui, monitors

from psychopy.hardware import keyboard
from pyglet.window import key


def doColorCalibration(ID=None, task=None):

    # site specific handling
    if os.sys.platform == 'linux':
        location = 'toronto'
    else:
        location = 'glasgow'
        
    if location == 'glasgow':
    
        ## info
        expInfo = {'ID':'XXX', 'task':['distance', 'area', 'curvature']}
        dlg = gui.DlgFromDict(dictionary=expInfo)
        
        ID = expInfo['ID'] 
        task = task = expInfo['task']
        
        ## colours
        col_back   = [ 0.55, 0.45,  -1.0] #changed by Belen to prevent bleed or red
        col_red    = [0.55, -1.0,  -1.0]
        col_blue   = [ -1.0, 0.45, -1.0]
        
        ## window & elements
        win = visual.Window([1500,800],allowGUI=True, monitor='ExpMon',screen=1, units='deg', viewPos = [0,0], fullscr = True, color= col_back)
        win.mouseVisible = False
        fixation = visual.ShapeStim(win, vertices = ((0, -1), (0, 1), (0,0), (-1, 0), (1, 0)), lineWidth = 5, units = 'deg', size = (1, 1), closeShape = False, lineColor = 'white')
        
    
    elif location == 'toronto':
        sys.path.append(os.path.join('..', 'EyeTracking'))
        from EyeTracking import localizeSetup, EyeTracker
    
        ## info
        expInfo = {}
        if ID == None:
            expInfo['ID'] = ''
        if task == None:
            expInfo['task'] = ['distance', 'area', 'curvature']
    
        dlg = gui.DlgFromDict(expInfo, title='Infos')
    
        if ID == None:
            ID = expInfo['ID']
        if task == None:
            task = expInfo['task']

        track_eyes = 'none'    # NO CHOICE !
        trackEyes = [False,False]
    
        ## get values
        setup = localizeSetup(location=location, glasses='RG', trackEyes=trackEyes, filefolder=None, filename=None) # data path is for the mapping data, not the eye-tracker data!
        cfg = {}
        cfg['hw'] = setup
        cfg['hw']['tracker'].shutdown()
        
        col_back = cfg['hw']['colors']['col_back']
        col_red  = cfg['hw']['colors']['col_red']
        col_blue = cfg['hw']['colors']['col_blue']
        win = cfg['hw']['win']
        fixation = cfg['hw']['fixation']
    
    else:
        raise ValueError("Location should be 'glasgow' or 'toronto', was {}".format(location))
    
    ## path & file
    data_path = "../data/%s/color/"%(task)
    os.makedirs(data_path, exist_ok=True)
    filename =  ID.lower() + '_col_cal_'
    x = 1
    while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
    
    ## pyglet keyboard
    pyg_keyboard = key.KeyStateHandler()
    win.winHandle.push_handlers(pyg_keyboard)
    
    ## stims
    dot_blue_left  = visual.Circle(win, radius = 0.5, pos = [-7, 7], fillColor = col_blue, colorSpace = 'rgb', lineColor = None)
    dot_red_left   = visual.Circle(win, radius = 0.5, pos = [-7,-7], fillColor = col_red,  colorSpace = 'rgb', lineColor = None)
    dot_both_left  = visual.Circle(win, radius = 0.5, pos = [ 0,-9], fillColor = col_back, colorSpace = 'rgb', lineColor = None)
    dot_blue_right = visual.Circle(win, radius = 0.5, pos = [ 7,-7], fillColor = col_blue, colorSpace = 'rgb', lineColor = None)
    dot_red_right  = visual.Circle(win, radius = 0.5, pos = [ 7, 7], fillColor = col_red,  colorSpace = 'rgb', lineColor = None)
    dot_both_right = visual.Circle(win, radius = 0.5, pos = [ 0, 9], fillColor = col_back, colorSpace = 'rgb', lineColor = None)
    
    step = 0.0015 # RGB color space has 256 values so the step should be 2/256, but that moves too fast


    ## main loop
    frameN = 0
    while 1:
    
        k = event.getKeys(['escape', 'space'])

        if k:
           break

        if pyg_keyboard[key.LEFT]:
            col_red[0]  = max(-1, col_red[0]  - step)
        if pyg_keyboard[key.RIGHT]:
            col_red[0]  = min( 1, col_red[0]  + step)
        if pyg_keyboard[key.UP]:
            col_blue[1] = min( 1, col_blue[1] + step)
        if pyg_keyboard[key.DOWN]:
            col_blue[1] = max(-1, col_blue[1] - step)
        if pyg_keyboard[key.R]:
            print('threshold found', col_red)
        if pyg_keyboard[key.B]:
            print('threshold found', col_blue)


        dot_red_left.fillColor   = col_red
        dot_red_right.fillColor  = col_red
        dot_blue_left.fillColor  = col_blue
        dot_blue_right.fillColor = col_blue

        if frameN >= 0 and frameN < 12:
            dot_both_left.fillColor   = col_red
            dot_both_right.fillColor  = col_red
        else:
            dot_both_left.fillColor  = col_blue
            dot_both_right.fillColor = col_blue

        frameN+=1

        if frameN >23:
            frameN = 0

        fixation.draw()
        dot_both_left.draw()
        dot_blue_left.draw()
        dot_red_left.draw()
        dot_both_right.draw()
        dot_blue_right.draw()
        dot_red_right.draw()

        event.clearEvents(eventType='mouse')
        event.clearEvents(eventType='keyboard')

        win.flip()

    respFile = open(data_path + filename + str(x) + '.txt','w')
    respFile.write('background:\t[{:.8f},{:.8f},{:.8f}]\nred:\t[{:.8f},{:.8f},{:.8f}]\ngreen:\t[{:.8f},{:.8f},{:.8f}]'.format( \
    col_back[0], col_back[1], col_back[2], \
    col_red[0],  col_red[1],  col_red[2],  \
    col_blue[0], col_blue[1], col_blue[2]))
    respFile.close()

    print("background: " + str(col_back))
    print("red: " + str(col_red))
    print("blue: " + str(col_blue))
    
    win.close() # should be after tracker shutdown, since tracker may use the window still...


if __name__ == "__main__":
    doColorCalibration()