import os
import mne
import pandas as pd
from datetime import datetime, date

from edf_processing.criteria_sorting.channels_processing.find_bad_channels_lof import find_bad_channels_lof
from edf_processing.criteria_sorting.channels_processing.find_flat_channels import find_flat_channels

mne.set_log_level('WARNING')


def extract_edf_metadata_from_file(edf_path):
    """
    Извлекает метаинформацию из одного EDF-файла.
    Определяет число сбоящих каналов.

    Параметры:
    edf_path : str
        Полный путь к EDF-файлу.

    Возвращает:
    list: Список с метаданными.
    """
    try:
        raw = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
    except Exception as e:
        print(f'Не удалось прочитать файл {edf_path}: {e}')

    edf_file = os.path.basename(edf_path)
    subject_info = raw.info.get('subject_info', {})
    patient_id = subject_info.get('his_id', 'Неизвестно')
    birthday = subject_info.get('birthday')

    meas_date = raw.info.get('meas_date')
    if isinstance(meas_date, tuple):
        meas_date = datetime.fromtimestamp(meas_date[0])
    elif not isinstance(meas_date, datetime):
        meas_date = None

    if isinstance(birthday, date) and meas_date:
        age_at_recording = (meas_date.date() - birthday).days // 365
    else:
        age_at_recording = 'Неизвестно'

    print(f'Информация из файла {edf_file} успешно извлечена')

    # Поиск плохих каналов с помощью find_bad_channels_lof()
    bad_channels_lof = find_bad_channels_lof(raw)

    # Поиск плохих каналов с помощью find_flat_channels()
    flat_channels = find_flat_channels(raw)

    # Объединение обоих списков в один сет (удаляются дубликаты)
    all_bad_channels = set(bad_channels_lof) | set(flat_channels)

    # Преобразуем сет обратно в список
    unique_bad_channels = list(all_bad_channels)

    # TODO: Добавить указание числа артефактов в записи

    return [
        edf_file,
        patient_id,
        birthday if birthday else 'Неизвестно',
        meas_date.date() if meas_date else 'Неизвестно',
        age_at_recording,
        len(unique_bad_channels),
        'NOT_IMPLEMENTED'
    ]


def extract_edf_metadata(edf_folder):
    """
    Обходит директорию и извлекает метаинформацию из всех EDF-файлов.

    Параметры:
    edf_folder : str
        Путь к директории, содержащей EDF-файлы.

    Возвращает:
    list[list]: Список записей по каждому файлу.
    """
    data = []
    for edf_file in os.listdir(edf_folder):
        if edf_file.lower().endswith('.edf'):
            edf_path = os.path.join(edf_folder, edf_file)
            try:
                row = extract_edf_metadata_from_file(edf_path)
            except Exception as e:
                print(e)
                continue
            if row:
                data.append(row)
    return data


def save_metadata_to_csv(data, output_csv='./temp/criteria_sorting/edf_metadata.csv'):
    """
    Сохраняет метаданные EDF-файлов в CSV-файл.

    Параметры:
    data : list[list]
        Список метаданных.
    output_csv : str
        Путь к файлу CSV.
    """
    df = pd.DataFrame(
        data,
        columns=[
            'Название файла',
            'ID пациента',
            'Дата рождения',
            'Дата записи',
            'Возраст на момент записи',
            'Число сбоев в каналах',
            'Процент артефактов в записи'
        ]
    )
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f'Данные сохранены в {output_csv}')
