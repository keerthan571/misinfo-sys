# Starter code for Neo4j Integration
# Students will need to install Neo4j locally or use AuraDB

# from neo4j import GraphDatabase

class GraphService:
    def __init__(self):
        # Dummy initialization. 
        # Replace with: self.driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        self.connected = False

    def get_propagation_graph(self, post_id: str):
        """
        Returns a dummy graph showing how a piece of info spread.
        Students should replace this with actual Cypher queries.
        """
        # Dummy graph data
        return {
            "nodes": [
                {"id": "user1", "label": "User", "name": "Alice"},
                {"id": "user2", "label": "User", "name": "Bob"},
                {"id": "user3", "label": "User", "name": "Charlie"},
                {"id": "post1", "label": "Post", "content": "Fake news about 5G"}
            ],
            "links": [
                {"source": "user1", "target": "post1", "type": "CREATED"},
                {"source": "user2", "target": "post1", "type": "SHARED"},
                {"source": "user3", "target": "user2", "type": "RETWEETED"}
            ]
        }

graph_service = GraphService()
