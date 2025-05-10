import mne
import numpy as np


def min_max_normalisation(raw):
    """
    Нормализует данные EEG по каждому каналу в диапазон [0, 1], исключает ECG перед нормализацией и добавляет обратно после.

    Параметры:
    - raw: исходный объект MNE Raw

    Возвращает:
    - Новый объект MNE Raw с нормализованными данными и сохранёнными аннотациями
    """
    # Сохраняем аннотации
    original_annotations = raw.annotations.copy()

    # Выделяем ECG-канал и удаляем его из основного потока
    if 'ECG  ECG' in raw.ch_names:
        ecg_channel = raw.copy().pick_channels(['ECG  ECG'])
        raw = raw.copy().drop_channels(['ECG  ECG'])
    else:
        ecg_channel = None

    # Получаем данные и нормализуем каждый канал
    data_by_channels = raw.get_data()
    normalised_data = []
    for data_by_channel in data_by_channels:
        min_val = data_by_channel.min()
        max_val = data_by_channel.max()
        if max_val == min_val:
            raise ZeroDivisionError("Один из каналов имеет нулевой диапазон значений.")
        normalized = (data_by_channel - min_val) / (max_val - min_val)
        normalised_data.append(normalized)
    normalised_data = np.array(normalised_data)

    # Создаём новый объект Raw с нормализованными данными
    info = raw.info.copy()
    for ch in info['chs']:
        ch['kind'] = mne.io.constants.FIFF.FIFFV_MISC_CH
        ch['unit'] = mne.io.constants.FIFF.FIFF_UNIT_NONE
    normalized_raw = mne.io.RawArray(normalised_data, info)

    # Возвращаем ECG, если он был
    if ecg_channel is not None:
        normalized_raw.add_channels([ecg_channel])

    # Восстанавливаем аннотации
    normalized_raw.set_annotations(original_annotations)

    return normalized_raw
