import random


def build_graph(content: str, reposts: int):
    nodes = []
    edges = []

    root_id = "Post_0"

    nodes.append({
        "id": root_id,
        "label": "Source Post",
        "type": "source",
        "color": "#ef4444",
        "size": 20
    })

    parents = [root_id]

    for i in range(1, reposts + 1):

        user_id = f"User_{i}"

        influence = round(random.uniform(0.2, 0.95), 2)

        # Classify some users as influencers
        if influence >= 0.75:
            node_type = "influencer"
            color = "#22c55e"   # Green
            size = 16
        else:
            node_type = "user"
            color = "#3b82f6"   # Blue
            size = 12

        nodes.append({
            "id": user_id,
            "label": f"User {i}",
            "type": node_type,
            "color": color,
            "size": size,
            "followers": random.randint(100, 5000),
            "engagement": random.randint(10, 100),
            "influence": influence
        })

        # Random parent creates a propagation tree
        parent = random.choice(parents)

        edges.append({
            "source": parent,
            "target": user_id
        })

        # Allow this user to spread the post further
        parents.append(user_id)

    return {
        "nodes": nodes,
        "edges": edges
    }