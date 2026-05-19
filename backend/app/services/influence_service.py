import networkx as nx


class InfluenceService:
    """
    Detects influential users involved in
    misinformation propagation using graph analysis.
    """

    def __init__(self):
        pass

    def classify_influencer(self, score):

        if score > 30:
            return "Mega Influencer"

        elif score > 20:
            return "High Influencer"

        return "Moderate Influencer"

    def detect_influencers(self, topic: str):

        # Create directed weighted graph
        G = nx.DiGraph()

        # Weighted propagation network
        # Weight represents interaction/share strength
        weighted_edges = [
            ("Alice", "Bob", 5),
            ("Alice", "Charlie", 3),
            ("Bob", "David", 4),
            ("Charlie", "Eve", 2),
            ("Alice", "Eve", 6),
            ("David", "Frank", 1),
            ("Eve", "George", 4),
            ("Charlie", "Frank", 3)
        ]

        # Add edges
        for source, target, weight in weighted_edges:
            G.add_edge(source, target, weight=weight)

        # Weighted PageRank calculation
        pagerank_scores = nx.pagerank(G, weight="weight")

        # Sort influencers
        sorted_users = sorted(
            pagerank_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_influencers = []

        for user, score in sorted_users[:5]:

            influence_score = round(score * 100, 2)

            top_influencers.append({
                "user_id": user.lower(),

                "name": user,

                "influence_score": influence_score,

                "category": self.classify_influencer(
                    influence_score
                )
            })

        return {
            "status": "success",

            "module": "Influence Detection",

            "topic": topic,

            "data": {
                "total_nodes": G.number_of_nodes(),

                "total_connections": G.number_of_edges(),

                "top_influencers": top_influencers
            },

            "analysis_summary":
                "Influencers were identified using weighted "
                "PageRank graph analysis based on interaction strength."
        }


influence_service = InfluenceService()