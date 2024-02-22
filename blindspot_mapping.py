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
# sys.path.append(os.path.join('..', 'EyeTracking'))
# from EyeTracking import EyeTracker
sys.path.append(os.path.join('..', 'System'))
from System import localizeSetup


from psychopy import core, visual, gui, data, event, monitors
from psychopy.tools.coordinatetools import pol2cart, cart2pol
import numpy as np
import os

from glob import glob

from psychopy.hardware import keyboard
from pyglet.window import key

## path
data_path = "../data/mapping/"

## files
expInfo = {'ID':'XXX'}
dlg = gui.DlgFromDict(expInfo, title='Infos')

step = .01

# gammaGrid = np.array([  [  0., 135.44739,  2.4203537, np.nan, np.nan, np.nan  ],
#                         [  0.,  27.722954, 2.4203537, np.nan, np.nan, np.nan  ],
#                         [  0.,  97.999275, 2.4203537, np.nan, np.nan, np.nan  ],
#                         [  0.,   9.235623, 2.4203537, np.nan, np.nan, np.nan  ]], dtype=float)

# resolution = [1920, 1080]
# size = [59.8, 33.6]
# distance = 50

# mymonitor = monitors.Monitor(name='temp',
#                              distance=distance,
#                              width=size[0])

# mymonitor.setGammaGrid(gammaGrid)
# mymonitor.setSizePix(resolution)


# win = visual.Window(resolution, allowGUI=True, monitor=mymonitor, units='deg', fullscr=True, screen=1)

## colour (eye) parameters
col_file = open(glob('../data/color/' + expInfo['ID'] + "_col_cal*.txt")[-1],'r')
col_param = col_file.read().replace('\t','\n').split('\n')
col_file.close()
col_back  = eval(col_param[1])
col_left  = eval(col_param[3]) # a red color, invisble to the left eye, which has the green-pass filter
col_right = eval(col_param[5]) # a green color, ...
# col_both  = [col_left[0], -1, col_right[2]] # Red BLUE glasses
col_both  = [col_left[0], col_right[1], -1] # red green glasses



if os.sys.platform == 'linux':
    location = 'toronto'
else:
    location = 'glasgow'


glasses = 'RG'
trackEyes = [True, True]


setup = localizeSetup(location=location, glasses=glasses, trackEyes=trackEyes, filefolder=None) # data path is for the mapping data, not the eye-tracker data!

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
        filename = expInfo['ID'].lower() + '_LH_blindspot_'
        # win = visual.Window([1920,1080],allowGUI=True, monitor='ccni', units='deg', viewPos = [0,0], fullscr = True)
        # win = visual.Window(resolution, allowGUI=True, monitor=mymonitor, units='deg', viewPos = [0,0], fullscr=True, screen=1)
        point = visual.Circle(cfg['hw']['win'], size = [1,1], pos = [-7,-1], fillColor=col_left, lineColor = None, units='deg')
    else:
        filename = expInfo['ID'].lower() + '_RH_blindspot_'
        # win = visual.Window([1920,1080],allowGUI=True, monitor='ccni', units='deg', viewPos = [0,0], fullscr = True)
        # win = visual.Window(resolution, allowGUI=True, monitor=mymonitor, units='deg', viewPos = [0,0], fullscr=True, screen=1)
        point = visual.Circle(cfg['hw']['win'], size = [1,1], pos = [7,-1], fillColor=col_right, lineColor = None, units='deg')

    print(point.size)
    

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
        k = event.getKeys(['up', 'down', 'left', 'right', 'q', 'w', 'a', 's', 'space', 'escape'])

        if k:
            if 'escape' in k:
                abort = True
                break

            if 'space' in k:
                break

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

    respFile.write('position:\t[{:.1f},{:.1f}]\nsize:\t[{:.1f},{:.1f}]'.format(point.pos[0], point.pos[1],  point.size[0], point.size[1]))
    respFile.close()


cfg['hw']['tracker'].stopcollecting()
# close files here? there shouldn't be any...
cfg['hw']['tracker'].shutdown()
cfg['hw']['win'].close()