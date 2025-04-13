import mne.io
import numpy as np

raw = mne.io.read_raw_edf("./EEG/085574.edf", preload=True)
raw.pick_types(eeg=True)

CROP_SPAN = 3
duration = raw.times[-1]
raw.crop(tmin=CROP_SPAN, tmax=duration - CROP_SPAN)

original_annotations = raw.annotations.copy()
events, titles = mne.events_from_annotations(raw)

# 1 - это stimflash event, его учитывать при разбиении нет смысла
blacklist_titles = ['stimFlash']
blacklist_numbers = []

whitelist_titles = []
whitelist_numbers = []

for title in titles:
    event_id = titles[title]
    if title in blacklist_titles:
        continue
    else:
        whitelist_numbers.append(event_id)
        whitelist_titles.append(title)

events_mask = np.isin(events[:, -1], whitelist_numbers)
clear_events = events[events_mask]

event_times = raw.times[clear_events[:, 0]]
event_times = np.append(event_times, raw.times[-1])
event_times = np.insert(event_times, 0, raw.times[0])

segments = []

for i in range(len(event_times) - 1):
    start = event_times[i]
    end = event_times[i + 1]

    segment = raw.copy().crop(tmin=start, tmax=end)

    data = segment.get_data()
    mean = np.mean(data, axis=1, keepdims=True)
    std = np.std(data, axis=1, keepdims=True)
    mask = np.abs(data - mean) > 3 * std
    data[mask] = np.broadcast_to(mean, data.shape)[mask]

    # Интерполяция по времени для каждого канала отдельно
    for ch in range(data.shape[0]):
        bad_idx = np.where(mask[ch])[0]
        good_idx = np.where(~mask[ch])[0]

        if len(good_idx) < 2:
            continue  # нечего интерполировать

        data[ch, bad_idx] = np.interp(
            bad_idx,
            good_idx,
            data[ch, good_idx]
        )

    cleaned = mne.io.RawArray(data, segment.info)
    segments.append(cleaned)

raw_combined = mne.concatenate_raws(segments)
shifted_annotations = original_annotations.copy()
shifted_annotations.onset -= CROP_SPAN
raw_combined.set_annotations(shifted_annotations)
raw_combined.export("cleaned_with_sigma_filter", fmt="edf")