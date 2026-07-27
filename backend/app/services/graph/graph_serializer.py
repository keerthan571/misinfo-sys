from __future__ import annotations

import networkx as nx


class GraphSerializer:
    """
    Converts a NetworkX graph into a frontend-ready JSON response.
    """

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    # ======================================================================
    # Public API
    # ======================================================================

    def serialize(
        self,
        influence=None,
        communities=None,
    ):
        return {
            "nodes": self._nodes(),
            "edges": self._edges(),
            "statistics": self._statistics(),
            "influence": influence or {},
            "communities": communities or {},
        }

    # ======================================================================
    # Nodes
    # ======================================================================

    def _nodes(self):

        nodes = []

        for node_id, data in self.graph.nodes(data=True):

            nodes.append(
                {
                    "id": node_id,
                    "label": data.get("label"),
                    "type": data.get("node_type"),
                    "followers": data.get("followers", 0),
                    "leader": data.get("is_leader", False),
                    "bot": data.get("is_bot", False),
                    "viral": data.get("is_viral", False),
                    "community": data.get("community"),
                }
            )

        return nodes

    # ======================================================================
    # Edges
    # ======================================================================

    def _edges(self):

        edges = []

        for source, target, data in self.graph.edges(data=True):

            edges.append(
                {
                    "source": source,
                    "target": target,
                    "weight": round(data.get("weight", 1.0), 3),
                }
            )

        return edges

    # ======================================================================
    # Statistics
    # ======================================================================

    def _statistics(self):

        node_types = {}

        leaders = 0
        bots = 0
        viral = 0

        for _, data in self.graph.nodes(data=True):

            node_type = data.get("node_type", "unknown")

            node_types[node_type] = (
                node_types.get(node_type, 0) + 1
            )

            if data.get("is_leader"):
                leaders += 1

            if data.get("is_bot"):
                bots += 1

            if data.get("is_viral"):
                viral += 1

        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "density": round(nx.density(self.graph), 4),
            "connected_components": nx.number_weakly_connected_components(
                self.graph
            ),
            "is_directed": self.graph.is_directed(),
            "leaders": leaders,
            "bots": bots,
            "viral_nodes": viral,
            "node_types": node_types,
        }