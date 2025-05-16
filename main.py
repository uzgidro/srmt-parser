import pdfplumber

from data import Stock


def is_reservoir(n):
    return n[0].isnumeric()

with pdfplumber.open("stock.pdf") as pdf:
    table = pdf.pages[0].extract_tables()[0]
    reservoirs = filter(is_reservoir, table)
    response = []
    for row in reservoirs:
        response.append(Stock.convert_row_to_stock(row).to_json())
    print(response)