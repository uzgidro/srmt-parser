import pdfplumber

from modsnow import Modsnow

with pdfplumber.open("modsnow.pdf") as pdf:
    table = pdf.pages[0].extract_tables()[0]

    reservoirs = []
    for index, row in enumerate(table):
        print(row)
        if row and row[0] and str(row[0]).strip() == "1":
            reservoirs = table[index:]
    response = Modsnow.parse_modsnow_data(reservoirs)
    print(response)