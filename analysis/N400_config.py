import mne

bids_root = "../2026N400_demo"    #NOTE: change this to your dataset dir
deriv_root = bids_root + "/derivatives"
sessions = ["001"]
task = "n400"
runs = ["1"]
subjects = ["002"]
ch_types = ["eeg"]
data_type = "eeg"


pyprep_bad_chans = True

raw_resample_sfreq = 250.0
l_freq = 0.1
h_freq = 40.0
notch_freq = 50.0
epochs_tmin = -0.2
epochs_tmax = 0.8

spatial_filter = "ica"
ica_l_freq=1
ica_h_freq=100
ica_algorithm = "picard-extended_infomax"
ica_n_components = 0.99
ica_use_icalabel = True
ica_reject =  {'eeg': 400e-6}
ica_icalabel_include = ["brain"]
# ica_exclusion_thresholds = {
#     "brain": 0.7,
#     "muscle artifact": 0.7,
#     "eye blink": 0.7,
#     "heart beat": 0.7,
#     "line noise": 0.7,
#     "channel noise": 0.7,
#     "other": 0.7,
# }

eeg_template_montage = mne.channels.read_dig_fif("analysis/montage/wavenet128_fixed-montage.fif")
eeg_online_reference_channel = "Z7"
drop_channel_after_rereference = True


epochs_tmin = -0.2
epochs_tmax = 0.8
baseline = (-0.2, 0.0)


reject = {"eeg": 150e-6}



# sometimes theres 3 streams recorded so it starts with 3 sometimes 2 sometimes 1 idk why
# sub-001 has 3-1 and 3-2, sub-002 has 2-1 and 2-2, sub-009 has 1-1 and 1-2
rename_events = {
    #"1-1": "kongruent",
    #"1-2": "inkongruent",
    "2-1": "kongruent",
    "2-2": "inkongruent",
    #"3-1": "kongruent", #sometimes theres 3 streams recorded so it starts with 3 sometimes 2 sometimes 1 idk why
    #"3-2": "inkongruent",
}

conditions = ["kongruent", "inkongruent"]

contrasts = [
    ("inkongruent", "kongruent"), 
]


decode = False