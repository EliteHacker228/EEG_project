import os

import mne

from edf_processing.preprocessing.preprocessings.atar_3_sigma_filter import atar_3_sigma_filter
from edf_processing.preprocessing.preprocessings.bandpass_filter import bandpass_filter
from edf_processing.preprocessing.preprocessings.min_max_normalisation import min_max_normalisation


def edf_preprocess(edf_folder, output_folder='./temp/preprocessed_edf'):
    for edf_file in os.listdir(edf_folder):
        if edf_file.lower().endswith('.edf'):
            edf_path = os.path.join(edf_folder, edf_file)
            raw = mne.io.read_raw_edf(edf_path, preload=True)

            preprocessed_raw = preprocess_raw(raw)

            output_path = os.path.join(output_folder, edf_file)
            preprocessed_raw.export(output_path, fmt="edf", overwrite=True)
            print(f"Файл {edf_file} предобработан и сохранён: {output_path}")


def preprocess_raw(raw):
    # 1. Обрезание концов
    # Обрезаем данные: первые 5 секунд и последние 5 секунд
    duration = raw.times[-1]  # Последнее время в данных
    preprocessed_raw = raw.copy().crop(tmin=5.0, tmax=duration - 5.0)

    # Удаление артефактов (atar + 3sigma, ICA)
    preprocessed_raw = atar_3_sigma_filter(preprocessed_raw)

    # Полосовой фильтр
    preprocessed_raw = bandpass_filter(preprocessed_raw)

    # Мин-макс нормализация
    preprocessed_raw = min_max_normalisation(preprocessed_raw)

    return preprocessed_raw
