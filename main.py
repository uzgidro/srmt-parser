from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import pdfplumber
from data import Stock
from typing import List
import io


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
            response: List[dict] = []
            for row in reservoirs:
                response.append(Stock.convert_row_to_stock(row).to_json())

        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})