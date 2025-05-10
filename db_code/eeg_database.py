import pymysql
from typing import Optional, List, Dict

class EEGDatabase:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def execute(self, query: str, params: Optional[tuple] = None, fetch: bool = False):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
                return result
            self.conn.commit()

    def close(self):
        self.conn.close()

    # Работа с пациентами
    def add_patient(self, sex: int, age: int, note: Optional[str] = None):
        query = "INSERT INTO patients (sex, age, note) VALUES (%s, %s, %s)"
        self.execute(query, (sex, age, note))

    def get_patient(self, patient_id: int) -> Optional[Dict]:
        query = "SELECT * FROM patients WHERE patient_id = %s"
        result = self.execute(query, (patient_id,), fetch=True)
        return result[0] if result else None

    def update_patient(self, patient_id: int, sex: int, age: int, note: Optional[str]):
        query = "UPDATE patients SET sex=%s, age=%s, note=%s WHERE patient_id=%s"
        self.execute(query, (sex, age, note, patient_id))

    def delete_patient(self, patient_id: int):
        query = "DELETE FROM patients WHERE patient_id = %s"
        self.execute(query, (patient_id,))

    # Работа с диагнозами
    def add_diagnosis(self, patient_id: int, diag_code: str, clinical_data: str, note: Optional[str] = None):
        query = "INSERT INTO diagnosis (patient_id, diag_code, clinical_data, note) VALUES (%s, %s, %s, %s)"
        self.execute(query, (patient_id, diag_code, clinical_data, note))

    def get_diagnoses_by_patient(self, patient_id: int) -> List[Dict]:
        query = "SELECT * FROM diagnosis WHERE patient_id = %s"
        return self.execute(query, (patient_id,), fetch=True)

    # Работа с EDF-файлами
    def add_edf_file(self, patient_id: int, date: str, eeg_chan: int, rate: float, montage: str, note: Optional[str] = None):
        query = """INSERT INTO edf_files (patient_id, date, eeg_chan, rate, montage, note) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        self.execute(query, (patient_id, date, eeg_chan, rate, montage, note))

    def get_edf_files_by_patient(self, patient_id: int) -> List[Dict]:
        query = "SELECT * FROM edf_files WHERE patient_id = %s"
        return self.execute(query, (patient_id,), fetch=True)

    # Работа с сегментами
    def add_segment(self, edf_id: int, patient_id: int, start_time: str, end_time: str, left_marker: str, right_marker: str, note: Optional[str] = None):
        query = """INSERT INTO segments (edf_id, patient_id, start_time, end_time, left_marker, right_marker, note) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        self.execute(query, (edf_id, patient_id, start_time, end_time, left_marker, right_marker, note))

    def get_segments_by_edf(self, edf_id: int) -> List[Dict]:
        query = "SELECT * FROM segments WHERE edf_id = %s"
        return self.execute(query, (edf_id,), fetch=True)
