from app.services.graph.graph_config import GraphConfig
from app.services.graph.propagation_engine import PropagationEngine

config = GraphConfig()
engine = PropagationEngine(config)

analysis = {
    "prediction": "Fake",
    "confidence": 96.4,
    "risk_level": "High",
    "claim_type": "Political",
    "language": "English",
    "sentiment": "Negative",
}

engagement = {
    "likes": 1500,
    "shares": 800,
    "comments": 350,
    "views": 50000,
}

spread_prediction = {
    "virality_score": 88,
    "spread_probability": 92,
    "predicted_reach": 500000,
    "estimated_influencers": 6,
}

graph = engine.generate(
    analysis,
    engagement,
    spread_prediction,
)

print("=" * 50)
print("Nodes :", graph.number_of_nodes())
print("Edges :", graph.number_of_edges())
print("=" * 50)

for node, data in graph.nodes(data=True):
    print(node, data)

print("=" * 50)

for u, v, data in graph.edges(data=True):
    print(f"{u} -> {v} : {data}")