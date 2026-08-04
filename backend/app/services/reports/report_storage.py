from __future__ import annotations

import json
from pathlib import Path


class ReportStorage:
    """
    Handles saving and loading report files.
    """

    def __init__(
        self,
        output_directory: str = "reports",
    ):

        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_json(
        self,
        report: dict,
        filename: str,
    ) -> str:

        filepath = self.output_directory / filename

        with open(
            filepath,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                default=str,
            )

        return str(filepath)

    def load_json(
        self,
        filename: str,
    ) -> dict:

        filepath = self.output_directory / filename

        with open(
            filepath,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    def exists(
        self,
        filename: str,
    ) -> bool:

        filepath = self.output_directory / filename

        return filepath.exists()

    def delete(
        self,
        filename: str,
    ) -> bool:

        filepath = self.output_directory / filename

        if filepath.exists():

            filepath.unlink()

            return True

        return False

    def list_reports(self):

        return sorted(
            [
                file.name
                for file in self.output_directory.glob("*.json")
            ]
        )