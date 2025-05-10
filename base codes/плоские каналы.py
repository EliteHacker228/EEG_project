import mne
import numpy as np
import os

# === Настройки ===
file_path = '101172.edf'  # <-- сюда путь к твоему EDF-файлу
threshold_std = 1e-6         # Порог для определения "плоского" сигнала
skip_first_minutes = 1       # Сколько минут пропускать перед анализом

# === Загрузка файла ===
raw = mne.io.read_raw_edf(file_path, preload=True)
data = raw.get_data()
sfreq = raw.info['sfreq']  # частота дискретизации
start_sample = int(sfreq * 60 * skip_first_minutes)

# === Словарь симметричных каналов под твои имена ===
symmetric_channels = {
    'EEG FP1-A1': 'EEG FP2-A2', 'EEG FP2-A2': 'EEG FP1-A1',
    'EEG F7-A1': 'EEG F8-A2', 'EEG F8-A2': 'EEG F7-A1',
    'EEG F3-A1': 'EEG F4-A2', 'EEG F4-A2': 'EEG F3-A1',
    'EEG T3-A1': 'EEG T4-A2', 'EEG T4-A2': 'EEG T3-A1',
    'EEG C3-A1': 'EEG C4-A2', 'EEG C4-A2': 'EEG C3-A1',
    'EEG T5-A1': 'EEG T6-A2', 'EEG T6-A2': 'EEG T5-A1',
    'EEG P3-A1': 'EEG P4-A2', 'EEG P4-A2': 'EEG P3-A1',
    'EEG O1-A1': 'EEG O2-A2', 'EEG O2-A2': 'EEG O1-A1',
    'EEG FZ-A2': 'EEG FZ-A2',  # срединные оставляем как есть
    'EEG CZ-A1': 'EEG CZ-A1',
    'EEG PZ-A2': 'EEG PZ-A2'
}

# === Поиск плоских каналов ===
flat_channels = []

for idx, signal in enumerate(data):
    segment = signal[start_sample:]
    std_value = np.std(segment)
    if std_value < threshold_std:
        flat_channels.append(raw.ch_names[idx])
        print(f"Канал {raw.ch_names[idx]} помечен как плоский после {skip_first_minutes} минут (std = {std_value})")

if not flat_channels:
    print("Плоских каналов не найдено.")
else:
    print("Найдены плоские каналы:", flat_channels)

# === Замена плоских каналов на симметричные ===
for channel in flat_channels:
    if channel in symmetric_channels:
        replacement = symmetric_channels[channel]
        if replacement in raw.ch_names:
            print(f"Заменяем {channel} на сигнал с {replacement}")
            bad_idx = raw.ch_names.index(channel)
            replacement_idx = raw.ch_names.index(replacement)
            data[bad_idx] = data[replacement_idx]
        else:
            print(f"Симметричный канал {replacement} не найден для {channel}.")
    else:
        print(f"Для канала {channel} не задан симметричный аналог!")

# === Применяем изменённые данные ===
raw._data = data

# === Генерация нового имени файла ===
base_name = 'corrected_file'
counter = 1
output_file = f"{base_name}_{counter}.edf"

while os.path.exists(output_file):
    counter += 1
    output_file = f"{base_name}_{counter}.edf"

# === Сохранение файла ===
raw.export(output_file, fmt='auto')
print(f"Исправленный файл сохранён как: {output_file}")
