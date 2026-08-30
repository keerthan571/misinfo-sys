from __future__ import annotations

import networkx as nx


class InfluenceDetection:
    """
    Computes influence metrics for the propagation graph.

    The detector:
    - calculates PageRank
    - calculates degree centrality
    - calculates betweenness
    - calculates closeness
    - combines graph and account signals
    - returns only genuine influencer-type nodes
    """

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

        self.pagerank: dict[str, float] = {}
        self.degree: dict[str, dict] = {}
        self.betweenness: dict[str, float] = {}
        self.closeness: dict[str, float] = {}
        self.influence_scores: dict[str, float] = {}

    def analyze(self) -> dict:
        if self.graph.number_of_nodes() == 0:
            return {
                "top_influencers": [],
                "statistics": {},
            }

        self.pagerank = self._pagerank()
        self.degree = self._degree_scores()
        self.betweenness = self._betweenness()
        self.closeness = self._closeness()

        self.influence_scores = (
            self._calculate_influence_scores()
        )

        return {
            "top_influencers": self._top_influencers(),
            "statistics": self._statistics(),
        }

    def _pagerank(self) -> dict[str, float]:
        if self.graph.number_of_nodes() == 0:
            return {}

        return nx.pagerank(
            self.graph,
            alpha=0.85,
            weight="weight",
        )

    def _degree_scores(self) -> dict:
        scores = {}

        for node in self.graph.nodes():
            scores[node] = {
                "in_degree": self.graph.in_degree(node),
                "out_degree": self.graph.out_degree(node),
                "total_degree": self.graph.degree(node),
            }

        return scores

    def _betweenness(self) -> dict[str, float]:
        if self.graph.number_of_nodes() <= 1:
            return {
                node: 0.0
                for node in self.graph.nodes()
            }

        return nx.betweenness_centrality(
            self.graph,
            weight="weight",
            normalized=True,
        )

    def _closeness(self) -> dict[str, float]:
        if self.graph.number_of_nodes() == 0:
            return {}

        return nx.closeness_centrality(
            self.graph
        )

    def _calculate_influence_scores(
        self,
    ) -> dict[str, float]:
        scores = {}

        max_pr = max(
            self.pagerank.values(),
            default=1,
        )

        max_degree = max(
            (
                value["total_degree"]
                for value in self.degree.values()
            ),
            default=1,
        )

        max_between = max(
            self.betweenness.values(),
            default=1,
        )

        max_close = max(
            self.closeness.values(),
            default=1,
        )

        followers_values = []

        for node in self.graph.nodes():
            followers = self._safe_number(
                self.graph.nodes[node].get(
                    "followers",
                    0,
                )
            )

            followers_values.append(
                followers
            )

        max_followers = max(
            followers_values,
            default=1,
        )

        for node in self.graph.nodes():
            data = self.graph.nodes[node]

            pr = (
                self.pagerank.get(node, 0)
                / max_pr
                if max_pr
                else 0
            )

            deg = (
                self.degree[node]["total_degree"]
                / max_degree
                if max_degree
                else 0
            )

            bet = (
                self.betweenness.get(node, 0)
                / max_between
                if max_between
                else 0
            )

            clo = (
                self.closeness.get(node, 0)
                / max_close
                if max_close
                else 0
            )

            followers = self._safe_number(
                data.get("followers", 0)
            )

            follower_score = (
                followers / max_followers
                if max_followers
                else 0
            )

            existing_influence = self._safe_number(
                data.get(
                    "influenceScore",
                    data.get(
                        "influence_score",
                        0,
                    ),
                )
            )

            influence_score = min(
                existing_influence / 100,
                1,
            )

            score = (
                0.30 * pr
                + 0.20 * deg
                + 0.15 * bet
                + 0.10 * clo
                + 0.20 * influence_score
                + 0.05 * follower_score
            )

            scores[node] = round(
                score * 100,
                2,
            )

        return scores

    def _is_valid_influencer(
        self,
        node: str,
    ) -> bool:
        data = self.graph.nodes[node]

        role = str(
            data.get("role", "")
        ).strip().lower()

        node_type = str(
            data.get("node_type", "")
        ).strip().lower()

        role_normalized = (
            role
            .replace("-", "_")
            .replace(" ", "_")
        )

        node_type_normalized = (
            node_type
            .replace("-", "_")
            .replace(" ", "_")
        )

        if data.get("is_bot", False):
            return False

        if role_normalized in (
            "user",
            "bot",
            "source",
            "regular_user",
            "normal_user",
        ):
            return False

        if node_type_normalized in (
            "user",
            "bot",
            "source",
            "regular_user",
            "normal_user",
        ):
            return False

        valid_roles = {
            "influencer",
            "micro_influencer",
            "macro_influencer",
            "mega_influencer",
            "community_leader",
            "content_creator",
            "creator",
        }

        if role_normalized in valid_roles:
            return True

        if node_type_normalized in valid_roles:
            return True

        return False

    def _top_influencers(
        self,
        top_n: int = 10,
    ) -> list[dict]:
        candidates = [
            node
            for node in self.graph.nodes()
            if self._is_valid_influencer(node)
        ]

        ranked = sorted(
            candidates,
            key=lambda node:
                self.influence_scores.get(
                    node,
                    0,
                ),
            reverse=True,
        )

        result = []

        for rank, node in enumerate(
            ranked[:top_n],
            start=1,
        ):
            data = self.graph.nodes[node]

            role = str(
                data.get(
                    "role",
                    data.get(
                        "node_type",
                        "influencer",
                    ),
                )
            )

            label = (
                data.get("label")
                or data.get("name")
                or data.get("username")
                or data.get("display_name")
                or node
            )

            result.append(
                {
                    "id": node,
                    "label": label,
                    "name": data.get(
                        "name",
                        label,
                    ),
                    "username": data.get(
                        "username",
                        None,
                    ),
                    "type": data.get(
                        "node_type",
                        role,
                    ),
                    "role": role,
                    "community": data.get(
                        "community",
                        0,
                    ),
                    "followers": self._safe_number(
                        data.get(
                            "followers",
                            0,
                        )
                    ),
                    "score": self.influence_scores.get(
                        node,
                        0,
                    ),
                    "rank": rank,
                    "is_top_influencer": True,
                }
            )

        return result

    def _statistics(self) -> dict:
        if self.graph.number_of_nodes() == 0:
            return {}

        highest_pr = max(
            self.pagerank.items(),
            key=lambda item: item[1],
            default=(None, 0),
        )[0]

        highest_degree = max(
            self.degree.items(),
            key=lambda item:
                item[1]["total_degree"],
            default=(None, {}),
        )[0]

        highest_betweenness = max(
            self.betweenness.items(),
            key=lambda item: item[1],
            default=(None, 0),
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

        influencer_count = sum(
            1
            for node in self.graph.nodes()
            if self._is_valid_influencer(node)
        )

        return {
            "highest_pagerank":
                self._node_summary(highest_pr),

            "highest_degree":
                self._node_summary(highest_degree),

            "highest_betweenness":
                self._node_summary(
                    highest_betweenness
                ),

            "average_degree":
                round(
                    average_degree,
                    2,
                ),

            "node_count":
                self.graph.number_of_nodes(),

            "edge_count":
                self.graph.number_of_edges(),

            "influencer_count":
                influencer_count,
        }

    def _node_summary(
        self,
        node,
    ):
        if node is None:
            return None

        data = self.graph.nodes[node]

        label = (
            data.get("label")
            or data.get("name")
            or data.get("username")
            or node
        )

        return {
            "id": node,
            "label": label,
        }

    @staticmethod
    def _safe_number(value) -> float:
        try:
            if value is None:
                return 0.0

            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return 0.0