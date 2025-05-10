import mne
import csv
import os


# Функция для преобразования времени в формат MM:SS.mmm
def seconds_to_min_sec_ms(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{minutes:02}:{secs:02}.{milliseconds:03}"


# Директория с .edf файлами
input_dir = "."  # Папка с файлами .edf
output_dir = "output_csv"  # Папка для результатов в формате CSV

# Создаем папку для выходных CSV файлов
os.makedirs(output_dir, exist_ok=True)

# Аннотации, которые нужно пропускать
skip_labels = ["Разрыв записи", "eventBreak", "Артефакт", "stimFlash"]

# Проходим по всем .edf файлам в папке
for filename in os.listdir(input_dir):
    if filename.endswith(".edf"):
        edf_file = os.path.join(input_dir, filename)
        raw = mne.io.read_raw_edf(edf_file, preload=True)

        # Обрезка всего файла на 5 секунд
        duration = raw.times[-1]
        raw = raw.copy().crop(tmin=5.0, tmax=duration - 5.0)

        annotations = raw.annotations
        onsets = annotations.onset
        descriptions = annotations.description
        total_duration = raw.times[-1]

        blocks = []
        i = 0

        # Поиск блоков и их извлечение
        while i < len(descriptions):
            desc = descriptions[i]

            if any(skip_word.lower() in desc.lower() for skip_word in skip_labels):
                i += 1
                continue

            start = onsets[i]

            # Ищем следующую хорошую аннотацию
            j = i + 1
            while j < len(descriptions):
                next_desc = descriptions[j]
                if any(
                    skip_word.lower() in next_desc.lower() for skip_word in skip_labels
                ):
                    j += 1
                else:
                    break

            end = onsets[j] if j < len(onsets) else total_duration
            block_duration = end - start

            blocks.append((desc, start, block_duration))
            i = j

        # Получаем имя файла без расширения
        base_filename = os.path.splitext(filename)[0]

        # Сохраняем данные в CSV для каждого файла
        csv_output_path = os.path.join(output_dir, f"{base_filename}_blocks.csv")
        with open(csv_output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Название", "Время начала", "Длительность"])
            for name, start, duration in blocks:
                writer.writerow(
                    [
                        name,
                        seconds_to_min_sec_ms(start),
                        seconds_to_min_sec_ms(duration),
                    ]
                )

        print(f"Блоки для файла {filename} сохранены в {csv_output_path}")
