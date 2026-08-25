from collections import Counter
from statistics import mean

from app.services.graph.propagation_engine import PropagationEngine


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


def analyze_graph(graph):

    # ---------------------------------------------
    # 1. Cascade Size
    # Source node is the origin of propagation.
    # Reached nodes = total nodes excluding source.
    # ---------------------------------------------
    cascade_size = max(
        0,
        graph.number_of_nodes() - 1
    )

    # ---------------------------------------------
    # 2. Propagation depth
    # Uses actual level assigned by propagation engine.
    # ---------------------------------------------
    levels = [
        int(data.get("level", 0) or 0)
        for _, data in graph.nodes(data=True)
    ]

    max_depth = max(levels) if levels else 0

    # ---------------------------------------------
    # 3. Peak spread
    # Count nodes appearing at each propagation level.
    # Ignore source level 0.
    # ---------------------------------------------
    level_counts = Counter(
        level
        for level in levels
        if level > 0
    )

    if level_counts:
        peak_level = max(
            level_counts,
            key=level_counts.get
        )

        peak_nodes = level_counts[peak_level]
    else:
        peak_level = 0
        peak_nodes = 0

    # ---------------------------------------------
    # 4. Top influential users contribution
    # Top 5 nodes based on actual influence_score.
    # ---------------------------------------------
    influences = sorted(
        [
            float(
                data.get(
                    "influence_score",
                    0
                )
                or 0
            )
            for _, data in graph.nodes(data=True)
        ],
        reverse=True,
    )

    total_influence = sum(influences)

    top_5_influence = sum(
        influences[:5]
    )

    if total_influence > 0:
        top_influential_contribution = (
            top_5_influence
            / total_influence
        ) * 100
    else:
        top_influential_contribution = 0

    # ---------------------------------------------
    # 5. Misinformation spread rate
    # Average newly reached nodes per propagation step.
    # ---------------------------------------------
    if max_depth > 0:
        spread_rate = (
            cascade_size
            / max_depth
        )
    else:
        spread_rate = 0

    return {
        "cascade_size": cascade_size,
        "max_depth": max_depth,
        "peak_level": peak_level,
        "peak_nodes": peak_nodes,
        "top_influential_contribution":
            round(
                top_influential_contribution,
                2
            ),
        "spread_rate":
            round(
                spread_rate,
                2
            ),
    }


def main():

    print("\n" + "=" * 70)
    print("AI MISINFO - PROPAGATION AND INFLUENCE ANALYSIS")
    print("=" * 70)

    results = []

    for index, test_case in enumerate(
        TEST_CASES,
        start=1
    ):

        graph = engine.generate(
            test_case["analysis"],
            test_case["engagement"],
            test_case["spread_prediction"],
        )

        metrics = analyze_graph(graph)

        metrics["scenario"] = (
            test_case["name"]
        )

        results.append(metrics)

        print(
            f"\n[{index}] "
            f"{test_case['name']}"
        )

        print(
            "Cascade Size                  : "
            f"{metrics['cascade_size']}"
        )

        print(
            "Propagation Depth             : "
            f"{metrics['max_depth']}"
        )

        print(
            "Peak Spread Level             : "
            f"{metrics['peak_level']}"
        )

        print(
            "Nodes at Peak                 : "
            f"{metrics['peak_nodes']}"
        )

        print(
            "Top 5 Influential Contribution: "
            f"{metrics['top_influential_contribution']}%"
        )

        print(
            "Spread Rate                   : "
            f"{metrics['spread_rate']} nodes/step"
        )

        print("-" * 70)

    # =================================================
    # FINAL TABLE VALUES
    # =================================================

    cascade_sizes = [
        result["cascade_size"]
        for result in results
    ]

    depths = [
        result["max_depth"]
        for result in results
    ]

    peak_levels = [
        result["peak_level"]
        for result in results
    ]

    top_contributions = [
        result[
            "top_influential_contribution"
        ]
        for result in results
    ]

    spread_rates = [
        result["spread_rate"]
        for result in results
    ]

    print("\n" + "=" * 70)
    print("TABLE IV VALUES")
    print("PROPAGATION AND INFLUENCE ANALYSIS")
    print("=" * 70)

    print(
        f"\nAverage Cascade Size: "
        f"{mean(cascade_sizes):.2f} nodes"
    )

    print(
        f"Maximum Cascade Size: "
        f"{max(cascade_sizes)} nodes"
    )

    print(
        f"Average Propagation Depth: "
        f"{mean(depths):.2f} levels"
    )

    print(
        f"Average Time to Peak Spread: "
        f"{mean(peak_levels):.2f} "
        f"propagation steps"
    )

    print(
        f"Top Influential Users Contribution: "
        f"{mean(top_contributions):.2f}%"
    )

    print(
        f"Misinformation Spread Rate: "
        f"{mean(spread_rates):.2f} "
        f"nodes/propagation step"
    )

    print("\n" + "=" * 70)
    print("SCENARIO SUMMARY")
    print("=" * 70)

    print(
        f"{'Scenario':<28}"
        f"{'Cascade':>10}"
        f"{'Depth':>8}"
        f"{'Peak':>8}"
        f"{'Top 5 %':>12}"
        f"{'Rate':>12}"
    )

    print("-" * 78)

    for result in results:

        print(
            f"{result['scenario']:<28}"
            f"{result['cascade_size']:>10}"
            f"{result['max_depth']:>8}"
            f"{result['peak_level']:>8}"
            f"{result['top_influential_contribution']:>11.2f}%"
            f"{result['spread_rate']:>11.2f}"
        )

    print("-" * 78)


if __name__ == "__main__":
    main()