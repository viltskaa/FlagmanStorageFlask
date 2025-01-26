from app.utils.DisaiFileCacher.DisaiApi import disai_request, DisaiRequestAnswer
from pathlib import Path

import csv


class DisaiFileCasher:
    def __init__(self, file: Path):
        self.__file = file
        self.__cache: dict[int, str] = {}

        if not self._check_file():
            self._create_file()
        else:
            self._load_cache()

    def _load_cache(self):
        with open(self.__file) as f:
            csv_reader = csv.reader(f)
            next(csv_reader)

            for row in csv_reader:
                art, gtin = row
                gtin = int(gtin)

                if gtin not in self.__cache:
                    self.__cache.update({gtin: art})

    def get_article(self, barcode: int | str) -> DisaiRequestAnswer | None:
        cached_value = self._check_in_cache(barcode)
        if cached_value:
            return cached_value

        disai_request_answer = disai_request(barcode)

        if disai_request_answer:
            self._write_to_file(disai_request_answer)
            return disai_request_answer
        else:
            return None

    def _write_to_file(self, disai_request_answer: DisaiRequestAnswer):
        with open(self.__file, "a" if self._check_file() else "w") as f:
            writer = csv.writer(f)
            writer.writerow(disai_request_answer.to_csv())
        self._load_cache()

    def _check_in_cache(self, barcode: int | str) -> DisaiRequestAnswer | None:
        if not isinstance(barcode, int):
            barcode = int(barcode)

        if barcode in self.__cache:
            article = self.__cache.get(barcode, None)
            if article:
                return DisaiRequestAnswer(article, barcode)
            else:
                return None

    def _check_file(self):
        return self.__file.exists()

    def _create_file(self):
        self.__file.touch()
        with open(self.__file, "w") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["article", "gtin"])
