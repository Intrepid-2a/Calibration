# Calibration

This repo provides two tasks to adjust the stimuli to the participant:

## 1. Color Calibration

This task should be done first, as the results are used for the second task.

In this task, participants adjust two colors, while wearing red-green glasses (i.e. left eye through a red filter, right eye through a green filter). There are green stimuli that should appear as dark spots through the red filter, and red stimuli that should appear as dark spots through the green filter. Since the background is a mixture of red and green, the red spots should be close to indistinguishable from the background through the red filter and the green spots should be close to indistinguishable from the background through the green filter. Especially while fixating the central fixation cross.

However, if to the participant, the dots are not indistinguishable from the background while closing one eye, the colors can be adjusted with the arrow keys, as follows.

- `UP` & `DOWN` arrow keys: controls green (seen through the left eye)
- `LEFT` & `RIGHT` arrow keys: controls red (seen through the right eye)

Press `SPACE` to finish colour calibration and write the values to `..\data\color\XXX_col_cal_#.txt` where XXX is the participant ID, and # is the number of calibration attempts. The highest numbered calibration will be used by other tasks.

The file:

`color_calibration.py`

provides a function:

`doColorCalibration()`

that runs the task.

Arguments to the function:

- `ID`: _string_ the ID of the participant, if not provided, a pop-up asks to enter the ID

## 2. Blind Spot Mapping

A short PsychoPy task where a marker is moved and resized until it can just _not_ be seen by one eye: when it is in the blind spot of that eye. This should be done _after_ color calibration (different repository in Intrepid-2a) since this task assumes the participant is wearing red-blue glasses and needs to read the calibrated colors for the participant such that the marker can be made invisible to the contralateral eye to begin with.

- `LEFT`, `RIGHT`, `UP`, `DOWN` arrow keys to move the marker

- `Q`, `W` to in/decrease the height.

- `A`, `S` to in/decrease the width.

The procedure starts with the left eye (red marker). When you are satisfied that the marker can not be any bigger and remain invisble, press `SPACE`. It then does the right eye (green marker), which is also finished by pressing `SPACE`.

It stores both the left and right eye blind spots in `../data/mapping/` in a file for each eye/hemisphere called: `{participant}_{RH|LH}_blindspot_{#}.txt` filling in participant ID, hemisphere and the number of times the mapping procedure has been done. It also stores screenshots of the final stimuli as png's but otherwise the same file name.

The file:

`blindspot_mapping.py`

provides a function:

`doBlindSpotMapping()`

that runs the task.

Arguments to the function:

- `ID`: _string_ the ID of the participant, if not provided, a pop-up asks to enter the ID
