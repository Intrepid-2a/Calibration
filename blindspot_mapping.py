 #!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blind spot mapping
TWCF IIT vs PP experiment 2a piloting
Authors: Clement Abbatecola
    Code version:
        0.1 # 2022/10/06
"""

import sys, os
sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import localizeSetup, EyeTracker


from psychopy import core, visual, gui, data, event, monitors
from psychopy.tools.coordinatetools import pol2cart, cart2pol
import numpy as np
import os

from glob import glob

from psychopy.hardware import keyboard
from pyglet.window import key

def doBlindSpotMapping(ID=None,task=None,hemifield=None):
    
    expInfo = {}
    if ID == None:
        ## files
        expInfo['ID'] = ''
    if task == None:
        expInfo['task'] = ['distance', 'area', 'curvature']
    if hemifield == None:
        expInfo['hemifield'] = ['left','right']

    dlg = gui.DlgFromDict(expInfo, title='Infos')

    if ID == None:
        ID = expInfo['ID']
    if task == None:
        task = expInfo['task']
    if hemifield == None:
        hemifield = expInfo['hemifield']

    ## path
    data_path = "../data/%s/mapping/"%(task)
    os.makedirs(data_path, exist_ok=True)

    step = .25

    # col_file = open(glob(main_path + 'mapping_data/' + ID + '_col_cal*.txt')[-1],'r')
    col_file = open(glob('../data/' + task + '/color/' + ID + '_col_cal*.txt')[-1],'r')
    col_param = col_file.read().replace('\t','\n').split('\n')
    col_file.close()
    col_left  = eval(col_param[3])
    col_right = eval(col_param[5])
    col_ipsi  = eval(col_param[3]) if hemifield == 'left' else eval(col_param[5]) # left or right
    col_cont  = eval(col_param[5]) if hemifield == 'left' else eval(col_param[3]) # right or left
    # col_both = [-0.7, -0.7, -0.7] # now dependent on calibrated colors:
    col_both = [eval(col_param[3])[1], eval(col_param[5])[0], -1]
    col_back = [ 0.5, 0.5,  -1.0] # should this come from setupLocalization?

    colors = { 'left'   : col_left, 
               'right'  : col_right,
               'both'   : col_both,
               'ipsi'   : col_ipsi,
               'cont'   : col_cont  } 



    if os.sys.platform == 'linux':
        location = 'toronto'
        step = .02
    else:
        location = 'glasgow'


    glasses = 'RG'
    trackEyes = [True, True]


    setup = localizeSetup(location=location, glasses=glasses, trackEyes=trackEyes, filefolder=None, filename=None, colors=colors) # data path is for the mapping data, not the eye-tracker data!

    cfg = {}
    cfg['hw'] = setup


    pyg_keyboard = key.KeyStateHandler()
    cfg['hw']['win'].winHandle.push_handlers(pyg_keyboard)

    cfg['hw']['tracker'].initialize()
    cfg['hw']['tracker'].calibrate()
    cfg['hw']['tracker'].startcollecting()
    # print('tracking...')


    for hemifield in ['left', 'right']:

        if hemifield == 'left':
            filename = ID.lower() + '_LH_blindspot_'
            # win = visual.Window([1920,1080],allowGUI=True, monitor='ccni', units='deg', viewPos = [0,0], fullscr = True)
            # win = visual.Window(resolution, allowGUI=True, monitor=mymonitor, units='deg', viewPos = [0,0], fullscr=True, screen=1)
            point = visual.Circle(cfg['hw']['win'], size = [1,1], pos = [-7,-1], fillColor=colors['left'], lineColor = None, units='deg')
        else:
            filename = ID.lower() + '_RH_blindspot_'
            # win = visual.Window([1920,1080],allowGUI=True, monitor='ccni', units='deg', viewPos = [0,0], fullscr = True)
            # win = visual.Window(resolution, allowGUI=True, monitor=mymonitor, units='deg', viewPos = [0,0], fullscr=True, screen=1)
            point = visual.Circle(cfg['hw']['win'], size = [1,1], pos = [7,-1], fillColor=colors['right'], lineColor = None, units='deg')

        # print(point.size)
        

        cfg['hw']['fusion']['hi'].resetProperties()
        cfg['hw']['fusion']['lo'].resetProperties()


        # make a new file for the participant:
        x = 1
        while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
        respFile = open(data_path + filename + str(x) + '.txt','w')

        cfg['hw']['win'].mouseVisible = False
        fixation = visual.ShapeStim(cfg['hw']['win'], vertices = ((0, -2), (0, 2), (0,0), (-2, 0), (2, 0)), lineWidth = 2, units = 'pix', size = (10, 10), closeShape = False, lineColor = 'white')
        abort = False

        fixation.draw()
        point.draw()
        cfg['hw']['win'].flip()

        while 1:
            k = event.getKeys(['up', 'down', 'left', 'right', 'q', 'w', 'a', 's', 'space', 'escape', '0'])

            if k:
                if 'escape' in k:
                    abort = True
                    break

                if 'space' in k:
                    break

                if '0' in k:
                    cfg['hw']['tracker'].stopcollecting() # do we even have to stop/start collecting?
                    cfg['hw']['tracker'].calibrate()
                    cfg['hw']['tracker'].startcollecting()

            if cfg['hw']['tracker'].gazeInFixationWindow():

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

            # if anything, fusion patterns should be below other stimuli:
            cfg['hw']['fusion']['hi'].draw()
            cfg['hw']['fusion']['lo'].draw()
            fixation.draw()
            point.draw()
            cfg['hw']['win'].flip()

        cfg['hw']['win'].getMovieFrame()
        cfg['hw']['win'].saveMovieFrames(data_path + filename + str(x) + '.png')

        respFile.write('position:\t[{:.2f},{:.2f}]\nsize:\t[{:.2f},{:.2f}]'.format(point.pos[0], point.pos[1],  point.size[0], point.size[1]))
        respFile.close()


    cfg['hw']['tracker'].stopcollecting()
    # close files here? there shouldn't be any...
    cfg['hw']['tracker'].shutdown()
    cfg['hw']['win'].close()