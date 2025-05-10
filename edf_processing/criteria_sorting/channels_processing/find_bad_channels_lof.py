import mne


def find_bad_channels_lof(raw):
    return mne.preprocessing.find_bad_channels_lof(raw, picks='all', n_neighbors=15)
