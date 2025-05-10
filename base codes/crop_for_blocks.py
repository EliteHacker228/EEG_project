import mne
import csv
import os


# Функция для преобразования времени из MM:SS.mmm в секунды
def time_str_to_seconds(time_str):
    minutes, rest = time_str.split(":")
    seconds, milliseconds = rest.split(".")
    return int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000


# Директория с .edf файлами
input_dir = "."  # Папка с файлами .edf
output_csv_dir = "output_csv"  # Папка для CSV файлов
output_dir = "splitted_blocks"  # Папка для сохранения разделённых блоков

# Создаем папки для CSV и блоков
os.makedirs(output_csv_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Проходим по всем .edf файлам в папке
for filename in os.listdir(input_dir):
    if filename.endswith(".edf"):
        edf_file = os.path.join(input_dir, filename)
        raw = mne.io.read_raw_edf(edf_file, preload=True)

        # Получаем имя файла без расширения
        base_filename = os.path.splitext(filename)[0]

        # Читаем блоки из CSV, связанного с текущим файлом
        csv_file = os.path.join(output_csv_dir, f"{base_filename}_blocks.csv")

        if not os.path.exists(csv_file):
            print(f"CSV файл для {filename} не найден.")
            continue

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Создаем папку для текущего файла
            file_output_dir = os.path.join(output_dir, base_filename)
            os.makedirs(file_output_dir, exist_ok=True)

            for i, row in enumerate(reader):
                block_name = row["Название"]
                start_sec = time_str_to_seconds(row["Время начала"])
                duration_sec = time_str_to_seconds(row["Длительность"])
                end_sec = start_sec + duration_sec

                # Вырезаем блок из общего raw
                raw_block = raw.copy().crop(tmin=start_sec, tmax=end_sec)

                # Формируем имя файла с нумерацией и названием исходного edf файла
                safe_name = (
                    block_name.replace(" ", "_").replace("(", "").replace(")", "")
                )
                out_path = os.path.join(
                    file_output_dir, f"{i+1:02d}_block_{base_filename}.edf"
                )

                # Сохраняем блок в отдельный файл
                raw_block.export(out_path, fmt="edf", physical_range="auto")
                print(f"Сохранен блок: {out_path}")
