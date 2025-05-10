import mne
import numpy as np
from spkit.eeg import ATAR
from edf_utils.montage_manager import MontageManager


def atar_3_sigma_filter(raw):
    """
    Функция для предварительной обработки ЭЭГ данных: удаления артефактов, фильтрации, сегментации и применения ATAR.

    Parameters:
    raw (mne.io.Raw): объект MNE, содержащий необработанные ЭЭГ данные.

    Returns:
    mne.io.Raw: очищенные ЭЭГ данные.
    """

    # Удаляем канал ECG, если он есть
    if "ECG  ECG" in raw.ch_names:
        raw.drop_channels(["ECG  ECG"])
        # print("Канал ECG удален.")

    # === Применение монтажа ===
    num_channels = len(raw.ch_names)
    montage = MontageManager.get_montage(num_channels)

    if montage:
        raw.set_montage(montage)
        # print("Монтаж успешно применен.")
    else:
        pass
        # print("Монтаж не применен: неподходящее количество каналов.")

    # Повторное применение монтажа (на всякий случай)
    raw.set_montage(montage)

    # === Фильтрация данных ===
    low_cut = 0.1
    hi_cut = 70.0
    raw_filtered = raw.copy().filter(low_cut, hi_cut)

    # === Аннотации и события ===
    original_annotations = raw.annotations.copy()
    events, titles = mne.events_from_annotations(raw)
    blacklist_titles = ['stimFlash']
    whitelist_numbers = [eid for title, eid in titles.items() if title not in blacklist_titles]

    events_mask = np.isin(events[:, -1], whitelist_numbers)
    clear_events = events[events_mask]

    # === Сегментация данных ===
    event_times = raw.times[clear_events[:, 0]]
    event_times = np.append(event_times, raw.times[-1])
    event_times = np.insert(event_times, 0, raw.times[0])

    segments = []
    sfreq = raw_filtered.info['sfreq']

    for i in range(len(event_times) - 1):
        start = event_times[i]
        end = event_times[i + 1]

        segment = raw_filtered.copy().crop(tmin=start, tmax=end)
        data = segment.get_data()
        mean = np.mean(data, axis=1, keepdims=True)
        std = np.std(data, axis=1, keepdims=True)

        # 3-сигма фильтрация
        mask = np.abs(data - mean) > 3 * std
        data[mask] = np.broadcast_to(mean, data.shape)[mask]

        # Интерполяция по времени
        for ch in range(data.shape[0]):
            bad_idx = np.where(mask[ch])[0]
            good_idx = np.where(~mask[ch])[0]
            if len(good_idx) >= 2:
                data[ch, bad_idx] = np.interp(bad_idx, good_idx, data[ch, good_idx])

        # === Детекция глобального артефакта и ATAR ===
        window_size_sec = 1
        window_size = int(sfreq * window_size_sec)
        n_windows = data.shape[1] // window_size
        threshold_uV = 100
        min_channels_with_artifact = int(0.8 * data.shape[0])
        data_cleaned = data.copy()

        for w in range(n_windows):
            start_idx = w * window_size
            end_idx = start_idx + window_size
            artifact_flags = []

            for ch in range(data.shape[0]):
                segment_uV = data[ch, start_idx:end_idx] * 1e6
                if np.max(np.abs(segment_uV)) > threshold_uV:
                    artifact_flags.append(True)
                else:
                    artifact_flags.append(False)

            if sum(artifact_flags) >= min_channels_with_artifact:
                # print(
                #     f"[Сегмент {i + 1}/{len(event_times) - 1}, окно {w + 1}/{n_windows}] Глобальный артефакт обнаружен. Применяется ATAR.")
                for ch in range(data.shape[0]):
                    x = data[ch, start_idx:end_idx] * 1e6
                    x_cleaned = ATAR(x, wv='db4', winsize=128, beta=0.1,
                                     thr_method='ipr', OptMode='soft', verbose=0)
                    data_cleaned[ch, start_idx:end_idx] = x_cleaned / 1e6
            else:
                pass
                # print(
                #     f"[Сегмент {i + 1}/{len(event_times) - 1}, окно {w + 1}/{n_windows}] Глобальный артефакт не обнаружен. Пропуск.")

        cleaned = mne.io.RawArray(data_cleaned, segment.info)
        segments.append(cleaned)

    # === Объединение сегментов ===
    raw_combined = mne.concatenate_raws(segments)

    # === Сдвигаем аннотации обратно ===
    shifted_annotations = original_annotations.copy()
    raw_combined.set_annotations(shifted_annotations)

    # === Возвращаем очищенные данные ===
    return raw_combined
