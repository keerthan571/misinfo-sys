from __future__ import annotations
import random
from math import log10
from typing import Any

import networkx as nx

from .graph_config import GraphConfig


class PropagationEngine:

    def __init__(self, config: GraphConfig):
        self.config = config
        self.graph = nx.DiGraph()

    def generate(
        self,
        analysis: dict[str, Any],
        engagement: dict[str, Any],
        spread_prediction: dict[str, Any],
    ) -> nx.DiGraph:

        self.analysis = analysis
        self.engagement = engagement
        self.prediction = spread_prediction

        self.confidence = self._confidence()
        self.engagement_score = self._engagement_score()

        self.total_nodes = self._total_nodes()
        self.influencer_count = self._influencer_count()
        self.followers = self._followers()

        self._create_claim()
        self._create_source()
        self._create_fact_check()

        self._create_influencers()
        self._create_users()

        self._assign_leaders()
        self._assign_bots()
        

        self._build_propagation()

        self._validate_graph()

        return self.graph
    
    def _create_claim(self):
        self.graph.add_node(
            "claim",
            node_type="claim",
            label="Claim",
            level=0,
            text=self.analysis.get("text", "Unknown Claim"),
            claim_type=self.analysis.get("claim_type"),
            language=self.analysis.get("language"),
            sentiment=self.analysis.get("sentiment"),
            confidence=self.confidence,
            risk_level=self.analysis.get("risk_level"),
        )
    def _create_source(self) -> None:
        self.graph.add_node(
            "source",
            node_type=self.config.SOURCE_NODE,
            label="Source",
            level=1,
            prediction=self.analysis.get("prediction"),
            confidence=self.confidence,
            risk_level=self.analysis.get("risk_level"),
            sentiment=self.analysis.get("sentiment"),
            language=self.analysis.get("language"),
            claim_type=self.analysis.get("claim_type"),
            engagement_score=self.engagement_score,
            virality_score=self.prediction.get("virality_score", 0),
            spread_probability=self.prediction.get("spread_probability", 0),
            predicted_reach=self.prediction.get("predicted_reach", 0),
        )
        self.graph.add_edge(
            "claim",
            "source",
            interaction="originates",
            weight=1.0,
        )
    def _create_fact_check(self):
        self.graph.add_node(
            "fact_check",
            node_type="fact_check",
            label="Fact Check",
            level=1,
            prediction=self.analysis.get("prediction"),
            confidence=self.confidence,
            risk_level=self.analysis.get("risk_level"),
        )
        self.graph.add_edge(
            "claim",
            "fact_check",
            interaction="verified_by",
            weight=1.0,
        )
    def _create_influencers(self):
        for i in range(self.influencer_count):
            self.graph.add_node(
                f"inf_{i+1}",
                node_type=self.config.INFLUENCER_NODE,
                label=f"Influencer {i+1}",
                followers=self.followers[i],
                confidence=self.confidence,
                engagement_score=self.engagement_score,
                community=i,
                level=1,
                is_leader=False,
                is_bot=False,
                is_viral=False,
            )

    def _create_users(self):
        total_users = self.total_nodes - self.influencer_count
        community_count = self.influencer_count

        base_size = total_users // community_count
        extra = total_users % community_count

        index = self.influencer_count

        for community in range(community_count):
            size = base_size + (1 if community < extra else 0)

            for _ in range(size):
                self.graph.add_node(
                    f"user_{index}",
                    node_type=self.config.USER_NODE,
                    label=f"User {index}",
                    followers=self.followers[index],
                    confidence=self.confidence,
                    engagement_score=self.engagement_score,
                    community=community,
                    level=2,
                    is_leader=False,
                    is_bot=False,
                    is_viral=False,
                )
                index += 1

    def _confidence(self) -> float:
        confidence = float(self.analysis.get("confidence", 0)) / 100
        return max(0.0, min(1.0, confidence))

    def _engagement_score(self) -> float:
        likes = self.engagement.get("likes", 0)
        shares = self.engagement.get("shares", 0)
        comments = self.engagement.get("comments", 0)
        views = max(1, self.engagement.get("views", 1))

        weights = self.config.ENGAGEMENT_WEIGHTS

        score = (
            likes * weights["likes"]
            + shares * weights["shares"]
            + comments * weights["comments"]
        ) / views

        return round(score, 4)

    def _total_nodes(self) -> int:
        virality = float(self.prediction.get("virality_score", 0))
        reach = max(1, float(self.prediction.get("predicted_reach", 1)))

        estimate = (
            virality * 2
            + log10(reach) * 20
        ) * self.config.risk_multiplier(
            self.analysis.get("risk_level", "Low")
        )

        estimate = int(round(estimate))

        return max(
            self.config.MIN_NODES,
            min(self.config.MAX_NODES, estimate),
        )

    def _influencer_count(self) -> int:
        estimated = int(
            self.prediction.get("estimated_influencers", 2)
        )

        maximum = int(
            self.total_nodes
            * self.config.MAX_INFLUENCER_RATIO
        )

        return max(
            self.config.MIN_INFLUENCERS,
            min(estimated, maximum),
        )

    def _followers(self) -> list[int]:
        max_followers = max(
            self.prediction.get("predicted_reach", 1000),
            self.config.MIN_FOLLOWERS,
        )

        followers = []

        for i in range(self.total_nodes):
            ratio = 1 - (i / max(1, self.total_nodes - 1))
            value = int(
                self.config.MIN_FOLLOWERS
                + (max_followers - self.config.MIN_FOLLOWERS)
                * (ratio ** 2)
            )
            followers.append(value)

        return followers

    def _assign_leaders(self):
        communities = {}

        for node, data in self.graph.nodes(data=True):
            if data["node_type"] != self.config.USER_NODE:
                continue

            communities.setdefault(data["community"], []).append(node)

        for users in communities.values():
            leader = max(
                users,
                key=lambda node: self.graph.nodes[node]["followers"],
            )
            self.graph.nodes[leader]["is_leader"] = True
    def _bot_count(self) -> int:
    
        risk = self.analysis.get("risk_level", "Low").lower()
        virality = float(
            self.prediction.get("virality_score", 0)
        )
        spread = float(
            self.prediction.get("spread_probability", 0)
        ) / 100

        base = {
            "low": 0.03,
            "medium": 0.07,
            "high": 0.12,
        }.get(risk, 0.05)

        multiplier = (
            1
            + virality / 200
            + spread / 2
            + self.engagement_score
        )

        percentage = min(0.35, base * multiplier)

        return max(
            1,
            int(
                percentage
                * (
                    self.total_nodes
                    - self.influencer_count
                )
            ),
        )
    def _assign_bots(self):
        
        required = self._bot_count()

        users = [
            node
            for node, data in self.graph.nodes(data=True)
            if data["node_type"] == self.config.USER_NODE
        ]

        users.sort(
            key=lambda node: (
                self.graph.nodes[node]["followers"],
                self.graph.nodes[node]["engagement_score"],
            ),
            reverse=True,
        )

        for node in users[:required]:
            self.graph.nodes[node]["is_bot"] = True
    def _build_default_graph(self):
        self._connect_source()
        self._connect_leaders()
        self._build_cascades()
        self._connect_bridges()    
           
    def _build_propagation(self):
        platform = (
            self.analysis.get("platform", "generic")
            .strip()
            .lower()
        )

        if platform in ["twitter", "x"]:
            self._build_twitter_graph()

        elif platform == "facebook":
            self._build_facebook_graph()

        elif platform == "instagram":
            self._build_instagram_graph()

        elif platform == "whatsapp":
            self._build_whatsapp_graph()

        else:
            self._build_default_graph()


    def _connect_source(self):
        weight = self._edge_weight()

        influencers = [
            node
            for node, data in self.graph.nodes(data=True)
            if data["node_type"] == self.config.INFLUENCER_NODE
        ]

        for influencer in influencers:
            self.graph.add_edge(
                "source",
                influencer,
                weight=weight,
                interaction=self.config.PUBLISH_EDGE,
            )


    def _connect_leaders(self):
        weight = self._edge_weight()

        influencers = sorted(
            [
                node
                for node, data in self.graph.nodes(data=True)
                if data["node_type"] == self.config.INFLUENCER_NODE
            ]
        )

        leaders = sorted(
            (
                node
                for node, data in self.graph.nodes(data=True)
                if data["node_type"] == self.config.USER_NODE
                and data["is_leader"]
            ),
            key=lambda node: self.graph.nodes[node]["community"],
        )

        for influencer, leader in zip(influencers, leaders):
            self.graph.add_edge(
                influencer,
                leader,
                weight=weight,
                interaction=self.config.SHARE_EDGE,
            )

    def _build_twitter_graph(self):
        self._connect_source()
        self._connect_leaders()
        self._build_cascades()
        self._connect_bridges()
        self._random_cross_links(3)
        
    def _build_facebook_graph(self):
        self._connect_source()
        self._connect_leaders()
        self._build_cascades()
        
    def _build_instagram_graph(self):
        self._connect_source()
        self._connect_leaders()
        
    def _build_whatsapp_graph(self):
        self._connect_source()
        self._build_cascades()
    
    def _build_cascades(self):
        weight = self._edge_weight()

        communities = {}

        for node, data in self.graph.nodes(data=True):
            if data["node_type"] != self.config.USER_NODE:
                continue

            communities.setdefault(data["community"], []).append(node)

        for users in communities.values():

            users.sort(
                key=lambda node: (
                    not self.graph.nodes[node]["is_leader"],
                    -self.graph.nodes[node]["followers"],
                )
            )

            # Leader -> User chain
            for i in range(len(users) - 1):
                self.graph.add_edge(
                    users[i],
                    users[i + 1],
                    weight=weight,
                    interaction=self.config.CASCADE_EDGE,
                )

            # Additional local sharing
            for i in range(len(users)):
                for j in range(i + 2, min(i + 4, len(users))):
                    self.graph.add_edge(
                        users[i],
                        users[j],
                        weight=round(weight * 0.8, 3),
                        interaction=self.config.SHARE_EDGE,
                    )


    def _connect_bridges(self):
        weight = self._edge_weight()

        communities = {}

        for node, data in self.graph.nodes(data=True):
            if data["node_type"] != self.config.USER_NODE:
                continue

            communities.setdefault(data["community"], []).append(node)

        bridge_users = []

        for users in communities.values():

            users.sort(
                key=lambda node: self.graph.nodes[node]["followers"],
                reverse=True,
            )

            if len(users) >= 2:
                bridge_users.append(users[1])

        for i in range(len(bridge_users) - 1):
    
            src = bridge_users[i]
            dst = bridge_users[i + 1]

            if nx.has_path(self.graph, dst, src):
                continue

            self.graph.add_edge(
                src,
                dst,
                weight=weight,
                interaction=self.config.BRIDGE_EDGE,
            )
            weight=weight,
            interaction=self.config.BRIDGE_EDGE,
    
    def _random_cross_links(self, per_community):
    
        users=[
            node
            for node,data in self.graph.nodes(data=True)
            if data["node_type"]==self.config.USER_NODE
        ]

        if len(users)<2:
            return

        for node in users:

            community=self.graph.nodes[node]["community"]

            others=[
                u
                for u in users
                if self.graph.nodes[u]["community"]>community
            ]

            random.shuffle(others)

            for neighbour in others[:per_community]:
                if (
                    not nx.has_path(self.graph, neighbour, node)
                    and not nx.has_path(self.graph, node, neighbour)
                ):
                    self.graph.add_edge(
                        node,
                        neighbour,
                        weight=round(self._edge_weight()*0.7,3),
                        interaction="cross_share",
                    )
    
    def _edge_weight(self) -> float:
        confidence = self.confidence
        engagement = self.engagement_score
        spread = float(
            self.prediction.get("spread_probability", 0)
        ) / 100

        weight = (
            confidence * 0.40
            + engagement * 0.30
            + spread * 0.30
        )

        return self._clamp(
            round(weight, 3),
            self.config.MIN_EDGE_WEIGHT,
            self.config.MAX_EDGE_WEIGHT,
        )


    def _clamp(
        self,
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        return max(minimum, min(maximum, value))

    def _amplify_bots(self):
        multiplier=self.config.bot_edge_multiplier(
            self.analysis.get("risk_level","Low")
        )

        bots=[
            node
            for node,data in self.graph.nodes(data=True)
            if data.get("is_bot",False)
        ]

        for bot in bots:

            community=self.graph.nodes[bot]["community"]

            neighbours=[
                node
                for node,data in self.graph.nodes(data=True)
                if(
                    data["node_type"]==self.config.USER_NODE
                    and data["community"]==community
                    and node!=bot
                )
            ]

            neighbours.sort(
                key=lambda node:self.graph.nodes[node]["followers"],
                reverse=True,
            )

            for neighbour in neighbours[:3]:

                # Don't create cycles
                if (
                    nx.has_path(self.graph, neighbour, bot)
                    or nx.has_path(self.graph, bot, neighbour)
                ):
                    continue

                self.graph.add_edge(
                    bot,
                    neighbour,
                    weight=round(
                        self._edge_weight()*multiplier,
                        3,
                    ),
                    interaction=self.config.BOT_EDGE,
                )    
    
    def _ensure_connectivity(self):
    
        for node, data in self.graph.nodes(data=True):

            if data["node_type"] != self.config.USER_NODE:
                continue

            if self.graph.in_degree(node) > 0:
                continue

            leaders = [
                n
                for n, d in self.graph.nodes(data=True)
                if (
                    d["node_type"] == self.config.USER_NODE
                    and d["community"] == data["community"]
                    and d["is_leader"]
                )
            ]

            if leaders:

                if (
                    not nx.has_path(self.graph, node, leaders[0])
                    and not nx.has_path(self.graph, leaders[0], node)
                ):
                    self.graph.add_edge(
                    leaders[0],
                    node,
                    weight=self._edge_weight(),
                    interaction=self.config.SHARE_EDGE,
                )


    def _validate_graph(self):
        self._ensure_connectivity()
        self._amplify_bots()
        print("NODES:", self.graph.number_of_nodes())
        print("EDGES:", self.graph.number_of_edges())
        print(list(self.graph.edges()))
        print("Cycles:")
        for cycle in nx.simple_cycles(self.graph):
            print(cycle)
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError(
                "Propagation graph contains cycles."
            )