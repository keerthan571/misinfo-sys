from __future__ import annotations

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class PDFGenerator:
    """
    Generates a professional PDF report.
    """

    def generate(
        self,
        report: dict,
        output_path: str,
    ) -> str:

        document = SimpleDocTemplate(output_path)
        styles = getSampleStyleSheet()

        elements = []

        self._title(elements, styles)
        self._metadata(elements, styles, report)
        self._analysis(elements, styles, report)
        self._prediction(elements, styles, report)
        self._engagement(elements, styles, report)
        self._verification(elements, styles, report)
        self._graph_statistics(elements, styles, report)
        self._top_influencers(elements, styles, report)
        self._communities(elements, styles, report)

        document.build(elements)

        return output_path

    def _title(self, elements, styles):

        elements.append(
            Paragraph(
                "AI Misinformation Analysis Report",
                styles["Title"],
            )
        )

        elements.append(Spacer(1, 20))

    def _metadata(
        self,
        elements,
        styles,
        report,
    ):

        metadata = report.get("metadata", {})

        elements.append(
            Paragraph(
                f"<b>Report ID:</b> {metadata.get('report_id','-')}",
                styles["Normal"],
            )
        )

        elements.append(
            Paragraph(
                f"<b>Generated At:</b> {metadata.get('generated_at','-')}",
                styles["Normal"],
            )
        )

        elements.append(Spacer(1, 15))

    def _analysis(
        self,
        elements,
        styles,
        report,
    ):

        analysis = report.get("analysis", {})

        elements.append(
            Paragraph(
                "Analysis Summary",
                styles["Heading2"],
            )
        )

        for key, value in analysis.items():
            elements.append(
                Paragraph(
                    f"<b>{key.replace('_',' ').title()}:</b> {value}",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 15))

    def _prediction(
        self,
        elements,
        styles,
        report,
    ):

        prediction = report.get("prediction", {})

        elements.append(
            Paragraph(
                "Spread Prediction",
                styles["Heading2"],
            )
        )

        for key, value in prediction.items():
            elements.append(
                Paragraph(
                    f"<b>{key.replace('_',' ').title()}:</b> {value}",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 15))

    def _engagement(
        self,
        elements,
        styles,
        report,
    ):

        engagement = report.get("engagement", {})

        elements.append(
            Paragraph(
                "Engagement Metrics",
                styles["Heading2"],
            )
        )

        for key, value in engagement.items():
            elements.append(
                Paragraph(
                    f"<b>{key.title()}:</b> {value}",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 15))

    def _verification(
        self,
        elements,
        styles,
        report,
    ):

        verification = report.get(
            "fact_verification",
            {},
        )

        elements.append(
            Paragraph(
                "Fact Verification",
                styles["Heading2"],
            )
        )

        for key, value in verification.items():

            if isinstance(value, list):
                value = ", ".join(value)

            elements.append(
                Paragraph(
                    f"<b>{key.replace('_',' ').title()}:</b> {value}",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 15))

    def _graph_statistics(
        self,
        elements,
        styles,
        report,
    ):

        statistics = report.get(
            "graph_statistics",
            {},
        )

        elements.append(
            Paragraph(
                "Graph Statistics",
                styles["Heading2"],
            )
        )

        for key, value in statistics.items():
            elements.append(
                Paragraph(
                    f"<b>{key.replace('_',' ').title()}:</b> {value}",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 15))

    def _top_influencers(
        self,
        elements,
        styles,
        report,
    ):

        influencers = report.get(
            "top_influencers",
            [],
        )

        elements.append(
            Paragraph(
                "Top Influencers",
                styles["Heading2"],
            )
        )

        for influencer in influencers:

            elements.append(
                Paragraph(
                    f"{influencer['label']} | Followers: {influencer['followers']} | Score: {influencer['score']}",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 15))

    def _communities(
        self,
        elements,
        styles,
        report,
    ):

        communities = report.get(
            "communities",
            [],
        )

        elements.append(
            Paragraph(
                "Community Summary",
                styles["Heading2"],
            )
        )

        for community in communities:

            elements.append(
                Paragraph(
                    f"Community {community['community_id']} | Risk Score: {community['risk_score']}",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 15))