 #!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blind spot mapping
TWCF IIT vs PP experiment 2a
"""

import sys, os
sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import localizeSetup, EyeTracker, fusionStim


from psychopy import core, visual, gui, data, event, monitors
from psychopy.tools.coordinatetools import pol2cart, cart2pol
import numpy as np
import os

from glob import glob

from psychopy.hardware import keyboard
from pyglet.window import key

def doBlindSpotMapping(ID=None,task=None,hemifield=None):
    
    # site specific handling
    if os.sys.platform == 'linux':
        location = 'toronto'
    else:
        location = 'glasgow'
    
    if location == 'glasgow':
        step = .25
        
        ## info
        expInfo = {'ID':'XXX', 'task':['distance', 'area', 'curvature']}
        dlg = gui.DlgFromDict(expInfo, title='Infos')
        ID = expInfo['ID']
        task = expInfo['task']
        
        ## colours
        col_file = open(glob('../data/' + task + '/color/' + ID + '_col_cal*.txt')[-1],'r')
        col_param = col_file.read().replace('\t','\n').split('\n')
        col_file.close()        
        col_left  = eval(col_param[3])
        col_right = eval(col_param[5])
        col_both = [eval(col_param[3])[1], eval(col_param[5])[0], -1] 
        col_back = [ 0.55,  0.45, -1.00]
        
        ## window & elements
        win = visual.Window([1500,800],allowGUI=True, monitor='ExpMon',screen=1, units='deg', viewPos = [0,0], fullscr = True, color= col_back)
        win.mouseVisible = False
        fixation = visual.ShapeStim(win, vertices = ((0, -2), (0, 2), (0,0), (-2, 0), (2, 0)), lineWidth = 4, units = 'pix', size = (10, 10), closeShape = False, lineColor = col_both)
    
        hiFusion = fusionStim(win = win, pos = [0, 7], colors = [col_both,col_back])
        loFusion = fusionStim(win = win, pos = [0,-7], colors = [col_both,col_back])  
        
        ## eyetracking
        colors = {'both'   : col_both,
                  'back'   : col_back} 
        tracker = EyeTracker(tracker           = 'eyelink',
                             trackEyes         = [True, True],
                             fixationWindow    = 2.0,
                             minFixDur         = 0.2,
                             fixTimeout        = 3.0,
                             psychopyWindow    = win,
                             filefolder        = None,
                             filename          = None,
                             samplemode        = 'average',
                             calibrationpoints = 5,
                             colors            = colors)
                           
        
    elif location == 'toronto':
        step = .02
        
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
            
        ## colours
        col_file = open(glob('../data/' + task + '/color/' + ID + '_col_cal*.txt')[-1],'r')
        col_param = col_file.read().replace('\t','\n').split('\n')
        col_file.close()
        col_left  = eval(col_param[3])
        col_right = eval(col_param[5])
        col_both = [eval(col_param[3])[1], eval(col_param[5])[0], -1]
        colors = { 'left'   : col_left, 
                   'right'  : col_right,
                   'both'   : col_both}        
        glasses = 'RG'
        trackEyes = [True, True]
        
        ## get values
        setup = localizeSetup(location=location, glasses=glasses, trackEyes=trackEyes, filefolder=None, filename=None, colors=colors, task=task) # data path is for the mapping data, not the eye-tracker data!
        colors = setup['colors']
        col_left = colors['left']
        col_right = colors['right']
        
        cfg = {}
        cfg['hw'] = setup
        
        win = cfg['hw']['win']
        tracker = cfg['hw']['tracker']
        hiFusion = setup['fusion']['hi']
        loFusion = setup['fusion']['lo']
        
    else:
        raise ValueError("Location should be 'glasgow' or 'toronto', was {}".format(location))
    
    ## dynamic fixation
    fixation_yes = visual.ShapeStim(win, vertices = ((0, -2), (0, 2), (0,0), (-2, 0), (2, 0)), lineWidth = 2, units = 'pix', size = (10, 10), closeShape = False, lineColor = col_both)
    fixation_no  = visual.ShapeStim(win, vertices = ((0, -2), (0, 2), (0,0), (-2, 0), (2, 0)), lineWidth = 2, units = 'pix', size = (10, 10), closeShape = False, lineColor = col_both, ori = -45)
    fixation = fixation_yes
    
    ## path
    data_path = "../data/%s/mapping/"%(task)
    os.makedirs(data_path, exist_ok=True)

    ## pyglet keyboard
    pyg_keyboard = key.KeyStateHandler()
    win.winHandle.push_handlers(pyg_keyboard)
    
    ## start tracker
    tracker.initialize(calibrationScale=(0.35, 0.35))
    tracker.calibrate()
    tracker.startcollecting()

    
    ## files/task handling through hemifields
    for hemifield in ['left', 'right']:

        if hemifield == 'left':
            filename = ID.lower() + '_LH_blindspot_'
            point = visual.Circle(win, size = [1,1], pos = [-7,-1], fillColor=col_left, lineColor = None, units='deg')
        else:
            filename = ID.lower() + '_RH_blindspot_'
            point = visual.Circle(win, size = [1,1], pos = [7,-1], fillColor=col_right, lineColor = None, units='deg')

        hiFusion.resetProperties()
        loFusion.resetProperties()

        ## make a new file for the participant:
        x = 1
        while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
        respFile = open(data_path + filename + str(x) + '.txt','w')

        ## main loop
        abort = False
        while 1:
            k = event.getKeys(['space', 'escape', '0'])

            if k:
                if 'escape' in k:
                    abort = True
                    break

                if 'space' in k:
                    break

                if '0' in k:
                    tracker.calibrate()

            if tracker.gazeInFixationWindow():
                fixation = fixation_yes
                if pyg_keyboard[key.LCTRL]:
                    k = event.getKeys(['up', 'down', 'left', 'right', 'q', 'w', 'a', 's'])
                    if k:
                        if 'up' in k:
                            point.pos += [ 0, step]
                        if 'down' in k:
                            point.pos += [ 0,-step]
                        if 'left' in k:
                            point.pos += [-step, 0]
                        if 'right' in k:
                            point.pos += [ step, 0]
                        if 'q' in k:
                            point.size += [step,0]
                        if 'w' in k:
                            point.size = [max(step, point.size[0] - step), point.size[1]]
                        if 'a' in k:
                            point.size += [0, step]
                        if 's' in k:
                            point.size = [point.size[0], max(step, point.size[1] - step)]
                else:
                    if pyg_keyboard[key.UP]:
                        point.pos += [ 0, step]
                    if pyg_keyboard[key.DOWN]:
                        point.pos += [ 0,-step]
                    if pyg_keyboard[key.LEFT]:
                        point.pos += [-step, 0]
                    if pyg_keyboard[key.RIGHT]:
                        point.pos += [ step, 0]
                    if pyg_keyboard[key.Q]:
                        point.size += [step,0]
                    if pyg_keyboard[key.W]:
                        point.size = [max(step, point.size[0] - step), point.size[1]]
                    if pyg_keyboard[key.A]:
                        point.size += [0, step]
                    if pyg_keyboard[key.S]:
                        point.size = [point.size[0], max(step, point.size[1] - step)]
            else:
                fixation = fixation_no
            
            
            hiFusion.draw()
            loFusion.draw()
            fixation.draw()
            point.draw()
            win.flip()
        
        ## data saving
        win.getMovieFrame()
        win.saveMovieFrames(data_path + filename + str(x) + '.png')

        respFile.write('position:\t[{:.2f},{:.2f}]\nsize:\t[{:.2f},{:.2f}]'.format(point.pos[0], point.pos[1],  point.size[0], point.size[1]))
        respFile.close()

    ## wrapping up
    tracker.shutdown()
    win.close()
    
if __name__ == "__main__":
    doBlindSpotMapping()