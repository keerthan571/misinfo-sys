import networkx as nx


class InfluenceService:

    def __init__(self):
        pass

    def classify_influencer(self, score):

        if score >= 25:
            return "Mega Influencer"

        elif score >= 15:
            return "Strong Influencer"

        elif score >= 8:
            return "Active User"

        return "Normal User"

    def detect_influencers(self, topic: str):

        G = nx.DiGraph()

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

        for source, target, weight in weighted_edges:
            G.add_edge(source, target, weight=weight)

        follower_data = {
            "Alice": 85000,
            "Bob": 45000,
            "Charlie": 28000,
            "David": 15000,
            "Eve": 22000,
            "Frank": 8000,
            "George": 5000
        }

        pagerank_scores = nx.pagerank(
            G,
            weight="weight"
        )

        sorted_users = sorted(
            pagerank_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_influencers = []

        for user, score in sorted_users[:5]:

            influence_score = round(
                score * 100,
                2
            )

            followers = follower_data.get(
                user,
                1000
            )

            connections = len(
                list(G.neighbors(user))
            )

            top_influencers.append({
                "user_id": user.lower(),
                "name": user,
                "influence_score": influence_score,
                "followers": followers,
                "connections": connections,
                "category": self.classify_influencer(
                    influence_score
                )
            })

        total_nodes = G.number_of_nodes()

        total_connections = G.number_of_edges()

        average_influence = round(
            sum(
                influencer["influence_score"]
                for influencer in top_influencers
            ) / len(top_influencers),
            2
        )

        highest = top_influencers[0]["name"]

        summary = (
            f"{highest} emerged as the most influential "
            f"user in the misinformation network based "
            f"on weighted PageRank analysis."
        )

        return {
            "status": "success",
            "module": "Influence Detection",
            "topic": topic,

            "network_statistics": {
                "total_nodes": total_nodes,
                "total_connections": total_connections,
                "average_influence_score": average_influence
            },

            "top_influencers": top_influencers,

            "analysis_summary": summary
        }


influence_service = InfluenceService()