import asyncio
import io
import traceback

import pandas as pd
import pdfplumber
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse

from config import MODSNOW_FORWARD_URL, STOCK_FORWARD_URL
from service.data import Stock
from service.forwarder import forward_data
from service.modsnow import Modsnow
from service.s3 import get_required_files_from_rar

app = FastAPI()


# 2. Создаем "воркер" для обработки stock-файлов
def process_and_forward_stock(contents: bytes):
    """
    Эта функция будет выполняться в фоне.
    Она парсит данные и вызывает пересылку.
    """
    pdf_file = io.BytesIO(contents)
    try:
        with pdfplumber.open(pdf_file) as pdf:
            table = pdf.pages[0].extract_tables()[0]
            parsed_data = Stock.convert_row_to_stock(table)

        # ВАЖНО: forward_data теперь тоже должна быть асинхронной,
        # но мы не можем использовать await в синхронной функции.
        # Решение - запустить ее в цикле событий.
        asyncio.run(forward_data(url=STOCK_FORWARD_URL, data=parsed_data))

    except Exception as e:
        print("--- BACKGROUND TASK FAILED for /parse-stock ---")
        traceback.print_exc()


# 3. Создаем "воркер" для обработки modsnow-файлов
def process_and_forward_modsnow(filename: str, contents: bytes):
    """
    Эта функция будет выполняться в фоне для /parse-modsnow.
    """
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


@app.post("/parse-stock")
async def parse_stock(
        background_tasks: BackgroundTasks,  # 4. Добавляем зависимость
        file: UploadFile = File(...)
):
    """
    Принимает файл, немедленно отвечает 202 и запускает обработку в фоне.
    """
    contents = await file.read()

    # 5. Добавляем задачу в очередь и передаем ей содержимое файла
    background_tasks.add_task(process_and_forward_stock, contents)

    # 6. Немедленно возвращаем ответ
    return JSONResponse(
        status_code=202,
        content={"status": "accepted", "message": "File received and scheduled for processing."}
    )


@app.post("/parse-modsnow")
async def parse_modsnow(
        background_tasks: BackgroundTasks,  # Добавляем зависимость
        file: UploadFile = File(...)
):
    """
    Принимает PDF/XLSX, немедленно отвечает 202 и запускает обработку в фоне.
    """
    filename = file.filename.lower()
    if not (filename.endswith('.pdf') or filename.endswith('.xlsx')):
        return JSONResponse(status_code=400, content={"error": "Unsupported file type. Please upload PDF or XLSX."})

    contents = await file.read()
    background_tasks.add_task(process_and_forward_modsnow, filename, contents)
    return JSONResponse(
        status_code=202,
        content={"status": "accepted", "message": "File received and scheduled for processing."}
    )


@app.post("/parse-archive")
async def parse_archive(file: UploadFile = File(...)):
    # Этот эндпоинт можно оставить как есть, если его обработка быстрая,
    # или тоже переделать на фоновую задачу по аналогии.
    contents = await file.read()
    rar_file = io.BytesIO(contents)

    try:
        result_files = get_required_files_from_rar(rar_file)
        return JSONResponse(content=result_files)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
