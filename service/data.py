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
        if value_str is None:
            return Data(value=0, diff=0)
        parts = value_str.split("\n")
        value = int(parts[0]) if parts[0].strip() else 0
        diff = int(parts[1]) if len(parts) > 1 and parts[1].strip() else 0
        return Data(value=value, diff=diff)

    @staticmethod
    def translate_date_string(date_str: str) -> str:
        month_translation = {
            "янв": "yan", "фев": "fev", "мар": "mar",
            "апр": "apr", "май": "may", "июн": "iun",
            "июл": "iul", "авг": "avg", "сен": "sen",
            "окт": "okt", "ноя": "noy", "дек": "dek",
        }

        if date_str is None:
            return ""
        translated_str = date_str.lower()

        for rus, lat in month_translation.items():
            translated_str = translated_str.replace(rus, lat)

        return translated_str


    @staticmethod
    def convert_row_to_stock(table):
        response = []

        reservoirs = filter(
            lambda row: row and row[0] is not None and str(row[0]).strip().isnumeric(),
            table
        )

        for row in reservoirs:
            try:
                reservoir_id = int(row[0])
                name_and_date = str(row[1]).split("\n")
                name = name_and_date[0]
                raw_date = name_and_date[1] if len(name_and_date) > 1 else ""
                date = Stock.translate_date_string(raw_date)

                if "Андижон" in name:
                    name = 'Andijon'
                    position = 1
                elif "ангарон" in name:
                    name = 'Ohangaron'
                    position = 4
                elif "Сардоба" in name:
                    name = 'Sardoba'
                    position = 5
                elif "сорак" in name:
                    name = 'Hisorak'
                    position = 3
                elif "поланг" in name:
                    name = 'To\'palang'
                    position = 2
                elif "Чорво" in name:
                    name = 'Chorvoq'
                    position = 0
                else:
                    continue

                avg30 = Stock.parse_data(row[3])
                avg10 = Stock.parse_data(row[4])
                past_year = Stock.parse_data(row[5])
                # Безопасно получаем год
                current_year_str = str(row[6]).replace(",", ".") if row[6] is not None else "0"
                current_year = float(current_year_str)
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
            except (IndexError, ValueError) as e:
                print(f"Skipping malformed row due to error: {e}. Row content: {row}")
                continue

        response.sort(key=lambda x: x.position)
        return [asdict(s) for s in response]