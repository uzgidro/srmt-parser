import io
import os
import re
from collections import defaultdict

import rarfile
from minio import Minio
import rarfile
# rarfile.UNRAR_TOOL = "unrar"

client = Minio(
    "192.168.40.225:19000",
    access_key="admin",
    secret_key="supersecret",
    secure=False,
)
def ensure_bucket(bucket_name):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

def get_object_name(filepath: str):
    mapping = {
        "Андижон": (2, "Andijon"),
        "ангарон": (5, "Ohangaron"),
        "сорак": (4, "Hisorak"),
        "поланг": (3, "To'palang"),
        "Чорво": (1, "Chorvoq"),
    }

    _, ext = os.path.splitext(filepath)

    for key, (position, name) in mapping.items():
        if key in filepath:
            return f"{position}{name}{ext}"

    return None

def get_required_files_from_rar(rar_file_bytes):
    files_by_folder = defaultdict(list)

    with rarfile.RarFile(rar_file_bytes) as rf:
        for info in rf.infolist():
            filepath = info.filename

            if filepath.endswith('/'):
                continue

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

                filename = f.split('/')[-1]

                match = re.search(r'(\d+)', filename)
                if match:
                    number = int(match.group(1))
                    numbered_files.append((number, f))

            snow_dynamics = None
            if numbered_files:
                snow_dynamics = max(numbered_files, key=lambda x: x[0])[1]

            # загрузка в бакеты
            if snow_cover_file:
                ensure_bucket("modsnow-cover")
                data = rf.read(snow_cover_file)
                object_name = f"{get_object_name(f"{folder}/{snow_cover_file.split('/')[-1]}")}"
                client.put_object(
                    "modsnow-cover",
                    object_name,
                    io.BytesIO(data),
                    length=len(data)
                )

            if snow_dynamics:
                ensure_bucket("modsnow-dynamics")
                data = rf.read(snow_dynamics)
                object_name = f"{get_object_name(f"{folder}/{snow_dynamics.split('/')[-1]}")}"
                client.put_object(
                    "modsnow-dynamics",
                    object_name,
                    io.BytesIO(data),
                    length=len(data)
                )

            result_files[folder] = {
                'snow_cover': snow_cover_file,
                'snow_dynamics': snow_dynamics
            }

    return result_files


print(get_required_files_from_rar('test/arr.rar'))