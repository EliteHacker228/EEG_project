from eeg_database import EEGDatabase  # Импортируй свой класс сюда
from connection_data import connection_data
import random


def test_eeg_database():
    db = EEGDatabase(**connection_data)

    try:
        print("\n--- Добавляем пациентов ---")
        db.add_patient(sex=0, age=25, note="Test Patient 1")
        db.add_patient(sex=1, age=30, note="Test Patient 2")
        db.add_patient(sex=1, age=45, note="Test Patient 3")

        patients = [db.get_patient(i) for i in range(1, 4)]
        for p in patients:
            print(p)

        print("\n--- Обновляем одного пациента ---")
        db.update_patient(patient_id=1, sex=1, age=26, note="Updated Patient 1")
        updated_patient = db.get_patient(1)
        print(updated_patient)

        print("\n--- Добавляем диагнозы ---")
        db.add_diagnosis(patient_id=1, diag_code="G40", clinical_data="Epilepsy", note="Note1")
        db.add_diagnosis(patient_id=2, diag_code="G41", clinical_data="Seizure", note="Note2")

        diagnoses = db.get_diagnoses_by_patient(1)
        print(diagnoses)

        print("\n--- Добавляем EDF-файлы ---")
        db.add_edf_file(patient_id=1, date="2024-01-01", eeg_chan=19, rate=256.0, montage="Montage1", note="EDF1")
        db.add_edf_file(patient_id=2, date="2024-01-02", eeg_chan=21, rate=512.0, montage="Montage2", note="EDF2")

        edf_files_1 = db.get_edf_files_by_patient(1)
        edf_files_2 = db.get_edf_files_by_patient(2)
        print(edf_files_1)
        print(edf_files_2)

        edf_id_1 = edf_files_1[0]['edf_id']
        edf_id_2 = edf_files_2[0]['edf_id']

        print("\n--- Добавляем сегменты ---")
        db.add_segment(edf_id=edf_id_1, patient_id=1, start_time="00:00:00", end_time="00:01:00", left_marker="Start",
                       right_marker="End", note="Segment1")
        db.add_segment(edf_id=edf_id_2, patient_id=2, start_time="00:05:00", end_time="00:06:00", left_marker="Start",
                       right_marker="End", note="Segment2")

        segments_1 = db.get_segments_by_edf(edf_id_1)
        segments_2 = db.get_segments_by_edf(edf_id_2)
        print(segments_1)
        print(segments_2)

        print("\n--- Удаляем одного пациента и смотрим каскадное удаление ---")
        db.delete_patient(patient_id=3)  # удаляем пациента 3 (и всё, что связано, если бы было)

        remaining_patients = [db.get_patient(i) for i in range(1, 4) if db.get_patient(i) is not None]
        print("Оставшиеся пациенты:", remaining_patients)

        remaining_diagnoses = db.get_diagnoses_by_patient(1) + db.get_diagnoses_by_patient(2)
        print("Оставшиеся диагнозы:", remaining_diagnoses)

        remaining_edfs = db.get_edf_files_by_patient(1) + db.get_edf_files_by_patient(2)
        print("Оставшиеся EDF-файлы:", remaining_edfs)

        print("\n✅ Тест завершен успешно!")

    except Exception as e:
        print("\n❌ Ошибка в тесте:", e)

    finally:
        db.close()


if __name__ == "__main__":
    test_eeg_database()
