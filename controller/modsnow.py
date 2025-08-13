import asyncio
import io
import traceback

import pandas as pd
import pdfplumber

from config import MODSNOW_FORWARD_URL
from service.forwarder import forward_data
from service.modsnow import Modsnow


def process(filename: str, contents: bytes):
    table_data = []
    try:
        if filename.endswith('.pdf'):
            pdf_file = io.BytesIO(contents)
            with pdfplumber.open(pdf_file) as pdf:
                raw_table = pdf.pages[0].extract_tables()[0]
                for index, row in enumerate(raw_table):
                    if row and row[0] and str(row[0]).strip() == "1":
                        table_data = raw_table[index:]
                        break
        elif filename.endswith('.xlsx'):
            excel_file = io.BytesIO(contents)
            all_sheets_dfs = pd.read_excel(excel_file, sheet_name=None, header=None)

            aggregated_data = []
            # Проходим по каждому листу в файле
            for sheet_name, df in all_sheets_dfs.items():
                df_cleaned = df.where(pd.notna(df), None)
                raw_table_from_sheet = df_cleaned.values.tolist()

                # --- НОВАЯ ДВУХЭТАПНАЯ ЛОГИКА ПОИСКА ---
                header_found = False
                for index, row in enumerate(raw_table_from_sheet):
                    # ЭТАП 1: Ищем строку-заголовок
                    if not header_found:
                        for cell in row:
                            if isinstance(cell, str) and "сув омборлари сув шаклланадиган" in cell.lower():
                                header_found = True
                                break  # Нашли заголовок, прекращаем поиск в ячейках
                        if header_found:
                            continue  # Переходим к следующей строке, пропуская саму строку-заголовок

                    # ЭТАП 2: После заголовка ищем первую строку с данными (начинается с "1")
                    if header_found:
                        if row and row[0] is not None and str(row[0]).strip() == "1":
                            # Нашли начало данных. Забираем всё отсюда и до конца листа.
                            aggregated_data.extend(raw_table_from_sheet[index:])
                            # Завершаем работу с этим листом, переходим к следующему.
                            break
            table_data = aggregated_data

        if not table_data:
            print(f"Could not find data starting row in the file {filename}.")
            return

        parsed_data = Modsnow.parse_modsnow_data(table_data)

        asyncio.run(forward_data(url=MODSNOW_FORWARD_URL, data=parsed_data))

    except Exception as e:
        print(f"--- BACKGROUND TASK FAILED for /parse-modsnow ({filename}) ---")
        traceback.print_exc()