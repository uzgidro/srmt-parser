import asyncio
import io
import traceback

import pandas as pd
import pdfplumber

from config import STOCK_FORWARD_URL
from service.data import Stock
from service.forwarder import forward_data


def process(filename: str, contents: bytes):
    table_data = []
    try:
        if filename.endswith('.pdf'):
            pdf_file = io.BytesIO(contents)
            with pdfplumber.open(pdf_file) as pdf:
                # Предполагаем, что нужная таблица на первой странице
                table_data = pdf.pages[0].extract_tables()[0]

        elif filename.endswith('.xlsx'):
            excel_file = io.BytesIO(contents)
            # Читаем все листы из файла
            all_sheets_dfs = pd.read_excel(excel_file, sheet_name=None, header=None)
            aggregated_data = []
            for sheet_name, df in all_sheets_dfs.items():
                df_cleaned = df.where(pd.notna(df), None)
                aggregated_data.extend(df_cleaned.values.tolist())
            table_data = aggregated_data

        if not table_data:
            print(f"Could not find data in the file {filename}.")
            return

        parsed_data = Stock.convert_row_to_stock(table_data)
        print(parsed_data)
        asyncio.run(forward_data(url=STOCK_FORWARD_URL, data=parsed_data))

    except Exception as e:
        print(f"--- BACKGROUND TASK FAILED for /parse-stock ({filename}) ---")
        traceback.print_exc()