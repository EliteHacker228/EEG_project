import mne
import numpy as np

raw = mne.io.read_raw_edf("./EEG/085574.edf", preload=True)

original_annotations = raw.annotations.copy()

ecg_channel = raw.copy().pick_channels(['ECG  ECG'])
raw.drop_channels('ECG  ECG')

data_by_channels = raw.get_data()
normalised_data = []
for data_by_channel in data_by_channels:
    min_val = data_by_channel.min()
    max_val = data_by_channel.max()
    range_val = max_val - min_val
    if max_val - min_val == 0:
        raise ZeroDivisionError
    normalised_data_by_channel = ((data_by_channel - min_val) / (max_val - min_val))
    normalised_data.append(normalised_data_by_channel)
normalised_data = np.array(normalised_data)

info = raw.info.copy()
for ch in info['chs']:
    ch['kind'] = mne.io.constants.FIFF.FIFFV_MISC_CH
    ch['unit'] = mne.io.constants.FIFF.FIFF_UNIT_NONE

normalized_raw = mne.io.RawArray(normalised_data, info)
normalized_raw.add_channels([ecg_channel])

normalized_raw.set_annotations(original_annotations)

normalized_raw.export("normalized_anno.edf", fmt="edf")