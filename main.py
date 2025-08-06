import io

import pandas as pd
import pdfplumber
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from data import Stock
from modsnow import Modsnow
from s3 import get_required_files_from_rar


app = FastAPI()


@app.post("/parse-stock")
async def parse_stock(file: UploadFile = File(...)):
    contents = await file.read()
    pdf_file = io.BytesIO(contents)

    try:
        with pdfplumber.open(pdf_file) as pdf:
            table = pdf.pages[0].extract_tables()[0]
            response = Stock.convert_row_to_stock(table)

        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/parse-modsnow")
async def parse_modsnow(file: UploadFile = File(...)):  # 1. Исправлено имя функции
    filename = file.filename.lower()
    contents = await file.read()

    try:
        if filename.endswith('.pdf'):
            print("Processing PDF file...")
            pdf_file = io.BytesIO(contents)
            with pdfplumber.open(pdf_file) as pdf:
                table = pdf.pages[0].extract_tables()[0]
                reservoirs = []
                for index, row in enumerate(table):
                    if row and row[0] and str(row[0]).strip() == "1":
                        reservoirs = table[index:]
                response = Modsnow.parse_modsnow_data(reservoirs)

        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Unsupported file type: '{filename}'. Please upload a PDF or XLSX file."}
            )

        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to process file: {str(e)}"})


@app.post("/parse-archive")
async def parse_archive(file: UploadFile = File(...)):
    contents = await file.read()
    rar_file = io.BytesIO(contents)

    try:
        result_files = get_required_files_from_rar(rar_file)
        return JSONResponse(content=result_files)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})