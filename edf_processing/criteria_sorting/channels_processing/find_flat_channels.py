import mne
import numpy as np
import os


def find_flat_channels(raw, threshold_std=1e-6, skip_first_minutes=1):
    """
    Функция для нахождения плоских каналов в EDF-файле.

    Параметры:
    file_path : str
        Путь к EDF-файлу.
    threshold_std : float
        Пороговое значение для стандартного отклонения (по умолчанию 1e-6).
    skip_first_minutes : int
        Сколько минут пропустить в начале перед анализом (по умолчанию 1 минута).

    Возвращает:
    list : Список каналов, которые являются плоскими.
    """
    # Загрузка данных
    data = raw.get_data()
    sfreq = raw.info['sfreq']  # частота дискретизации
    start_sample = int(sfreq * 60 * skip_first_minutes)

    # Поиск плоских каналов
    flat_channels = []
    for idx, signal in enumerate(data):
        channel_name = raw.ch_names[idx]

        # Игнорируем канал ECG ECG
        if channel_name == "ECG  ECG":
            continue

        segment = signal[start_sample:]
        std_value = np.std(segment)
        if std_value < threshold_std:
            flat_channels.append(raw.ch_names[idx])

    return flat_channels
