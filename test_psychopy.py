
from psychopy import visual, event

win = visual.Window(
    units='pix', fullscr=True, allowGUI=False)

print(win.winHandle)

#win.flip()