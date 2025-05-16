import rarfile
import re
from datetime import datetime
from collections import defaultdict

def get_required_files_from_rar(rar_path):
    files_by_folder = defaultdict(list)

    with rarfile.RarFile(rar_path) as rf:
        for info in rf.infolist():
            filepath = info.filename

            # Пропускаем папки
            if filepath.endswith('/'):
                continue

            # Проверка на нужное имя папки
            if ("Андижон" in filepath or
                "ангарон" in filepath or
                "Сардоба" in filepath or
                "сорак" in filepath or
                "поланг" in filepath or
                "Чорво" in filepath):

                folder = filepath.rsplit('/', 1)[0] if '/' in filepath else ''
                files_by_folder[folder].append(filepath)

    result_files = {}

    for folder, files in files_by_folder.items():
        snow_cover_file = None
        numbered_files = []

        for f in files:
            if 'snow_cover' in f.lower():
                snow_cover_file = f

            match = re.search(r'(\d+)\.', f.split('/')[-1])
            if match:
                number = int(match.group(1))
                numbered_files.append((number, f))

        max_number_file = None
        if numbered_files:
            max_number_file = max(numbered_files, key=lambda x: x[0])[1]

        result_files[folder] = {
            'snow_cover': snow_cover_file,
            'max_number_file': max_number_file
        }

    return result_files


rar_path = 'arr.rar'
result = get_required_files_from_rar(rar_path)

for folder, files in result.items():
    print(f"\nПапка: {folder}")
    print(f"  snow_cover файл: {files['snow_cover']}")
    print(f"  max number файл: {files['max_number_file']}")