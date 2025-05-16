import io

import pdfplumber
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from data import Stock
from modsnow import Modsnow

app = FastAPI()


def is_reservoir(n):
    return n[0].isnumeric()


@app.post("/parse-stock")
async def parse_stock(file: UploadFile = File(...)):
    contents = await file.read()
    pdf_file = io.BytesIO(contents)

    try:
        with pdfplumber.open(pdf_file) as pdf:
            table = pdf.pages[0].extract_tables()[0]
            reservoirs = filter(is_reservoir, table)
            response = Stock.convert_row_to_stock(reservoirs)

        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/parse-mondsnow")
async def parse_stock(file: UploadFile = File(...)):
    contents = await file.read()
    pdf_file = io.BytesIO(contents)

    try:
        with pdfplumber.open(pdf_file) as pdf:
            table = pdf.pages[0].extract_tables()[0]
            reservoirs = []
            for index, row in enumerate(table):
                if row and row[0] and str(row[0]).strip() == "1":
                    reservoirs = table[index:]
            response = Modsnow.parse_modsnow_data(reservoirs)

        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
