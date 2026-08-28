import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else BASE_DIR / "actual_graph.json"
)

OUTPUT_FILE = (
    Path(sys.argv[2])
    if len(sys.argv) > 2
    else BASE_DIR / "fig4_propagation_network.png"
)


# ============================================================
# LOAD ACTUAL PROJECT GRAPH
# ============================================================

def load_graph_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "\nActual graph JSON was not found.\n\n"
            f"Expected file:\n{INPUT_FILE}\n\n"
            "The file should contain either:\n"
            "1. { 'graph': { 'nodes': [...], 'edges': [...] } }\n"
            "or:\n"
            "2. { 'nodes': [...], 'edges': [...] }\n"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        payload = json.load(file)

    graph_data = payload.get(
        "graph",
        payload,
    )

    nodes = graph_data.get(
        "nodes",
        [],
    )

    edges = graph_data.get(
        "edges",
        [],
    )

    if not nodes:
        raise ValueError(
            "No nodes found in the graph JSON."
        )

    return nodes, edges


# ============================================================
# BUILD NETWORKX GRAPH
# ============================================================

def build_graph(nodes, edges):

    graph = nx.DiGraph()

    for node in nodes:

        node_id = str(
            node.get(
                "id",
                ""
            )
        )

        if not node_id:
            continue

        graph.add_node(
            node_id,
            **node,
        )

    for edge in edges:

        source = str(
            edge.get(
                "source",
                ""
            )
        )

        target = str(
            edge.get(
                "target",
                ""
            )
        )

        if (
            not source
            or not target
        ):
            continue

        if (
            source not in graph
            or target not in graph
        ):
            continue

        graph.add_edge(
            source,
            target,
            **edge,
        )

    return graph


# ============================================================
# NODE VALUE HELPERS
# ============================================================

def number(value, default=0.0):

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def get_node_type(data):

    return str(
        data.get(
            "nodeType",
            data.get(
                "node_type",
                data.get(
                    "type",
                    "user",
                ),
            ),
        )
    ).lower()


def get_level(data):

    try:
        return int(
            data.get(
                "level",
                0,
            )
            or 0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0


def get_influence(data):

    # Prefer the actual influence values
    # already supplied by your backend.

    for key in (
        "networkInfluence",
        "influenceScore",
        "influence_score",
        "pageRankScore",
        "pageRank",
    ):

        value = number(
            data.get(key),
            0.0,
        )

        if value > 0:
            return value

    return 0.0


# ============================================================
# HIERARCHICAL PROPAGATION LAYOUT
# ============================================================

def propagation_layout(graph):

    levels = {}

    for node, data in graph.nodes(
        data=True
    ):

        level = get_level(data)

        levels.setdefault(
            level,
            [],
        ).append(node)

    # If any node has no useful level,
    # calculate a fallback propagation distance.
    source_nodes = [
        node
        for node, data in graph.nodes(
            data=True
        )
        if (
            get_node_type(data) == "source"
            or data.get("role") == "source"
        )
    ]

    if source_nodes:

        source = source_nodes[0]

    else:

        source = next(
            iter(graph.nodes)
        )

    distances = nx.single_source_shortest_path_length(
        graph,
        source,
    )

    max_level = max(
        levels.keys(),
        default=0,
    )

    # Correct missing / inconsistent levels
    # using actual graph propagation distance.
    for node in graph.nodes:

        current_level = get_level(
            graph.nodes[node]
        )

        if (
            current_level == 0
            and node != source
        ):

            current_level = distances.get(
                node,
                max_level + 1,
            )

        levels.setdefault(
            current_level,
            [],
        )

        if node not in levels[current_level]:

            levels[current_level].append(
                node
            )

    # Remove duplicates.
    cleaned_levels = {}

    for level, node_list in levels.items():

        unique_nodes = []

        seen = set()

        for node in node_list:

            if node not in seen:

                seen.add(node)

                unique_nodes.append(node)

        cleaned_levels[level] = unique_nodes

    levels = cleaned_levels

    pos = {}

    max_width = max(
        (
            len(node_list)
            for node_list in levels.values()
        ),
        default=1,
    )

    horizontal_span = max(
        12.0,
        max_width * 1.35,
    )

    vertical_gap = 1.8

    for level in sorted(
        levels.keys()
    ):

        node_list = levels[level]

        # Sort deterministically so the same
        # graph always produces the same figure.
        node_list = sorted(
            node_list
        )

        count = len(node_list)

        if count == 1:

            positions = [
                0.0
            ]

        else:

            spacing = (
                horizontal_span
                / max(
                    count - 1,
                    1,
                )
            )

            start = (
                -horizontal_span / 2
            )

            positions = [
                start + index * spacing
                for index in range(count)
            ]

        for node, x in zip(
            node_list,
            positions,
        ):

            pos[node] = (
                x,
                -level * vertical_gap,
            )

    return pos


# ============================================================
# CENTRALITY
# ============================================================

def calculate_centrality(graph):

    if graph.number_of_nodes() <= 1:

        return {
            node: 0.0
            for node in graph.nodes
        }

    try:

        page_rank = nx.pagerank(
            graph,
            alpha=0.85,
        )

    except Exception:

        page_rank = {
            node: 0.0
            for node in graph.nodes
        }

    return page_rank


# ============================================================
# DRAW FIGURE
# ============================================================

def generate_figure(graph):

    pos = propagation_layout(
        graph
    )

    page_rank = calculate_centrality(
        graph
    )

    # --------------------------------------------------------
    # Determine actual influential nodes
    # --------------------------------------------------------

    influence_values = {}

    for node, data in graph.nodes(
        data=True
    ):

        backend_influence = get_influence(
            data
        )

        centrality = page_rank.get(
            node,
            0.0,
        )

        # Use actual backend influence when present.
        # PageRank is only used as an additional
        # network-centrality signal.
        score = (
            backend_influence
            if backend_influence > 0
            else centrality
        )

        influence_values[node] = score

    ranked_nodes = sorted(
        graph.nodes,
        key=lambda node: (
            influence_values.get(
                node,
                0.0,
            ),
            page_rank.get(
                node,
                0.0,
            ),
        ),
        reverse=True,
    )

    # Source should not occupy all "top user"
    # highlight positions.
    ranked_users = [
        node
        for node in ranked_nodes
        if get_node_type(
            graph.nodes[node]
        ) != "source"
    ]

    top_count = min(
        5,
        len(ranked_users),
    )

    top_influential = set(
        ranked_users[:top_count]
    )

    # --------------------------------------------------------
    # Figure
    # --------------------------------------------------------

    plt.figure(
        figsize=(
            7.16,
            5.4,
        )
    )

    ax = plt.gca()

    # --------------------------------------------------------
    # Draw actual propagation edges
    # --------------------------------------------------------

    nx.draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=10,
        width=0.8,
        alpha=0.65,
        connectionstyle=(
            "arc3,rad=0.03"
        ),
    )

    # --------------------------------------------------------
    # Separate nodes by actual type
    # --------------------------------------------------------

    source_nodes = []
    influencer_nodes = []
    bot_nodes = []
    user_nodes = []

    for node, data in graph.nodes(
        data=True
    ):

        node_type = get_node_type(
            data
        )

        if (
            node_type == "source"
            or data.get("role") == "source"
        ):

            source_nodes.append(
                node
            )

        elif (
            node_type == "influencer"
            or data.get("isLeader")
            or data.get("is_leader")
        ):

            influencer_nodes.append(
                node
            )

        elif (
            node_type == "bot"
            or data.get("isBot")
            or data.get("is_bot")
        ):

            bot_nodes.append(
                node
            )

        else:

            user_nodes.append(
                node
            )

    # --------------------------------------------------------
    # Node sizes from actual influence
    # --------------------------------------------------------

    values = list(
        influence_values.values()
    )

    min_value = min(
        values,
        default=0.0,
    )

    max_value = max(
        values,
        default=1.0,
    )

    def node_size(node):

        value = influence_values.get(
            node,
            0.0,
        )

        if max_value == min_value:

            return 260

        normalized = (
            (value - min_value)
            / (max_value - min_value)
        )

        return (
            170
            + normalized * 430
        )

    # --------------------------------------------------------
    # Draw regular users
    # --------------------------------------------------------

    regular_users = [
        node
        for node in user_nodes
        if node not in top_influential
    ]

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=regular_users,
        node_size=[
            node_size(node)
            for node in regular_users
        ],
        node_shape="o",
        alpha=0.95,
        linewidths=0.8,
        edgecolors="black",
        ax=ax,
    )

    # --------------------------------------------------------
    # Influencer / leader nodes
    # --------------------------------------------------------

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=influencer_nodes,
        node_size=[
            node_size(node)
            for node in influencer_nodes
        ],
        node_shape="s",
        alpha=0.98,
        linewidths=1.2,
        edgecolors="black",
        ax=ax,
    )

    # --------------------------------------------------------
    # Bots
    # --------------------------------------------------------

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=bot_nodes,
        node_size=[
            node_size(node)
            for node in bot_nodes
        ],
        node_shape="D",
        alpha=0.9,
        linewidths=0.8,
        edgecolors="black",
        ax=ax,
    )

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=source_nodes,
        node_size=[
            max(
                600,
                node_size(node) + 200,
            )
            for node in source_nodes
        ],
        node_shape="*",
        alpha=1.0,
        linewidths=1.2,
        edgecolors="black",
        ax=ax,
    )

    # --------------------------------------------------------
    # Top influential / high-centrality users
    # --------------------------------------------------------

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=list(
            top_influential
        ),
        node_size=[
            node_size(node) + 100
            for node in top_influential
        ],
        node_shape="o",
        alpha=1.0,
        linewidths=2.0,
        edgecolors="black",
        ax=ax,
    )

    # --------------------------------------------------------
    # Clean publication labels
    # --------------------------------------------------------

    labels = {}

    for node, data in graph.nodes(
        data=True
    ):

        node_type = get_node_type(
            data
        )

        if node_type == "source":

            labels[node] = "Source"

        elif node in top_influential:

            label = str(
                data.get(
                    "label",
                    data.get(
                        "displayName",
                        node,
                    ),
                )
            )

            # Keep labels compact for IEEE scale.
            labels[node] = (
                label[:14]
            )

    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        font_size=6,
        font_weight="bold",
        ax=ax,
    )

    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    legend_items = [
        Line2D(
            [0],
            [0],
            marker="*",
            linestyle="None",
            markeredgecolor="black",
            markersize=11,
            label="Original source",
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            linestyle="None",
            markeredgecolor="black",
            markersize=8,
            label="Influential / leader account",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markeredgecolor="black",
            markersize=7,
            label="User account",
        ),
        Line2D(
            [0],
            [0],
            marker="D",
            linestyle="None",
            markeredgecolor="black",
            markersize=7,
            label="Automated account",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markeredgecolor="black",
            markerfacecolor="white",
            markeredgewidth=2,
            markersize=9,
            label="Top influential user",
        ),
    ]

    ax.legend(
        handles=legend_items,
        loc="upper right",
        fontsize=6,
        frameon=True,
    )

    # --------------------------------------------------------
    # Final academic styling
    # --------------------------------------------------------

    ax.set_axis_off()

    plt.tight_layout(
        pad=0.25
    )

    plt.savefig(
        OUTPUT_FILE,
        dpi=600,
        bbox_inches="tight",
        pad_inches=0.03,
    )

    plt.close()

    return top_influential


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 65
    )

    print(
        "GENERATING IEEE FIG. 4"
    )

    print(
        "=" * 65
    )

    print(
        f"\nInput : {INPUT_FILE}"
    )

    nodes, edges = load_graph_data()

    graph = build_graph(
        nodes,
        edges,
    )

    print(
        f"Nodes : "
        f"{graph.number_of_nodes()}"
    )

    print(
        f"Edges : "
        f"{graph.number_of_edges()}"
    )

    top_influential = generate_figure(
        graph
    )

    print(
        "\nTop influential nodes "
        "highlighted:"
    )

    for index, node in enumerate(
        sorted(top_influential),
        start=1,
    ):

        data = graph.nodes[node]

        label = data.get(
            "label",
            data.get(
                "displayName",
                node,
            ),
        )

        print(
            f"{index}. {label} "
            f"({node})"
        )

    print(
        f"\nFigure saved successfully:\n"
        f"{OUTPUT_FILE}"
    )

    print(
        "\n"
        + "=" * 65
    )


if __name__ == "__main__":
    main()