from app.services.graph.graph_generator import GraphGenerator


def build_graph(analysis_data: dict):
    """
    Main coordinator for the Graph Module.

    Future flow:

    GraphGenerator
            ↓
    InfluenceDetector
            ↓
    CommunityDetector
            ↓
    GraphStatistics
            ↓
    GraphSerializer
    """

    generator = GraphGenerator()

    graph = generator.generate(analysis_data)

    return graph