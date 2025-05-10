-- Создаем базу данных
CREATE DATABASE IF NOT EXISTS eeg_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eeg_system;

-- Таблица для пациентов
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    sex TINYINT NOT NULL CHECK (sex IN (0, 1)),
    age TINYINT NOT NULL CHECK (age >= 0),
    note TEXT
);

-- Таблица для диагнозов
CREATE TABLE diagnosis (
    diag_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    diag_code VARCHAR(100) NOT NULL,
    clinical_data TEXT NOT NULL,
    note TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Таблица для EDF-файлов
CREATE TABLE edf_files (
    edf_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    date DATE NOT NULL,
    eeg_chan TINYINT NOT NULL CHECK (eeg_chan > 0),
    rate FLOAT NOT NULL CHECK (rate > 0),
    montage VARCHAR(255) NOT NULL,
    note TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Таблица для сегментов EDF-файлов
CREATE TABLE segments (
    segment_id INT AUTO_INCREMENT PRIMARY KEY,
    edf_id INT NOT NULL,
    patient_id INT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    left_marker VARCHAR(255) NOT NULL,
    right_marker VARCHAR(255) NOT NULL,
    note TEXT,
    FOREIGN KEY (edf_id) REFERENCES edf_files(edf_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);
