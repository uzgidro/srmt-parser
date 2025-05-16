from dataclasses import dataclass, asdict


@dataclass
class Data:
    value: int
    diff: int

    def to_json(self):
        return {
            "value": self.value,
            "diff": self.diff
        }


@dataclass
class Stock:
    id: int
    position: int
    name: str
    date: str
    avg30: Data
    avg10: Data
    past_year: Data
    current_year: int
    percent30: Data
    percent10: Data
    past_year_percent: Data

    @staticmethod
    def parse_data(value_str):
        parts = value_str.split("\n")
        value = int(parts[0]) if parts[0].strip() else 0
        diff = int(parts[1]) if len(parts) > 1 and parts[1].strip() else 0
        return Data(value=value, diff=diff)

    @staticmethod
    def convert_row_to_stock(table):
        response = []

        for row in table:
            reservoir_id = int(row[0])
            name_and_date = row[1].split("\n")
            name = name_and_date[0]
            date = name_and_date[1]

            if name.__contains__("Андижон"):
                name = 'Andijon'
                position = 1
            elif name.__contains__("ангарон"):
                name = 'Ohangaron'
                position = 4
            elif name.__contains__("Сардоба"):
                name = 'Sardoba'
                position = 5
            elif name.__contains__("сорак"):
                name = 'Hisorak'
                position = 3
            elif name.__contains__("поланг"):
                name = 'To\'palang'
                position = 2
            elif name.__contains__("Чорво"):
                name = 'Chorvoq'
                position = 0
            else:
                continue

            avg30 = Stock.parse_data(row[3])
            avg10 = Stock.parse_data(row[4])
            past_year = Stock.parse_data(row[5])
            current_year = float(row[6].replace(",", "."))
            percent30 = Stock.parse_data(row[7])
            percent10 = Stock.parse_data(row[8])
            past_year_percent = Stock.parse_data(row[9])

            response.append(Stock(
                id=reservoir_id,
                position=position,
                name=name,
                date=date,
                avg30=avg30,
                avg10=avg10,
                past_year=past_year,
                current_year=int(current_year),
                percent30=percent30,
                percent10=percent10,
                past_year_percent=past_year_percent
            ))
        response.sort(key=lambda x: x.position)
        return [asdict(s) for s in response]
