from __future__ import annotations

import networkx as nx


class InfluenceDetection:
    """
    Computes influence metrics for the propagation graph.
    """

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

        self.pagerank = {}
        self.degree = {}
        self.betweenness = {}
        self.closeness = {}
        self.influence_scores = {}

    # ======================================================================
    # Public API
    # ======================================================================

    def analyze(self):
        """
        Run the complete influence analysis pipeline.
        """

        self.pagerank = self._pagerank()
        self.degree = self._degree_scores()
        self.betweenness = self._betweenness()
        self.closeness = self._closeness()

        self.influence_scores = self._calculate_influence_scores()

        return {
            "top_influencers": self._top_influencers(),
            "statistics": self._statistics(),
        }

    # ======================================================================
    # Metric Calculations
    # ======================================================================

    def _pagerank(self):
        return nx.pagerank(
            self.graph,
            alpha=0.85,
            weight="weight",
        )

    def _degree_scores(self):
        scores = {}

        for node in self.graph.nodes():
            scores[node] = {
                "in_degree": self.graph.in_degree(node),
                "out_degree": self.graph.out_degree(node),
                "total_degree": self.graph.degree(node),
            }

        return scores

    def _betweenness(self):
        return nx.betweenness_centrality(
            self.graph,
            weight="weight",
            normalized=True,
        )

    def _closeness(self):
        return nx.closeness_centrality(self.graph)

    # ======================================================================
    # Influence Score
    # ======================================================================

    def _calculate_influence_scores(self):
        scores = {}

        max_pr = max(self.pagerank.values(), default=1)
        max_degree = max(
            (v["total_degree"] for v in self.degree.values()),
            default=1,
        )
        max_between = max(self.betweenness.values(), default=1)
        max_close = max(self.closeness.values(), default=1)

        for node in self.graph.nodes():

            pr = self.pagerank[node] / max_pr if max_pr else 0

            deg = (
                self.degree[node]["total_degree"] / max_degree
                if max_degree
                else 0
            )

            bet = (
                self.betweenness[node] / max_between
                if max_between
                else 0
            )

            clo = (
                self.closeness[node] / max_close
                if max_close
                else 0
            )

            score = (
                0.40 * pr
                + 0.30 * deg
                + 0.20 * bet
                + 0.10 * clo
            )

            scores[node] = round(score, 4)

        return scores

    # ======================================================================
    # Top Influencers
    # ======================================================================

    def _top_influencers(self, top_n=10):

        ranked = sorted(
            self.influence_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        result = []

        for node, score in ranked[:top_n]:

            data = self.graph.nodes[node]

            result.append(
                {
                    "id": node,
                    "label": data.get("label", node),
                    "type": data.get("node_type"),
                    "community": data.get("community"),
                    "followers": data.get("followers", 0),
                    "score": score,
                }
            )

        return result

    # ======================================================================
    # Statistics
    # ======================================================================

    def _statistics(self):

        highest_pr = max(
            self.pagerank.items(),
            key=lambda x: x[1],
        )[0]

        highest_degree = max(
            self.degree.items(),
            key=lambda x: x[1]["total_degree"],
        )[0]

        highest_betweenness = max(
            self.betweenness.items(),
            key=lambda x: x[1],
        )[0]

        average_degree = (
            sum(
                value["total_degree"]
                for value in self.degree.values()
            )
            / len(self.degree)
            if self.degree
            else 0
        )

        return {
            "highest_pagerank": highest_pr,
            "highest_degree": highest_degree,
            "highest_betweenness": highest_betweenness,
            "average_degree": round(average_degree, 2),
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
        }