import pdfplumber

from service.data import Stock

with pdfplumber.open("stock.pdf") as pdf:
    table = pdf.pages[0].extract_tables()[0]
    print(table)
    response = Stock.convert_row_to_stock(table)
    print(response)