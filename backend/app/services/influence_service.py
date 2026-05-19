import networkx as nx


class InfluenceService:
    def __init__(self):
        pass

    def detect_influencers(self, topic: str):

        # Create directed graph
        G = nx.DiGraph()

        # Sample propagation network
        G.add_edges_from([
            ("Alice", "Bob"),
            ("Alice", "Charlie"),
            ("Bob", "David"),
            ("Charlie", "Eve"),
            ("Alice", "Eve"),
            ("David", "Frank")
        ])

        # Calculate PageRank scores
        pagerank_scores = nx.pagerank(G)

        # Sort top influencers
        sorted_users = sorted(
            pagerank_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_influencers = []

        for user, score in sorted_users[:3]:
            top_influencers.append({
                "user_id": user.lower(),
                "name": user,
                "influence_score": round(score * 100, 2)
            })

        return {
            "topic": topic,
            "top_influencers": top_influencers,
            "message": "Top influencers identified using PageRank algorithm."
        }


influence_service = InfluenceService()