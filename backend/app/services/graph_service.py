def build_graph(content: str, reposts: int):
    nodes = []
    edges = []

    # Root post node
    root = "Post_0"
    nodes.append(root)

    # Generate user nodes
    for i in range(1, reposts + 1):
        user = f"User_{i}"
        nodes.append(user)

        # Edge from post to user
        edges.append({
            "source": root,
            "target": user
        })

    # Simulate propagation chain
    for i in range(1, reposts):
        edges.append({
            "source": f"User_{i}",
            "target": f"User_{i+1}"
        })

    return {
        "nodes": nodes,
        "edges": edges
    }