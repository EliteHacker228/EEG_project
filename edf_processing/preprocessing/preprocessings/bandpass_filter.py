def bandpass_filter(raw):
    """
    Применяет полосовой фильтр к данным EEG, сохраняя аннотации.

    Возвращает:
    - Отфильтрованный объект Raw с сохранёнными аннотациями
    """
    annotations = raw.annotations.copy()
    raw_filtered = raw.copy().filter(l_freq=1, h_freq=40)
    raw_filtered.set_annotations(annotations)
    return raw_filtered
