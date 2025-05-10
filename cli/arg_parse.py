import argparse


def get_cl_args():
    """
        Получает и возвращает аргументы командной строки для скрипта обработки EDF-файлов.

        Аргументы командной строки:
        -e, --edf : str
            Путь к директории с EDF-файлами. Необязательный аргумент.
            По умолчанию используется путь './eegs'.

        Возвращает:
        argparse.Namespace: Объект с атрибутом 'edf', содержащим путь к директории.

        Пример использования:
            args = get_cl_args()
            print(args.edf)
    """
    parser = argparse.ArgumentParser(description='Обработка EDF-файлов.')
    parser.add_argument('-e', '--edf',
                        type=str,
                        required=False,
                        default='./eegs',
                        help='Путь к директории с EDF-файлами')

    args = parser.parse_args()
    return args
