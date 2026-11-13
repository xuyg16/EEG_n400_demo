"""Sentence RSVP N400 demo using the supplied semicolon-delimited German stimuli."""
import csv
import random
from datetime import datetime
from pathlib import Path

from psychopy import core, event, visual
from pylsl import StreamInfo, StreamOutlet

# ---------- Settings ----------
STIMULI_FILE = Path('stimuli/sentences.csv')
RESULTS_DIR = Path('results')
WORD_S = 0.8                # duration for every word (seconds)
FIXATION_S = 1.5
ITI_MIN_S = 0.8
ITI_MAX_S = 1.2
BREAK_EVERY = 20
N_TRIALS = None             # None = all selected trials; set 10 for a short test
USE_BOTH_CONDITIONS = True # True = all 100 rows; False = one version/item (50 trials)
SCREEN = 1                 # participant screen on lab PC; change to 0 as needed
FULLSCREEN = True
WINDOW_SIZE = (1920, 1080)
DEBUG_MARKERS = False       # Printing inside flip callbacks can affect timing
MARKERS = {'kongruent': 1, 'inkongruent': 2}


def clean_word(word):
    return word.strip('.,!?;:„“"«»()')


def load_sentences(path):
    with path.open('r', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        required = {'item', 'typ', 'bedingung', 'satz', 'krit_pos', 'krit_wort'}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f'Expected CSV columns: {sorted(required)}')
        rows = []
        for line_num, row in enumerate(reader, start=2):
            words = row['satz'].split()
            critical_pos = int(row['krit_pos'])  # 1-based
            if row['bedingung'] not in MARKERS:
                raise ValueError(f'Line {line_num}: unknown condition {row["bedingung"]!r}')
            if not 1 <= critical_pos <= len(words):
                raise ValueError(f'Line {line_num}: krit_pos out of range')
            if clean_word(words[critical_pos - 1]).casefold() != clean_word(row['krit_wort']).casefold():
                raise ValueError(f'Line {line_num}: critical word does not match position')
            rows.append({**row, 'words': words, 'critical_pos': critical_pos})
    return rows


def choose_trials(rows):
    if USE_BOTH_CONDITIONS:
        chosen = rows.copy()
    else:
        groups = {}
        for row in rows:
            groups.setdefault(row['item'], []).append(row)
        # For a demonstration: choose exactly one condition per item,
        # balancing overall counts when there are 50 items.
        ids = list(groups)
        random.shuffle(ids)
        chosen = []
        for idx, item_id in enumerate(ids):
            condition = 'kongruent' if idx % 2 == 0 else 'inkongruent'
            candidates = [r for r in groups[item_id] if r['bedingung'] == condition]
            if len(candidates) != 1:
                raise ValueError(f'Item {item_id} lacks exactly one {condition} sentence')
            chosen.append(candidates[0])
    random.shuffle(chosen)
    if N_TRIALS is not None:
        chosen = chosen[:N_TRIALS]
    return chosen


def wait_for_space(text_stim, message):
    text_stim.text = message
    text_stim.draw()
    win.flip()
    event.clearEvents(eventType='keyboard')
    keys = event.waitKeys(keyList=['space', 'escape'])
    if keys and 'escape' in keys:
        raise KeyboardInterrupt


def send_critical_marker(marker):
    outlet.push_sample([marker])
    if DEBUG_MARKERS:
        print(f'[LSL] critical word marker {marker}', flush=True)


rows = load_sentences(STIMULI_FILE)
trials = choose_trials(rows)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
participant = input('Participant ID: ').strip() or 'test'
filename = RESULTS_DIR / f'{participant}_sentence_rsvp_{datetime.now():%Y%m%d_%H%M%S}.csv'

info = StreamInfo('LSL_Markers', 'Markers', 1, 0, 'int32', 'n400_sentence_rsvp')
outlet = StreamOutlet(info)

win = visual.Window(size=WINDOW_SIZE, fullscr=FULLSCREEN, screen=SCREEN,
                    color='black', units='height', winType='pyglet')
word_stim = visual.TextStim(win, text='', height=0.085, color='white')
message_stim = visual.TextStim(win, text='', height=0.045, color='white',
                               wrapWidth=1.5, alignText='center')

fields = ['trial', 'item', 'typ', 'bedingung', 'satz', 'krit_pos', 'krit_wort',
          'marker', 'n_words', 'word_duration_s', 'iti_s']

try:
    print(f'Loaded {len(rows)} sentences; selected {len(trials)} trials.', flush=True)
    wait_for_space(message_stim,
                   'SENTENCE READING TASK\n\n'
                   'Read each sentence one word at a time.\n'
                   'You do not need to press any response keys.\n\n'
                   'Press SPACE to begin.')
    with filename.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i, trial in enumerate(trials, start=1):
            # Fixation
            word_stim.text = '+'
            word_stim.color = "green"
            word_stim.draw()
            win.flip()
            core.wait(FIXATION_S)

            # Reset to white for RSVP words
            word_stim.color = "white"

            # RSVP: one word per visual presentation
            for pos, token in enumerate(trial['words'], start=1):
                word_stim.text = token
                word_stim.draw()
                if pos == trial['critical_pos']:
                    marker = MARKERS[trial['bedingung']]
                    win.callOnFlip(send_critical_marker, marker)
                win.flip()
                core.wait(WORD_S)

            win.flip()  # clear after final word
            iti_s = random.uniform(ITI_MIN_S, ITI_MAX_S)
            core.wait(iti_s)

            writer.writerow({
                'trial': i,
                'item': trial['item'],
                'typ': trial['typ'],
                'bedingung': trial['bedingung'],
                'satz': trial['satz'],
                'krit_pos': trial['critical_pos'],
                'krit_wort': trial['krit_wort'],
                'marker': MARKERS[trial['bedingung']],
                'n_words': len(trial['words']),
                'word_duration_s': WORD_S,
                'iti_s': round(iti_s, 4),
            })
            f.flush()
            print(f'Trial {i}/{len(trials)}: item={trial["item"]}, {trial["bedingung"]}', flush=True)
            if i % BREAK_EVERY == 0 and i < len(trials):
                wait_for_space(message_stim,
                               f'{i} / {len(trials)} sentences completed.\n\n'
                               'Take a short break.\n\nPress SPACE to continue.')

    wait_for_space(message_stim, 'Experiment completed!\n\nThank you.\n\nPress SPACE to exit.')
except KeyboardInterrupt:
    print('Experiment interrupted.', flush=True)
finally:
    win.close()
    core.quit()
