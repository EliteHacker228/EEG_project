from edf_processing.edf_split.split.block_split import create_block_csvs, export_blocks


def edf_split(edf_path):
    input_dir = edf_path
    output_csv_dir = './temp/splitted_blocks/config'
    output_blocks_dir = './temp/splitted_blocks'

    # Вызов функции для создания CSV с блоками по аннотациям
    create_block_csvs(
        input_dir=input_dir,
        output_csv_dir=output_csv_dir,
        skip_labels=["Разрыв записи", "eventBreak", "Артефакт", "stimFlash"]
    )

    # Вызов функции для сохранения блоков по CSV
    export_blocks(
        input_dir=input_dir,
        output_csv_dir=output_csv_dir,
        output_dir=output_blocks_dir
    )

    print('Разбиение на блоки завершено')
