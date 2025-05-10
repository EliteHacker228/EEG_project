import mne
import os

edf_folder = "."  # Укажи свою папку с edf-файлами
unique_annotations = set()

for filename in os.listdir(edf_folder):
    if filename.endswith(".edf"):
        filepath = os.path.join(edf_folder, filename)
        try:
            raw = mne.io.read_raw_edf(filepath, preload=False, verbose=False)
            descriptions = raw.annotations.description
            unique_annotations.update(descriptions)
        except Exception as e:
            print(f"Ошибка при чтении {filename}: {e}")

# Сортируем и выводим
unique_annotations = sorted(unique_annotations)
# print("Найденные уникальные аннотации:")
# for ann in unique_annotations:
#     print(f"- {ann}")

# Сохраняем в файл
with open("all_unique_annotations.txt", "w", encoding="utf-8") as f:
    for ann in unique_annotations:
        f.write(ann + "\n")

print("Уникальные аннотации сохранены в all_unique_annotations.txt")
