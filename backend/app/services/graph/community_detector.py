from __future__ import annotations

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities


class CommunityDetector:
    """
    Detects graph communities and computes
    community-level analytics.
    """

    INFLUENCER_NODE = "influencer"

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def analyze(self) -> dict:
        communities = self._detect_communities()

        return {
            "communities": communities,
            "summary": self._summary(communities),
        }

    def _detect_communities(self) -> list[dict]:
        if self.graph.number_of_nodes() == 0:
            return []

        graph = self.graph.to_undirected()

        detected = list(
            greedy_modularity_communities(graph)
        )

        result = []

        for community_id, community in enumerate(detected):
            nodes = []

            for node in community:
                self.graph.nodes[node]["community"] = community_id

                data = self.graph.nodes[node]

                nodes.append(
                    {
                        "id": node,
                        "label": data.get("label"),
                        "type": data.get("node_type"),
                        "followers": data.get("followers", 0),
                        "leader": data.get("is_leader", False),
                        "bot": data.get("is_bot", False),
                        "is_viral": data.get("is_viral", False),
                        "community": community_id,
                    }
                )

            result.append(
                {
                    "id": community_id,
                    "size": len(nodes),
                    "nodes": nodes,
                }
            )

        return result

    def _summary(
        self,
        communities: list[dict],
    ) -> list[dict]:
        summary = []

        for community in communities:
            followers = []
            bots = 0
            leaders = 0
            influencers = 0

            for node in community["nodes"]:
                data = self.graph.nodes[node["id"]]

                followers.append(
                    data.get("followers", 0)
                )

                if data.get("is_bot"):
                    bots += 1

                if data.get("is_leader"):
                    leaders += 1

                if data.get("node_type") == self.INFLUENCER_NODE:
                    influencers += 1

            average_followers = (
                sum(followers) / len(followers)
                if followers
                else 0
            )

            risk_score = self._risk_score(
                bots=bots,
                influencers=influencers,
                average_followers=average_followers,
                size=community["size"],
            )

            summary.append(
                {
                    "community_id": community["id"],
                    "size": community["size"],
                    "leaders": leaders,
                    "bots": bots,
                    "influencers": influencers,
                    "average_followers": round(
                        average_followers,
                        2,
                    ),
                    "risk_score": round(
                        risk_score,
                        2,
                    ),
                }
            )

        summary.sort(
            key=lambda community: community["risk_score"],
            reverse=True,
        )

        return summary

    def _risk_score(
        self,
        bots: int,
        influencers: int,
        average_followers: float,
        size: int,
    ) -> float:
        score = (
            bots * 3
            + influencers * 5
            + average_followers / 10000
            + size
        )

        return score