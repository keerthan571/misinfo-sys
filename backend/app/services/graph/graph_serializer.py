from __future__ import annotations

from typing import Any

import networkx as nx


class GraphSerializer:
    """
    Converts a NetworkX graph into a frontend-ready JSON response.

    The serializer preserves:
    - node-level propagation metrics
    - influence metrics
    - community information
    - graph statistics

    It also exposes frontend-compatible aliases so the existing
    React GraphViewer can consume the backend response cleanly.
    """

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def serialize(
        self,
        influence: dict[str, Any] | None = None,
        communities: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        influence = influence or {}
        communities = communities or {}

        statistics = self._statistics()

        # Backend InfluenceDetection returns:
        # {
        #     "top_influencers": [...],
        #     "statistics": {...}
        # }
        top_influencers = influence.get(
            "top_influencers",
            [],
        )

        # Make a quick lookup for top influencer scores.
        influencer_scores = {
            item.get("id"): item.get("score", 0)
            for item in top_influencers
            if item.get("id") is not None
        }

        nodes = self._nodes(
            influencer_scores=influencer_scores
        )

        # CommunityDetector returns:
        # {
        #     "communities": [...],
        #     "summary": [...]
        # }
        community_list = communities.get(
            "communities",
            []
        )

        community_summary = communities.get(
            "summary",
            []
        )

        # Determine the largest community from the actual
        # detected community data.
        largest_community = self._largest_community(
            community_list
        )

        # Influence statistics calculated by InfluenceDetection.
        influence_statistics = influence.get(
            "statistics",
            {}
        )

        # Keep the original backend structure AND provide
        # frontend-compatible aliases.
        analytics = {
            "totalNodes": statistics["node_count"],
            "totalEdges": statistics["edge_count"],
            "averageInfluence": self._average_influence(),
            "density": statistics["density"],
            "spreadEfficiency": self._spread_efficiency(),
            "largestCommunity": largest_community,
            "connectedComponents":
                statistics["connected_components"],
            "leaders": statistics["leaders"],
            "bots": statistics["bots"],
            "viralNodes": statistics["viral_nodes"],
            "nodeTypes": statistics["node_types"],
            "averageDegree":
                influence_statistics.get(
                    "average_degree",
                    0,
                ),
        }

        return {
            # ==================================================
            # Main graph
            # ==================================================

            "nodes": nodes,
            "edges": self._edges(),

            # ==================================================
            # Original backend structures
            # ==================================================

            "statistics": statistics,
            "influence": influence,
            "communities": communities,

            # ==================================================
            # Frontend-compatible structures
            # ==================================================

            "analytics": analytics,

            "influencers": top_influencers,

            "communityAnalytics": community_summary,

            # Useful graph metadata
            "largestCommunity": largest_community,
        }

    # ==========================================================
    # NODE SERIALIZATION
    # ==========================================================

    def _nodes(
        self,
        influencer_scores: dict[str, float] | None = None,
    ) -> list[dict[str, Any]]:

        influencer_scores = influencer_scores or {}

        nodes = []

        # Find maximum propagation influence for normalization.
        raw_influences = [
            float(
                data.get(
                    "influence_score",
                    0,
                )
                or 0
            )
            for _, data in self.graph.nodes(data=True)
        ]

        max_influence = max(
            raw_influences,
            default=1,
        )

        if max_influence <= 0:
            max_influence = 1

        for node_id, data in self.graph.nodes(data=True):

            influence_score = float(
                data.get(
                    "influence_score",
                    0,
                )
                or 0
            )

            # Prefer InfluenceDetection's normalized score
            # for top influencers when available.
            detected_influence = influencer_scores.get(
                node_id
            )

            if detected_influence is not None:
                network_influence_percent = round(
                float(detected_influence),
                2,
            )
            else:
                network_influence_percent = round(
                    (
                        influence_score
                        / max_influence
                    ) * 100,
                    2,
                )

            # Preserve an explicitly calculated reach if
            # the propagation engine already supplied one.
            reach = data.get(
                "reach",
                None,
            )

            # If reach isn't present, calculate a deterministic
            # graph-based reach from descendants.
            if reach is None:
                try:
                    reach = len(
                        nx.descendants(
                            self.graph,
                            node_id,
                        )
                    )
                except Exception:
                    reach = 0

            reach = int(reach or 0)

            # Degree metrics
            in_degree = self.graph.in_degree(
                node_id
            )

            out_degree = self.graph.out_degree(
                node_id
            )

            degree = self.graph.degree(
                node_id
            )

            # PageRank is calculated independently here so
            # every node has a meaningful value available to
            # the frontend.
            page_rank = 0.0

            try:
                page_rank_values = nx.pagerank(
                    self.graph,
                    alpha=0.85,
                    weight="weight",
                )

                page_rank = round(
                    page_rank_values.get(
                        node_id,
                        0.0,
                    ),
                    6,
                )

            except Exception:
                page_rank = 0.0

            # Normalize PageRank for frontend display.
            page_rank_score = 0.0

            try:
                max_page_rank = max(
                    page_rank_values.values(),
                    default=1.0,
                )

                if max_page_rank > 0:
                    page_rank_score = round(
                        (
                            page_rank
                            / max_page_rank
                        ) * 100,
                        2,
                    )

            except Exception:
                page_rank_score = 0.0

            followers = int(
                data.get(
                    "followers",
                    0,
                )
                or 0
            )

            share_probability = float(
                data.get(
                    "share_probability",
                    0,
                )
                or 0
            )

            community = data.get(
                "community"
            )

            node_type = data.get(
                "node_type"
            )

            is_leader = bool(
                data.get(
                    "is_leader",
                    False,
                )
            )

            is_bot = bool(
                data.get(
                    "is_bot",
                    False,
                )
            )

            is_viral = bool(
                data.get(
                    "is_viral",
                    False,
                )
            )

            nodes.append(
                {
                    # =========================================
                    # Core fields
                    # =========================================

                    "id": node_id,

                    "label": data.get(
                        "label",
                        node_id,
                    ),

                    "type": node_type,

                    "nodeType": node_type,

                    # =========================================
                    # Identity / classification
                    # =========================================

                    "displayName": data.get(
                        "display_name",
                        data.get(
                            "label",
                            node_id,
                        ),
                    ),

                    "followers": followers,

                    "formattedFollowers":
                        self._format_followers(
                            followers
                        ),

                    "leader": is_leader,

                    "isLeader": is_leader,

                    "bot": is_bot,

                    "isBot": is_bot,

                    "viral": is_viral,

                    "isViral": is_viral,

                    "verified": bool(
                        data.get(
                            "verified",
                            is_leader,
                        )
                    ),

                    # =========================================
                    # Propagation metrics
                    # =========================================

                    "influenceScore":
                        round(
                            influence_score,
                            2,
                        ),

                    "networkInfluence":
                        round(
                            influence_score,
                            4,
                        ),

                    "networkInfluencePercent":
                        network_influence_percent,

                    "reach": reach,

                    "shareProbability":
                        round(
                            share_probability,
                            4,
                        ),

                    # =========================================
                    # Network metrics
                    # =========================================

                    "pageRank": page_rank,

                    "pageRankScore":
                        page_rank_score,

                    "inDegree": in_degree,

                    "outDegree": out_degree,

                    "degree": degree,

                    "weightedReach":
                        float(
                            data.get(
                                "weighted_reach",
                                reach,
                            )
                            or 0
                        ),

                    # =========================================
                    # Community
                    # =========================================

                    "community": community,

                    # =========================================
                    # Platform / publisher
                    # =========================================

                    "platform": data.get(
                        "platform"
                    ),

                    "publisher": data.get(
                        "publisher"
                    ),

                    # =========================================
                    # Propagation hierarchy
                    # =========================================

                    "parentId": data.get(
                        "parent_id"
                    ),

                    "level": data.get(
                        "level",
                        0,
                    ),
                }
            )

        return nodes

    # ==========================================================
    # EDGE SERIALIZATION
    # ==========================================================

    def _edges(self) -> list[dict[str, Any]]:

        edges = []

        for source, target, data in self.graph.edges(
            data=True
        ):

            edges.append(
                {
                    "id": f"{source}-{target}",

                    "source": source,

                    "target": target,

                    "weight": round(
                        float(
                            data.get(
                                "weight",
                                1.0,
                            )
                            or 1.0
                        ),
                        3,
                    ),

                    "interaction": data.get(
                        "interaction"
                    ),

                    "type": data.get(
                        "interaction"
                    ),
                }
            )

        return edges

    # ==========================================================
    # GRAPH STATISTICS
    # ==========================================================

    def _statistics(self) -> dict[str, Any]:

        node_types: dict[str, int] = {}

        leaders = 0
        bots = 0
        viral = 0

        for _, data in self.graph.nodes(
            data=True
        ):

            node_type = data.get(
                "node_type",
                "unknown",
            )

            node_types[node_type] = (
                node_types.get(
                    node_type,
                    0,
                )
                + 1
            )

            if data.get(
                "is_leader"
            ):
                leaders += 1

            if data.get(
                "is_bot"
            ):
                bots += 1

            if data.get(
                "is_viral"
            ):
                viral += 1

        density = (
            round(
                nx.density(
                    self.graph
                ),
                4,
            )
            if self.graph.number_of_nodes() > 1
            else 0.0
        )

        return {
            "node_count":
                self.graph.number_of_nodes(),

            "edge_count":
                self.graph.number_of_edges(),

            "density":
                density,

            "connected_components":
                nx.number_weakly_connected_components(
                    self.graph
                ),

            "is_directed":
                self.graph.is_directed(),

            "leaders":
                leaders,

            "bots":
                bots,

            "viral_nodes":
                viral,

            "node_types":
                node_types,
        }

    # ==========================================================
    # INFLUENCE
    # ==========================================================

    def _average_influence(self) -> float:

        values = []

        for _, data in self.graph.nodes(
            data=True
        ):

            value = float(
                data.get(
                    "influence_score",
                    0,
                )
                or 0
            )

            values.append(value)

        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            2,
        )

    # ==========================================================
    # SPREAD EFFICIENCY
    # ==========================================================

    def _spread_efficiency(self) -> float:

        node_count = (
            self.graph.number_of_nodes()
        )

        if node_count <= 1:
            return 0.0

        edge_count = (
            self.graph.number_of_edges()
        )

        # A tree-like propagation network has
        # approximately N-1 edges.
        #
        # This represents how effectively the graph
        # establishes propagation relationships relative
        # to the minimum connected propagation structure.
        efficiency = (
            edge_count
            / (node_count - 1)
        ) * 100

        return round(
            min(
                efficiency,
                100.0,
            ),
            2,
        )

    # ==========================================================
    # LARGEST COMMUNITY
    # ==========================================================

    def _largest_community(
        self,
        communities: list[dict[str, Any]],
    ) -> Any:

        if not communities:
            return "-"

        largest = max(
            communities,
            key=lambda item:
                item.get(
                    "size",
                    0,
                ),
        )

        return largest.get(
            "id",
            "-",
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def _format_followers(
        value: int,
    ) -> str:

        value = int(
            value or 0
        )

        if value >= 1_000_000:
            return (
                f"{value / 1_000_000:.1f}M"
            )

        if value >= 1_000:
            return (
                f"{value / 1_000:.1f}K"
            )

        return str(value)