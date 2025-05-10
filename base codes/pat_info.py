import os
import mne
import pandas as pd
from datetime import datetime, date

edf_folder = "."
output_csv = "output.csv"

data = []

for edf_file in os.listdir(edf_folder):
    if edf_file.endswith(".edf"):
        edf_path = os.path.join(edf_folder, edf_file)
        raw = mne.io.read_raw_edf(edf_path, preload=False)

        subject_info = raw.info.get("subject_info", {})
        patient_id = subject_info.get("his_id", "Неизвестно")
        birthday = subject_info.get("birthday")

        meas_date = raw.info.get("meas_date")
        if isinstance(meas_date, tuple):
            meas_date = datetime.fromtimestamp(meas_date[0])
        elif not isinstance(meas_date, datetime):
            meas_date = None

        if isinstance(birthday, date) and meas_date:
            age_at_recording = (meas_date.date() - birthday).days // 365
        else:
            age_at_recording = "Неизвестно"

        data.append(
            [
                edf_file,
                patient_id,
                birthday if birthday else "Неизвестно",
                meas_date.date() if meas_date else "Неизвестно",
                age_at_recording,
            ]
        )


df = pd.DataFrame(
    data,
    columns=[
        "Название файла",
        "ID пациента",
        "Дата рождения",
        "Дата записи",
        "Возраст на момент записи",
    ],
)
df.to_csv(output_csv, index=False, encoding="utf-8")

print(f"Данные сохранены в {output_csv}")
