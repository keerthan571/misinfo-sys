from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard")
def dashboard_analytics():

    return {

        "prediction_summary": {
            "predicted_reach": 12450,
            "risk_level": "High",
            "confidence": 87
        },

        "network_statistics": {
            "total_nodes": 7,
            "total_connections": 8,
            "average_influence_score": 16.71
        },

        "risk_distribution": [
            {
                "risk": "Low",
                "count": 12
            },
            {
                "risk": "Moderate",
                "count": 8
            },
            {
                "risk": "High",
                "count": 5
            },
            {
                "risk": "Critical",
                "count": 2
            }
        ],

        "top_influencers": [
            {
                "name": "Frank",
                "score": 25.61
            },
            {
                "name": "George",
                "score": 18.87
            },
            {
                "name": "David",
                "score": 15.90
            }
        ]
    }