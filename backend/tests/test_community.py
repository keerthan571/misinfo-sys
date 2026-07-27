from app.services.graph.graph_config import GraphConfig
from app.services.graph.propagation_engine import PropagationEngine
from app.services.graph.community_detector import CommunityDetector

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

detector = CommunityDetector(graph)

result = detector.analyze()

print("\n===== COMMUNITIES =====")

for community in result["communities"]:
    print(community)

print("\n===== SUMMARY =====")

for item in result["summary"]:
    print(item)