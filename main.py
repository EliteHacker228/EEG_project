import sys

from cli.arg_parse import get_cl_args
from cli.file_utils import get_edf_files
from edf_processing.criteria_sorting.patients_info import extract_edf_metadata, save_metadata_to_csv
from edf_processing.edf_split.edf_split import edf_split
from edf_processing.preprocessing.edf_preprocess import edf_preprocess


def get_edf_files_list(edf_path):
    try:
        edf_files = get_edf_files(edf_path)
    except Exception as e:
        print(e)
        sys.exit(0)
    return edf_files


def main():
    cl_args = get_cl_args()
    edf_path = cl_args.edf
    edf_files_list = get_edf_files_list(edf_path)

    # I этап - распределение по критериями (сделано всё, кроме % артефактов в записи)
    edf_metadata = extract_edf_metadata(edf_path)
    save_metadata_to_csv(edf_metadata)

    # II этап - предобработка
    edf_preprocess(edf_path)

    # III этап - разделение на блоки
    edf_split('./temp/preprocessed_edf')


if __name__ == "__main__":
    main()
