#%% Import
from psychopy import core, event
from psychopy.visual import Window, Rect, TextStim
from pylsl import StreamInfo, StreamOutlet
import random as rand

#%% LSL
def send_triggers(value):
    """Send value as hardware trigger and LSL marker."""
    outlet.push_sample(value)

# Create stream info
info = StreamInfo(name="LSL_Markers", type="Markers", channel_count=1,
                  channel_format="int32", source_id="LSL_Markers_00{}".format(rand.randint(1,9)))
# Make an outlet
outlet = StreamOutlet(info)

#%% Settings
BLACK, WHITE = (-1, -1, -1), (1, 1, 1) # stimulus colors

n_trials = 10 # number of trials
win_size = 1920, 1080  # window size
stim_size = 100, 100  # stimulus size
n_frames = 40  # number of frames: 1 frame at 60 Hz refresh rate is 16 ms

win = Window(size=win_size, fullscr=True, allowGUI = False, color=BLACK,
             units="pix", winType='pyglet', screen=0)

#%% Photosensor stimulus position
LOWER_LEFT = (stim_size[0]/2 - win_size[0]/2, stim_size[1]/2 - win_size[1]/2)
rect1 = Rect(win=win, width=stim_size[0], height=stim_size[1], fillColor=WHITE, pos=LOWER_LEFT)
rect2 = Rect(win=win, width=stim_size[0], height=stim_size[1], fillColor=BLACK, pos=LOWER_LEFT)

#%% Monitor refresh rate

refreshRate = win.getMsPerFrame(nFrames=240) # Get monitor refresh rate

# Stop script if monitor refresh rate is not set to 60 Hz
# if refreshRate[2] <  16 or refreshRate[2] >  17:
#    print("Refresh rate has to be 60 Hz!")
#    win.close()
#    core.quit()

#%% Define text to display
messages = [
    "First word",
    "Second word",
    "Third word",
    "Fourth word"
]

text_stim = TextStim(win=win, text="", pos=(0, 0), color=WHITE, height=60, units="pix")

#%% Main loop

core.wait(1) # Wait before paradigm starts
    
# Send triggers every time an image changes
for i in range(n_trials):
    if event.getKeys(keyList=["escape"]):
        break

    # photosensor flicker -> you won't need that
    win.callOnFlip(send_triggers, [1])
    for n in range(n_frames):
        rect1.draw()
        win.flip()
    win.callOnFlip(send_triggers, [2])
    for n in range(n_frames):
        rect2.draw()
        win.flip()

    # text
    # TODO: add LSL marker
    text_stim.text = messages[i % len(messages)]
    win.callOnFlip(send_triggers, [3])
    for n in range(n_frames):
        text_stim.draw()
        win.flip()

    # jitter -> no idea whether that's typically done for reading paradigms
    # core.wait(0.08+rand.random()/1000*40) # jitter onsets uniform 80-120 ms

# Close & quit
win.close()
core.quit()