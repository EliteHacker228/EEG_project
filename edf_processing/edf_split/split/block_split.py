import os
import csv
import mne


def seconds_to_min_sec_ms(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{minutes:02}:{secs:02}.{milliseconds:03}"


def time_str_to_seconds(time_str):
    minutes, rest = time_str.split(":")
    seconds, milliseconds = rest.split(".")
    return int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000


def create_block_csvs(input_dir=".", output_csv_dir="output_csv", skip_labels=None):
    if skip_labels is None:
        skip_labels = ["Разрыв записи", "eventBreak", "Артефакт", "stimFlash"]

    os.makedirs(output_csv_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.endswith(".edf"):
            continue

        edf_file = os.path.join(input_dir, filename)
        raw = mne.io.read_raw_edf(edf_file, preload=True)

        # Обрезка по 5 секунд с начала и конца
        raw.crop(tmin=5.0, tmax=raw.times[-1] - 5.0)

        annotations = raw.annotations
        onsets = annotations.onset
        descriptions = annotations.description
        total_duration = raw.times[-1]

        blocks = []
        i = 0
        while i < len(descriptions):
            desc = descriptions[i]
            if any(skip_word.lower() in desc.lower() for skip_word in skip_labels):
                i += 1
                continue

            start = onsets[i]
            j = i + 1
            while j < len(descriptions):
                next_desc = descriptions[j]
                if any(skip_word.lower() in next_desc.lower() for skip_word in skip_labels):
                    j += 1
                else:
                    break

            end = onsets[j] if j < len(onsets) else total_duration
            duration = end - start

            blocks.append((desc, start, duration))
            i = j

        base_filename = os.path.splitext(filename)[0]
        csv_path = os.path.join(output_csv_dir, f"{base_filename}_blocks.csv")

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Название", "Время начала", "Длительность"])
            for name, start, duration in blocks:
                writer.writerow([
                    name,
                    seconds_to_min_sec_ms(start),
                    seconds_to_min_sec_ms(duration),
                ])

        print(f"CSV создан: {csv_path}")


def export_blocks(input_dir=".", output_csv_dir="output_csv", output_dir="splitted_blocks"):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.endswith(".edf"):
            continue

        edf_file = os.path.join(input_dir, filename)
        raw = mne.io.read_raw_edf(edf_file, preload=True)
        base_filename = os.path.splitext(filename)[0]
        csv_file = os.path.join(output_csv_dir, f"{base_filename}_blocks.csv")

        if not os.path.exists(csv_file):
            print(f"Пропущен (нет CSV): {filename}")
            continue

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            file_output_dir = os.path.join(output_dir, base_filename)
            os.makedirs(file_output_dir, exist_ok=True)

            for i, row in enumerate(reader):
                block_name = row["Название"]
                start_sec = time_str_to_seconds(row["Время начала"])
                duration_sec = time_str_to_seconds(row["Длительность"])
                end_sec = start_sec + duration_sec

                raw_block = raw.copy().crop(tmin=start_sec, tmax=end_sec)
                safe_name = block_name.replace(" ", "_").replace("(", "").replace(")", "")
                out_path = os.path.join(file_output_dir, f"{i+1:02d}_{safe_name}_{base_filename}.edf")

                raw_block.export(out_path, fmt="edf", physical_range="auto")
                print(f"Сохранён блок: {out_path}")
