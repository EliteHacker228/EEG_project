import mne
from autoreject import AutoReject
from montage_manager import MontageManager

# Загружаем данные
edf_file = "004181.edf"
raw = mne.io.read_raw_edf(edf_file, preload=True)
raw.crop(tmax=60.0)

# Удаление канала ECG, если он присутствует
if "ECG  ECG" in raw.ch_names:
    raw.drop_channels(["ECG  ECG"])
    print("Канал ECG удален.")

# Получаем монтаж в зависимости от количества каналов
num_channels = len(raw.ch_names)

montage = MontageManager.get_montage(num_channels)
if montage:
    # Применяем монтаж
    raw.set_montage(montage)
    print("Монтаж успешно применен.")

    # Визуализируем монтаж в 3D
    fig = mne.viz.plot_montage(
        montage,
        kind="topomap",
        show_names=True,  # Показать названия каналов
        sphere="auto",  # Автоматически подберет параметры сферы
        scale=1.2,  # Увеличим размер точек для улучшения видимости
    )
else:
    print("Монтаж не применен: неподходящее количество каналов.")

# Добавляем стандартную разметку для ЭЭГ (система 10-20)
# montage = mne.channels.make_standard_montage('standard_1020')  # Для ЭЭГ можно использовать 'standard_1020'
raw.set_montage(montage)

# Фильтруем данные (0.1–40 Гц)
ica_low_cut = 1.0  # Для ICA, мы исключаем больше низкочастотного сигнала
hi_cut = 30

raw_ica = raw.copy().filter(ica_low_cut, hi_cut)

# Разделяем данные на эпохи по 1 секунде
tstep = 1.0
events_ica = mne.make_fixed_length_events(raw_ica, duration=tstep)
epochs_ica = mne.Epochs(
    raw_ica, events_ica, tmin=0.0, tmax=tstep, baseline=None, preload=True
)

# Применяем AutoReject
ar = AutoReject(
    n_interpolate=[1, 2, 4],
    random_state=42,
    picks=mne.pick_types(
        epochs_ica.info,
        eeg=True,
    ),
    n_jobs=-1,
    verbose=False,
)

ar.fit(epochs_ica)

# Получаем лог отклонений
reject_log = ar.get_reject_log(epochs_ica)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=[15, 5])
reject_log.plot("horizontal", ax=ax, aspect="auto")
plt.show()
