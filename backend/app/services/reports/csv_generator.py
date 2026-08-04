from __future__ import annotations

import csv


class CSVGenerator:
    """
    Generates a CSV report from
    the report dictionary.
    """

    def generate(
        self,
        report: dict,
        output_path: str,
    ) -> str:

        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                [
                    "Section",
                    "Field",
                    "Value",
                ]
            )

            self._write_section(
                writer,
                "Metadata",
                report.get(
                    "metadata",
                    {},
                ),
            )

            self._write_section(
                writer,
                "Analysis",
                report.get(
                    "analysis",
                    {},
                ),
            )

            self._write_section(
                writer,
                "Engagement",
                report.get(
                    "engagement",
                    {},
                ),
            )

            self._write_section(
                writer,
                "Prediction",
                report.get(
                    "prediction",
                    {},
                ),
            )

            self._write_section(
                writer,
                "Fact Verification",
                report.get(
                    "fact_verification",
                    {},
                ),
            )

            self._write_section(
                writer,
                "Graph Statistics",
                report.get(
                    "graph_statistics",
                    {},
                ),
            )

            self._write_list(
                writer,
                "Top Influencers",
                report.get(
                    "top_influencers",
                    [],
                ),
            )

            self._write_list(
                writer,
                "Communities",
                report.get(
                    "communities",
                    [],
                ),
            )

        return output_path

    def _write_section(
        self,
        writer,
        section,
        data,
    ):

        for key, value in data.items():

            if isinstance(value, list):
                value = ", ".join(
                    map(str, value)
                )

            writer.writerow(
                [
                    section,
                    key,
                    value,
                ]
            )

    def _write_list(
        self,
        writer,
        section,
        data,
    ):

        for item in data:

            for key, value in item.items():

                writer.writerow(
                    [
                        section,
                        key,
                        value,
                    ]
                )