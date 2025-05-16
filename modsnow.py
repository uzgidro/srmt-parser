from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Modsnow:
    name: str
    position: int
    current_year: int
    current_percent: int
    current_data: List[int]
    past_year: int
    past_percent: int
    past_data: List[int]
    diff_percent: int
    diff_data: List[int]

    @staticmethod
    def to_int(value):
        try:
            return int(value.strip()) if value and value.strip().isdigit() else 0
        except:
            return 0

    @staticmethod
    def parse_modsnow_data(table):
        results = []

        for i in range(0, len(table), 3):
            try:
                row1 = table[i]
                row2 = table[i + 1]

                if not row1 or not row2:
                    continue

                name = row1[1]
                current_year = row1[2]
                current_percent = Modsnow.to_int(row1[3])
                current_data = [Modsnow.to_int(x) for x in row1[5:13]]

                past_year = row2[2]
                past_percent = Modsnow.to_int(row2[3])
                past_data = [Modsnow.to_int(x) for x in row2[5:13]]

                diff_percent = current_percent - past_percent
                diff_data = [c - p for c, p in zip(current_data, past_data)]

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
                    name = "To'palang"
                    position = 2
                elif "Чорво" in name:
                    name = 'Chorvoq'
                    position = 0
                else:
                    continue

                mod = Modsnow(
                    name=name,
                    position=position,
                    current_year=current_year,
                    current_percent=current_percent,
                    current_data=current_data,
                    past_year=past_year,
                    past_percent=past_percent,
                    past_data=past_data,
                    diff_percent=diff_percent,
                    diff_data=diff_data
                )

                results.append(mod)

            except IndexError:
                continue

        results.sort(key=lambda x: x.position)
        return [asdict(m) for m in results]
