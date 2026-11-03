import csv
from datetime import datetime
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet
from pathlib import Path
import random



# ---------- Settings ----------

N_TRIALS = 100  # Change to 100 for the complete experiment

FIXATION_S = 0.5
PRIME_S = 1.0
BLANK_S = 0.7
TARGET_S = 1.0
ITI_S = 0.5

KEY_TO_CONDITION = {
    "left": "related",
    "right": "unrelated"
}


# ---------- Load stimuli ----------

def load_trials(filename):
    trials = []

    with open(filename, encoding="utf-8") as f:
        for line in f:
            words = line.strip().split()

            if not words:
                continue

            if len(words) != 4:
                raise ValueError(
                    f"Expected 4 words, got {len(words)}: {line}"
                )

            related_prime, related_target, unrelated_prime, unrelated_target = words

            trials.append({
                "prime": related_prime,
                "target": related_target,
                "condition": "related",
                "marker": 1
            })

            trials.append({
                "prime": unrelated_prime,
                "target": unrelated_target,
                "condition": "unrelated",
                "marker": 2
            })

    random.shuffle(trials)
    return trials


trials = load_trials(
    Path("stimuli/English/N400_stimuli_list1_English.txt")
)

print(f"Loaded {len(trials)} trials")

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

participant_id = input("Participant ID: ").strip() or "test"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = RESULTS_DIR / f"{participant_id}_{timestamp}.csv"

results = []

# ---------- LSL setup ----------

info = StreamInfo(
    name="LSL_Markers",
    type="Markers",
    channel_count=1,
    nominal_srate=0,
    channel_format="int32",
    source_id="n400_demo"
)

outlet = StreamOutlet(info)


# ---------- PsychoPy setup ----------

win = visual.Window(
    size=(1920, 1080),
    fullscr=True,
    screen=1,
    color="black",
    units="height",
    winType="pyglet"
)

word = visual.TextStim(
    win,
    text="",
    color="white",
    height=0.08
)




# ---------- Presentation functions ----------

def show_instructions():
    instructions = visual.TextStim(
        win,
        text=(
            "WORD RELATIONSHIP TASK\n\n"
            "You will see two words, one after another.\n\n"
            "Decide whether they are related in meaning.\n\n"
            "LEFT arrow = Related\n"
            "RIGHT arrow = Unrelated\n\n"
            "Press SPACE to begin."
        ),
        color="white",
        height=0.045,
        wrapWidth=1.5,
        alignText="center"
    )

    instructions.draw()
    win.flip()

    event.clearEvents()
    event.waitKeys(keyList=["space"])


def show_text(text, duration, color="white"):
    word.text = text
    word.color = color
    word.draw()

    win.flip()
    core.wait(duration)


def show_end_screen():
    end_text = visual.TextStim(
        win,
        text=(
            "Experiment completed!\n\n"
            "Thank you for your participation.\n\n"
            "Press SPACE to exit."
        ),
        color="white",
        height=0.05,
        alignText="center"
    )

    end_text.draw()
    win.flip()

    event.clearEvents()
    event.waitKeys(keyList=["space"])



# ---------- Main experiment ----------

try:
    show_instructions()

    for i, trial in enumerate(trials[:N_TRIALS]):

        print(
            f"Trial {i + 1}: "
            f"{trial['prime']} -> {trial['target']} "
            f"({trial['condition']})",
            flush=True
        )

        # 1. Fixation
        show_text("+", FIXATION_S)

        # 2. Prime
        show_text(trial["prime"], PRIME_S, color="orange")

        # 3. Blank interval
        win.flip()
        core.wait(BLANK_S)

        
        # 4. Prepare target
        word.text = trial["target"]
        word.color = "green"
        word.draw()

        # Prepare clock and clear previous keypresses
        target_clock = core.Clock()
        event.clearEvents(eventType="keyboard")

        # Reset clock and send LSL marker at target onset
        win.callOnFlip(target_clock.reset)
        win.callOnFlip(
            outlet.push_sample,
            [int(trial["marker"])]
        )

        win.flip()

        # 5. Collect response
        response_key = None
        response_rt = None
        target_cleared = False

        reminder = visual.TextStim(
            win,
            text="LEFT = Related\nRIGHT = Unrelated",
            color="white",
            height=0.045,
            alignText="center"
        )

        while True:
            elapsed = target_clock.getTime()

            # After the target duration, show the reminder
            if not target_cleared and elapsed >= TARGET_S:
                reminder.draw()
                win.flip()
                target_cleared = True

                # Ignore responses before reminder onset
                event.clearEvents(eventType="keyboard")

            if target_cleared:
                keys = event.getKeys(
                    keyList=["left", "right", "escape"],
                    timeStamped=target_clock
                )

                for key_name, key_rt in keys:
                    if key_name == "escape":
                        raise KeyboardInterrupt

                    if response_key is None:
                        response_key = key_name
                        response_rt = key_rt

            # Advance only after a response
            if response_key is not None:
                break

            core.wait(0.005)

        # 6. Calculate accuracy
        response = KEY_TO_CONDITION[response_key]
        correct = response == trial["condition"]

        print(
            f"Response: {response}, "
            f"RT: {response_rt:.3f}s, "
            f"Correct: {correct}",
            flush=True
        )

        results.append({
            "trial": i + 1,
            "prime": trial["prime"],
            "target": trial["target"],
            "condition": trial["condition"],
            "marker": trial["marker"],
            "response": response,
            "rt_s": round(response_rt, 4),
            "correct": int(correct)
        })

        with open(results_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "trial",
                    "prime",
                    "target",
                    "condition",
                    "marker",
                    "response",
                    "rt_s",
                    "correct"
                ]
            )

            writer.writeheader()
            writer.writerows(results)

        # 7. Brief blank before next fixation
        win.flip()
        core.wait(ITI_S)

    show_end_screen()
except KeyboardInterrupt:
    print("Experiment stopped by user.")

finally:
    win.close()
    core.quit()
