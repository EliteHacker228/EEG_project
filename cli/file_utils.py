import os


def get_edf_files(edf_path):
    """
        Получает список EDF-файлов из указанной директории.

        Проверяет, существует ли путь и является ли он директорией.
        Затем ищет все файлы с расширением .edf (без учета регистра).

        Параметры:
        edf_path : str
            Путь к директории, где предполагается наличие EDF-файлов.

        Возвращает:
        list[str]: Список имён файлов с расширением .edf в указанной директории.

        Исключения:
        Exception: Если путь не существует, не является директорией
                   или не содержит EDF-файлов.

        Пример использования:
            files = get_edf_files('./eegs')
            for f in files:
                print(f)
    """
    if not os.path.exists(edf_path):
        raise Exception(f'Ошибка: путь {edf_path} не существует')

    if not os.path.isdir(edf_path):
        raise Exception(f'Ошибка: путь {edf_path} не является директорией')

    edf_files = [f for f in os.listdir(edf_path) if f.lower().endswith('.edf')]

    if not edf_files:
        raise Exception(f'EDF-файлы не найдены в директории {edf_path}')

    return edf_files
