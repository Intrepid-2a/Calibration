# Calibration

This repo provides two tasks to adjust the stimuli to the participant:

1. Color Calibration

This task should be done first, as the results are used for the second task.

In this task, participants adjust two colors, while wearing red-green glasses (i.e. left eye through a red filter, right eye through a green filter). There are green stimuli that should appear as dark spots through the red filter, and red stimuli that should appear as dark spots through the green filter. Since the background is a mixture of red and green, the red spots should be close to indistinguishable from the background through the red filter and the green spots should be close to indistinguishable from the background through the green filter. Especially while fixating the central fixation cross.

However, if to the participant, the dots are not indistinguishable from the background while closing one eye, the colors can be adjusted with the arrow keys, as follows.

- `UP` & `DOWN` arrow keys: controls green (seen through the left eye)
- `LEFT` & `RIGHT` arrow keys: controls red (seen through the right eye)

Press `space` to finish colour calibration and write the values to `..\data\color\XXX_col_cal_#.txt` where XXX is the participant ID, and # is the number of calibration attempts. The highest numbered calibration will be used by other tasks.

2. Blind Spot Mapping