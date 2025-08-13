import io

from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse

from controller import modsnow, stock
from service.s3 import get_required_files_from_rar

app = FastAPI()

@app.post("/parse-stock")
async def parse_stock(
        background_tasks: BackgroundTasks,  # 4. Добавляем зависимость
        file: UploadFile = File(...)
):
    filename = file.filename.lower()
    if not (filename.endswith('.pdf') or filename.endswith('.xlsx')):
        return JSONResponse(status_code=400, content={"error": "Unsupported file type. Please upload PDF or XLSX."})
    contents = await file.read()

    background_tasks.add_task(stock.process, filename, contents)

    return JSONResponse(
        status_code=202,
        content={"status": "accepted", "message": "File received and scheduled for processing."}
    )


@app.post("/parse-modsnow")
async def parse_modsnow(
        background_tasks: BackgroundTasks,  # Добавляем зависимость
        file: UploadFile = File(...)
):
    filename = file.filename.lower()
    if not (filename.endswith('.pdf') or filename.endswith('.xlsx')):
        return JSONResponse(status_code=400, content={"error": "Unsupported file type. Please upload PDF or XLSX."})

    contents = await file.read()
    background_tasks.add_task(modsnow.process, filename, contents)
    return JSONResponse(
        status_code=202,
        content={"status": "accepted", "message": "File received and scheduled for processing."}
    )


@app.post("/parse-archive")
async def parse_archive(file: UploadFile = File(...)):
    contents = await file.read()
    rar_file = io.BytesIO(contents)

    try:
        result_files = get_required_files_from_rar(rar_file)
        return JSONResponse(content=result_files)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
