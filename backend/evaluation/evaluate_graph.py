from app.services.graph.propagation_engine import PropagationEngine
import networkx as nx


engine = PropagationEngine()


TEST_CASES = [
    {
        "name": "Low Spread",
        "analysis": {
            "platform": "Twitter",
            "publisher": "Test Source",
        },
        "engagement": {
            "followers": 5000,
        },
        "spread_prediction": {
            "risk_level": "Low",
            "virality_score": 20,
            "spread_probability": 20,
            "predicted_reach": 5000,
        },
    },
    {
        "name": "Moderate Spread",
        "analysis": {
            "platform": "Twitter",
            "publisher": "Test Source",
        },
        "engagement": {
            "followers": 25000,
        },
        "spread_prediction": {
            "risk_level": "Medium",
            "virality_score": 45,
            "spread_probability": 50,
            "predicted_reach": 50000,
        },
    },
    {
        "name": "High Spread",
        "analysis": {
            "platform": "Twitter",
            "publisher": "Test Source",
        },
        "engagement": {
            "followers": 100000,
        },
        "spread_prediction": {
            "risk_level": "Medium",
            "virality_score": 70,
            "spread_probability": 75,
            "predicted_reach": 250000,
        },
    },
    {
        "name": "Viral Misinformation",
        "analysis": {
            "platform": "Facebook",
            "publisher": "Test Source",
        },
        "engagement": {
            "followers": 500000,
        },
        "spread_prediction": {
            "risk_level": "High",
            "virality_score": 90,
            "spread_probability": 92,
            "predicted_reach": 1000000,
        },
    },
    {
        "name": "High Risk Amplification",
        "analysis": {
            "platform": "Twitter",
            "publisher": "Test Source",
        },
        "engagement": {
            "followers": 750000,
        },
        "spread_prediction": {
            "risk_level": "High",
            "virality_score": 95,
            "spread_probability": 96,
            "predicted_reach": 2000000,
        },
    },
]


def calculate_metrics(graph):

    nodes = graph.number_of_nodes()
    edges = graph.number_of_edges()

    density = (
        nx.density(graph)
        if nodes > 1
        else 0
    )

    connected_components = (
        nx.number_weakly_connected_components(graph)
        if nodes > 0
        else 0
    )

    leaders = sum(
        1
        for _, data in graph.nodes(data=True)
        if data.get("is_leader")
    )

    bots = sum(
        1
        for _, data in graph.nodes(data=True)
        if data.get("is_bot")
    )

    viral_nodes = sum(
        1
        for _, data in graph.nodes(data=True)
        if data.get("is_viral")
    )

    influence_values = [
        float(data.get("influence_score", 0) or 0)
        for _, data in graph.nodes(data=True)
    ]

    average_influence = (
        sum(influence_values) / len(influence_values)
        if influence_values
        else 0
    )

    levels = [
        int(data.get("level", 0) or 0)
        for _, data in graph.nodes(data=True)
    ]

    max_propagation_depth = (
        max(levels)
        if levels
        else 0
    )

    spread_efficiency = (
        min(
            (edges / (nodes - 1)) * 100,
            100
        )
        if nodes > 1
        else 0
    )

    return {
        "nodes": nodes,
        "edges": edges,
        "density": round(density, 4),
        "components": connected_components,
        "leaders": leaders,
        "bots": bots,
        "viral_nodes": viral_nodes,
        "average_influence": round(
            average_influence,
            2
        ),
        "max_depth": max_propagation_depth,
        "spread_efficiency": round(
            spread_efficiency,
            2
        ),
    }


def graphs_are_identical(graph1, graph2):

    if set(graph1.nodes()) != set(graph2.nodes()):
        return False

    if set(graph1.edges()) != set(graph2.edges()):
        return False

    for node in graph1.nodes():

        data1 = graph1.nodes[node]
        data2 = graph2.nodes[node]

        if data1 != data2:
            return False

    for edge in graph1.edges():

        data1 = graph1.edges[edge]
        data2 = graph2.edges[edge]

        if data1 != data2:
            return False

    return True


def main():

    print("\n" + "=" * 75)
    print("AI MISINFO - PROPAGATION GRAPH EVALUATION")
    print("=" * 75)

    results = []

    reproducible_count = 0

    for index, test_case in enumerate(
        TEST_CASES,
        start=1
    ):

        print(f"\n[{index}] {test_case['name']}")

        graph1 = engine.generate(
            test_case["analysis"],
            test_case["engagement"],
            test_case["spread_prediction"],
        )

        # Generate again with exactly the same input
        graph2 = engine.generate(
            test_case["analysis"],
            test_case["engagement"],
            test_case["spread_prediction"],
        )

        reproducible = graphs_are_identical(
            graph1,
            graph2
        )

        if reproducible:
            reproducible_count += 1

        metrics = calculate_metrics(graph1)

        result = {
            "name": test_case["name"],
            "risk_level":
                test_case["spread_prediction"]["risk_level"],
            "virality":
                test_case["spread_prediction"]["virality_score"],
            "spread_probability":
                test_case["spread_prediction"]["spread_probability"],
            "reproducible": reproducible,
            **metrics,
        }

        results.append(result)

        print(
            f"Risk Level           : "
            f"{result['risk_level']}"
        )

        print(
            f"Virality Score       : "
            f"{result['virality']}"
        )

        print(
            f"Spread Probability   : "
            f"{result['spread_probability']}"
        )

        print(
            f"Nodes                : "
            f"{result['nodes']}"
        )

        print(
            f"Edges                : "
            f"{result['edges']}"
        )

        print(
            f"Density              : "
            f"{result['density']}"
        )

        print(
            f"Connected Components : "
            f"{result['components']}"
        )

        print(
            f"Leaders              : "
            f"{result['leaders']}"
        )

        print(
            f"Bots                 : "
            f"{result['bots']}"
        )

        print(
            f"Viral Nodes          : "
            f"{result['viral_nodes']}"
        )

        print(
            f"Average Influence    : "
            f"{result['average_influence']}"
        )

        print(
            f"Max Propagation Depth: "
            f"{result['max_depth']}"
        )

        print(
            f"Spread Efficiency    : "
            f"{result['spread_efficiency']}%"
        )

        print(
            f"Reproducible         : "
            f"{'PASS' if reproducible else 'FAIL'}"
        )

        print("-" * 75)

    print("\n" + "=" * 75)
    print("FINAL GRAPH EVALUATION RESULTS")
    print("=" * 75)

    print(
        f"\nTotal Test Cases          : "
        f"{len(TEST_CASES)}"
    )

    print(
        f"Reproducible Test Cases   : "
        f"{reproducible_count}/{len(TEST_CASES)}"
    )

    reproducibility_rate = (
        reproducible_count
        / len(TEST_CASES)
        * 100
    )

    print(
        f"Reproducibility Rate      : "
        f"{reproducibility_rate:.2f}%"
    )

    print("\nSUMMARY TABLE")

    print("-" * 140)

    print(
        f"{'Scenario':<25}"
        f"{'Nodes':>8}"
        f"{'Edges':>8}"
        f"{'Density':>10}"
        f"{'Leaders':>10}"
        f"{'Bots':>8}"
        f"{'Viral':>8}"
        f"{'Depth':>8}"
        f"{'Efficiency':>14}"
        f"{'Reproducible':>16}"
    )

    print("-" * 140)

    for result in results:

        print(
            f"{result['name']:<25}"
            f"{result['nodes']:>8}"
            f"{result['edges']:>8}"
            f"{result['density']:>10.4f}"
            f"{result['leaders']:>10}"
            f"{result['bots']:>8}"
            f"{result['viral_nodes']:>8}"
            f"{result['max_depth']:>8}"
            f"{result['spread_efficiency']:>13.2f}%"
            f"{'PASS' if result['reproducible'] else 'FAIL':>16}"
        )

    print("-" * 140)


if __name__ == "__main__":
    main()