import mne

# Загружаем данные
edf_file = "101172.edf"
raw = mne.io.read_raw_edf(edf_file, preload=True)

# Обрезаем данные: первые 5 секунд и последние 5 секунд
duration = raw.times[-1]  # Последнее время в данных
raw = raw.copy().crop(tmin=5.0, tmax=duration - 5.0)
