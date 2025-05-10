import mne
from mne.preprocessing import ICA, annotate_amplitude
import pandas as pd

# Загрузка данных
raw = mne.io.read_raw_edf('238217.edf', preload=True)

# 1. Предварительная обработка данных
# Фильтрация данных (полосовой фильтр 1–40 Гц)
raw.filter(1, 40)

# Установка общего среднего референса
raw.set_eeg_reference('average', projection=False)

# 2. Обнаружение артефактов с помощью annotate_amplitude
# Пороговый метод для обнаружения артефактов по амплитуде и плоских участков
annotations, bad_channels = annotate_amplitude(
    raw,
    peak=200e-6,  # Порог амплитуды (200 µV)
    flat=5e-6,    # Порог для обнаружения плоских участков (5 µV)
    bad_percent=5,  # Процент времени для пометки канала как плохого
    min_duration=0.005  # Минимальная длительность артефакта (5 мс)
)

# Добавление аннотаций к данным
raw.set_annotations(annotations)

# Вывод плохих каналов
print(f"Плохие каналы (по амплитуде): {bad_channels}")

# 3. Сохранение результатов в CSV-файл (UTF-8)
# Подсчет количества артефактов и плохих каналов
n_artifacts = len(annotations)  # Количество артефактов
n_bad_channels = len(bad_channels)  # Количество плохих каналов

# Создание DataFrame для сохранения результатов
results = {
    'Количество артефактов': [n_artifacts],
    'Плохие каналы': [', '.join(bad_channels)],  # Преобразуем список в строку
    'Количество плохих каналов': [n_bad_channels]
}

df = pd.DataFrame(results)

# Сохранение в CSV-файл с кодировкой UTF-8
df.to_csv('artifacts_report.csv', index=False, encoding='utf-8')

print("Анализ завершен. Результаты сохранены в файл 'artifacts_report.csv'.")