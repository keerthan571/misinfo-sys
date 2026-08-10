from __future__ import annotations

import hashlib
import math
import random
from typing import Any

import networkx as nx

from app.services.graph.graph_config import GraphConfig


class PropagationEngine:
    def __init__(self, config: GraphConfig | None = None) -> None:
        self.config = config or GraphConfig()

    def generate(
        self,
        analysis: dict[str, Any],
        engagement: dict[str, Any],
        spread_prediction: dict[str, Any],
    ) -> nx.DiGraph:
        seed = self._build_seed(
            analysis,
            engagement,
            spread_prediction,
        )
        rng = random.Random(seed)

        platform = str(
            analysis.get("platform", "Unknown")
        )

        publisher = (
            analysis.get("publisher")
            or analysis.get("source")
            or analysis.get("source_name")
            or analysis.get("publisher_name")
            or analysis.get("author")
            or None
        )

        if isinstance(publisher, dict):
            publisher = (
                publisher.get("name")
                or publisher.get("displayname")
                or publisher.get("username")
                or publisher.get("handle")
            )

        risk_level = self._risk_level(
            spread_prediction
        )

        virality = self._number(
            spread_prediction.get(
                "virality_score",
                0,
            )
        )

        spread_probability = self._number(
            spread_prediction.get(
                "spread_probability",
                0,
            )
        )

        predicted_reach = self._number(
            spread_prediction.get(
                "predicted_reach",
                0,
            )
        )


        total_nodes = self._calculate_node_count(
            engagement,
            spread_prediction,
        )

        influencer_count = self._calculate_influencer_count(
            total_nodes,
            virality,
            spread_probability,
        )

        # Reserve space for source + influencers + bots
        available_after_influencers = (
            total_nodes
            - 1
            - influencer_count
        )

        bot_count = min(
            self._calculate_bot_count(
                total_nodes,
                risk_level,
                virality,
                spread_probability,
            ),
            max(
                0,
                available_after_influencers,
            ),
        )
        
        user_count = max(
            0,
            available_after_influencers
            - bot_count,
        )

        graph = nx.DiGraph()

        source_id = "source-0"

        source_followers = self._number(
            engagement.get("followers")
        )

        if source_followers <= 0:
            source_followers = None

        source_label = (
            str(publisher).strip()
            if publisher
            else "Original Publisher"
        )

        graph.add_node(
            source_id,
            label=source_label,
            display_name=source_label,
            username=(
                f"@{source_label.lower().replace(' ', '_')}"
                if publisher
                else None
            ),
            role="source",
            node_type=self.config.SOURCE_NODE,
            followers=source_followers,
            is_leader=True,
            is_bot=False,
            is_viral=(
                virality >= 60
                or spread_probability >= 60
            ),
            community=0,
            publisher=publisher,
            platform=platform,
            influence_score=100.0,
            share_probability=min(
                1.0,
                max(
                    0.05,
                    spread_probability / 100,
                ),
            ),
            level=0,
        )

        influencer_ids: list[str] = []
        user_ids: list[str] = []
        bot_ids: list[str] = []

        
        for index in range(influencer_count):
    
            node_id = f"influencer-{index + 1}"

            # Calculate influence strength first.
            influence = self._influencer_influence(
                rng,
                virality,
                spread_probability,
            )

            # Temporary follower estimate used only to determine role.
            preliminary_followers = max(
                8000,
                int(predicted_reach * 0.05),
            )

            # Determine the actual influencer role.
            label, role = self._node_identity(
                index + 1,
                influence,
                preliminary_followers,
                platform,
                rng,
            )

            # Generate followers according to the influencer role.
            followers = self._influencer_followers(
                rng,
                predicted_reach,
                role,
            )

            community = (
                index % max(
                    1,
                    min(
                        6,
                        influencer_count,
                    ),
                )
            )

            # -------------------------------------------------
            # ACTUALLY CREATE THE INFLUENCER NODE
            # -------------------------------------------------

            graph.add_node(
                node_id,

                label=label,

                display_name=label,

                username=(
                    f"@{label.lower().replace(' ', '_')}"
                ),

                role=role,

                node_type="influencer",

                followers=followers,

                is_leader=True,

                is_bot=False,

                is_viral=(
                    virality >= 60
                    or spread_probability >= 60
                ),

                community=community,

                publisher=None,

                platform=platform,

                influence_score=round(
                    influence,
                    2,
                ),

                share_probability=self._share_probability(
                    spread_probability,
                    influence,
                    followers,
                    False,
                ),

                level=1,
            )

            # Store the ID so users/edges can connect to it.
            influencer_ids.append(
                node_id
            )
        
        if influencer_ids:
            for index, node_id in enumerate(
                influencer_ids
            ):
                source_weight = self._edge_weight(
                    graph.nodes[source_id],
                    graph.nodes[node_id],
                )

                graph.add_edge(
                    source_id,
                    node_id,
                    weight=source_weight,
                    interaction=self.config.PUBLISH_EDGE,
                )

        available_parents = (
            influencer_ids[:]
            if influencer_ids
            else [source_id]
        )

        for index in range(user_count):
            node_id = f"user-{index + 1}"

            parent_id = self._select_parent(
                available_parents,
                graph,
                rng,
            )

            parent_data = graph.nodes[
                parent_id
            ]

            parent_level = parent_data.get(
                "level",
                1,
            )

            followers = self._user_followers(
                rng
            )

            influence = self._user_influence(
                rng,
                parent_data.get(
                    "influence_score",
                    20,
                ),
            )

            community = parent_data.get(
                "community",
                0,
            )

            label = f"User {index + 1}"
            role = "user"

            graph.add_node(
                node_id,
                label=label,
                node_type="user",
                role=role,
                display_name=label,
                username=f"@{label.lower().replace(' ', '_')}",
                followers=followers,
                is_leader=role in (
                    "community_leader",
                    "micro_influencer",
                ),
                is_bot=False,
                is_viral=influence >= 70,
                community=community,
                publisher=None,
                platform=platform,
                influence_score=influence,
                share_probability=self._share_probability(
                    spread_probability,
                    influence,
                    followers,
                    False,
                ),
                level=parent_level + 1,
            )
            
            graph.add_edge(
                parent_id,
                node_id,
                weight=self._edge_weight(
                    graph.nodes[parent_id],
                    graph.nodes[node_id],
                ),
                interaction=self.config.SHARE_EDGE,
            )

            user_ids.append(node_id)
            available_parents.append(node_id)

        bot_start = 0

        for index in range(bot_count):
            node_id = f"bot-{index + 1}"

            parent_pool = (
                influencer_ids
                + user_ids
            )

            if not parent_pool:
                parent_pool = [
                    source_id
                ]

            parent_id = parent_pool[
                rng.randrange(
                    len(parent_pool)
                )
            ]

            parent_data = graph.nodes[
                parent_id
            ]

            followers = rng.randint(
                300,
                7000,
            )

            influence = rng.uniform(
                10,
                45,
            )

            community = parent_data.get(
                "community",
                0,
            )

            graph.add_node(
                node_id,
                label="Bot Account",
                node_type="bot",
                followers=followers,
                is_leader=False,
                is_bot=True,
                is_viral=False,
                community=community,
                publisher=None,
                platform=platform,
                influence_score=round(
                    influence,
                    2,
                ),
                share_probability=self._share_probability(
                    spread_probability,
                    influence,
                    followers,
                    True,
                ),
                level=parent_data.get(
                    "level",
                    1,
                ) + 1,
            )

            base_weight = self._edge_weight(
                graph.nodes[parent_id],
                graph.nodes[node_id],
            )

            graph.add_edge(
                parent_id,
                node_id,
                weight=min(
                    self.config.MAX_EDGE_WEIGHT,
                    round(
                        base_weight
                        * self.config.bot_edge_multiplier(
                            risk_level
                        ),
                        3,
                    ),
                ),
                interaction=self.config.BOT_EDGE,
            )

            bot_ids.append(node_id)

        actual_nodes = graph.number_of_nodes()

        if actual_nodes != total_nodes:
            raise RuntimeError(
                "Graph node count mismatch: "
                f"target={total_nodes}, "
                f"actual={actual_nodes}, "
                f"source=1, "
                f"influencers={influencer_count}, "
                f"users={user_count}, "
                f"bots={bot_count}"
            )
        
        self._add_deterministic_cross_edges(
            graph,
            rng,
            spread_probability,
            risk_level,
        )

        self._finalize_nodes(
            graph,
            source_id,
            publisher,
            platform,
            predicted_reach,
        )

        return graph

    def _build_seed(
        self,
        analysis: dict[str, Any],
        engagement: dict[str, Any],
        spread_prediction: dict[str, Any],
    ) -> int:
        stable = (
            f"{self._stable_value(analysis)}|"
            f"{self._stable_value(engagement)}|"
            f"{self._stable_value(spread_prediction)}"
        )

        digest = hashlib.sha256(
            stable.encode("utf-8")
        ).hexdigest()

        return int(
            digest[:16],
            16,
        )

    def _stable_value(
        self,
        value: Any,
    ) -> str:
        if isinstance(value, dict):
            return "{"+",".join(
                f"{key}:{self._stable_value(value[key])}"
                for key in sorted(value)
            )+"}"

        if isinstance(value, list):
            return "["+",".join(
                self._stable_value(item)
                for item in value
            )+"]"

        return str(value)

    def _number(
        self,
        value: Any,
    ) -> float:
        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    def _risk_level(
        self,
        prediction: dict[str, Any],
    ) -> str:
        value = prediction.get(
            "risk_level",
            "Medium",
        )

        value = str(value).strip().title()

        if value not in (
            "Low",
            "Medium",
            "High",
        ):
            return "Medium"

        return value

    def _engagement_score(
        self,
        engagement: dict[str, Any],
    ) -> float:

        likes = float(engagement.get("likes", 0) or 0)
        comments = float(engagement.get("comments", 0) or 0)
        shares = float(
            engagement.get(
                "shares",
                engagement.get("reposts", 0)
            ) or 0
        )

        weighted_engagement = (
            likes
            + comments * 2
            + shares * 3
        )

        return weighted_engagement
    
    def _calculate_node_count(
        self,
        engagement: dict[str, Any],
        spread_prediction: dict[str, Any],
    ) -> int:

        def normalize_percentage(value: Any) -> float:
            try:
                value = float(value or 0)
            except (TypeError, ValueError):
                return 0.0

            if value > 1:
                value /= 100.0

            return max(0.0, min(1.0, value))

        def get_metric(
            data: dict[str, Any],
            *keys: str,
        ) -> float:
            for key in keys:
                if key in data:
                    try:
                        return float(data[key] or 0)
                    except (TypeError, ValueError):
                        continue

            return 0.0

        spread_probability = normalize_percentage(
            get_metric(
                spread_prediction,
                "spread_probability",
                "spreadProbability",
                "probability",
            )
        )

        virality_score = normalize_percentage(
            get_metric(
                spread_prediction,
                "virality_score",
                "viralityScore",
                "virality",
            )
        )

        predicted_reach = get_metric(
            spread_prediction,
            "predicted_reach",
            "predictedReach",
            "reach",
        )

        if predicted_reach <= 0:
            predicted_reach = get_metric(
                engagement,
                "predicted_reach",
                "predictedReach",
                "reach",
            )

        reach_score = min(
            1.0,
            math.log10(
                predicted_reach + 1
            ) / 6.0
        )

        propagation_intensity = (
            0.55 * spread_probability
            + 0.35 * virality_score
            + 0.10 * reach_score
        )

        effective_intensity = (
            propagation_intensity ** 1.8
        )

        min_nodes = self.config.MIN_NODES
        max_nodes = min(
            self.config.MAX_NODES,
            100
        )

        node_count = min_nodes + round(
            effective_intensity
            * (max_nodes - min_nodes)
        )

        return max(
            min_nodes,
            min(max_nodes, node_count)
        )
    
    def _calculate_influencer_count(
        self,
        total_nodes: int,
        virality: float,
        spread_probability: float,
    ) -> int:

        virality_score = max(
            0.0,
            min(100.0, virality),
        )

        spread_score = max(
            0.0,
            min(100.0, spread_probability),
        )

        propagation_strength = (
            0.60 * virality_score
            + 0.40 * spread_score
        ) / 100.0

        # Influencers should exist even in a low-spread graph,
        # because real propagation networks can contain influential
        # accounts even when the current content is unlikely to spread.
        if propagation_strength < 0.10:
            ratio = 0.025

        elif propagation_strength < 0.30:
            ratio = 0.05

        elif propagation_strength < 0.50:
            ratio = 0.08

        elif propagation_strength < 0.70:
            ratio = 0.12

        else:
            ratio = 0.18

        count = round(
            total_nodes * ratio
        )

        # Always keep at least 1 influencer
        # when the graph has enough nodes.
        if total_nodes >= 20:
            count = max(
                1,
                count,
            )

        max_count = max(
            1,
            int(
                total_nodes *
                self.config.MAX_INFLUENCER_RATIO
            ),
        )

        return min(
            count,
            max_count,
            max(
                1,
                total_nodes - 1,
            ),
        )
    
    def _calculate_bot_count(
        self,
        total_nodes: int,
        risk_level: str,
        virality: float = 0.0,
        spread_probability: float = 0.0,
    ) -> int:

        virality_score = max(
            0.0,
            min(100.0, virality)
        )

        spread_score = max(
            0.0,
            min(100.0, spread_probability)
        )

        propagation_strength = (
            0.60 * virality_score
            + 0.40 * spread_score
        ) / 100.0

        risk_multiplier = {
            "Low": 0.20,
            "Medium": 0.55,
            "High": 1.00,
        }.get(
            risk_level,
            0.55
        )

        bot_ratio = (
            propagation_strength *
            risk_multiplier *
            0.12
        )

        if propagation_strength < 0.15:
            bot_ratio *= 0.25

        count = round(
            total_nodes * bot_ratio
        )

        if (
            risk_level == "High"
            and propagation_strength >= 0.70
        ):
            count = max(
                1,
                count
            )

        return max(
            0,
            min(
                count,
                max(0, total_nodes - 1)
            )
        )
    
    def _source_followers(
        self,
        engagement: dict[str, Any],
        predicted_reach: float,
    ) -> int | None:

        followers = engagement.get(
            "followers"
        )

        if followers is None:
            return None

        try:
            followers = int(
                self._number(followers)
            )
        except Exception:
            return None

        if followers <= 0:
            return None

        return followers    
         
    def _influencer_followers(
        self,
        rng: random.Random,
        predicted_reach: float,
        role: str = "micro_influencer",
    ) -> int:

        reach = max(
            1000,
            float(predicted_reach or 1000),
        )

        role = str(
            role or "micro_influencer"
        ).lower()

        if role == "community_leader":

            minimum = max(
                15000,
                int(reach * 0.05),
            )

            maximum = max(
                minimum + 1,
                int(reach * 0.20),
            )

        elif role == "influencer":

            minimum = max(
                25000,
                int(reach * 0.08),
            )

            maximum = max(
                minimum + 1,
                int(reach * 0.35),
            )

        else:

            minimum = max(
                8000,
                int(reach * 0.03),
            )

            maximum = max(
                minimum + 1,
                int(reach * 0.15),
            )

        maximum = min(
            maximum,
            1_000_000,
        )

        return rng.randint(
            minimum,
            maximum,
        )
        
    def _influencer_influence(
        self,
        rng: random.Random,
        virality: float,
        spread_probability: float,
    ) -> float:

        propagation_strength = (
            0.60 * max(0.0, min(100.0, virality))
            + 0.40 * max(0.0, min(100.0, spread_probability))
        )

        base = (
            35
            + propagation_strength * 0.55
        )

        variation = rng.uniform(
            -5,
            5,
        )

        return round(
            max(
                25,
                min(
                    100,
                    base + variation,
                ),
            ),
            2,
        )
    
    def _node_identity(
        self,
        index: int,
        influence: float,
        followers: int,
        platform: str,
        rng: random.Random,
    ) -> tuple[str, str]:

        if influence >= 80 and followers >= 50000:
            return (
                f"Major Influencer {index}",
                "influencer",
            )

        if influence >= 65 and followers >= 10000:
            return (
                f"Community Leader {index}",
                "community_leader",
            )

        return (
            f"Micro Influencer {index}",
            "micro_influencer",
        )
        
    def _user_followers(
        self,
        rng: random.Random,
    ) -> int:

        return rng.randint(
            100,
            8000,
        )

    def _user_influence(
        self,
        rng: random.Random,
        parent_influence: float,
    ) -> float:
        decay = rng.uniform(
            0.72,
            0.92,
        )

        return round(
            max(
                5,
                min(
                    100,
                    parent_influence * decay,
                ),
            ),
            2,
        )

    def _share_probability(
        self,
        spread_probability: float,
        influence: float,
        followers: int,
        is_bot: bool,
    ) -> float:
        probability = (
            spread_probability / 100
            + influence / 500
            + min(
                followers,
                100000,
            ) / 500000
        )

        if is_bot:
            probability += 0.08

        return round(
            min(
                1.0,
                max(
                    0.01,
                    probability,
                ),
            ),
            3,
        )

    def _select_parent(
        self,
        parents: list[str],
        graph: nx.DiGraph,
        rng: random.Random,
    ) -> str:
        if not parents:
            return "source-0"

        weighted = []

        for node_id in parents:
            data = graph.nodes[node_id]

            influence = self._number(
                data.get(
                    "influence_score",
                    0,
                )
            )

            followers = self._number(
                data.get(
                    "followers",
                    0,
                )
            )

            score = max(
                1.0,
                influence
                + math.log10(
                    followers + 1
                ) * 5,
            )

            weighted.append(
                (
                    node_id,
                    score,
                )
            )

        total = sum(
            score
            for _, score in weighted
        )

        if total <= 0:
            return weighted[
                rng.randrange(
                    len(weighted)
                )
            ][0]

        point = rng.random() * total

        current = 0.0

        for node_id, score in weighted:
            current += score

            if point <= current:
                return node_id

        return weighted[-1][0]

    def _edge_weight(
        self,
        source: dict[str, Any],
        target: dict[str, Any],
    ) -> float:
        source_probability = self._number(
            source.get(
                "share_probability",
                0.1,
            )
        )

        target_probability = self._number(
            target.get(
                "share_probability",
                0.1,
            )
        )

        source_influence = self._number(
            source.get(
                "influence_score",
                0,
            )
        )

        target_influence = self._number(
            target.get(
                "influence_score",
                0,
            )
        )

        weight = (
            (
                source_probability
                + target_probability
            ) / 2
        ) * 0.5

        weight += (
            (
                source_influence
                + target_influence
            ) / 200
        ) * 0.5

        return round(
            max(
                self.config.MIN_EDGE_WEIGHT,
                min(
                    self.config.MAX_EDGE_WEIGHT,
                    weight,
                ),
            ),
            3,
        )

    def _add_deterministic_cross_edges(
        self,
        graph: nx.DiGraph,
        rng: random.Random,
        spread_probability: float,
        risk_level: str,
    ) -> None:
        nodes = sorted(
            graph.nodes(
                data=True
            ),
            key=lambda item: str(item[0]),
        )

        probability = min(
            0.25,
            0.04
            + spread_probability / 500,
        )

        bot_multiplier = (
            self.config.bot_edge_multiplier(
                risk_level
            )
        )

        for target_id, target_data in nodes:
            if target_data.get(
                "node_type"
            ) == self.config.SOURCE_NODE:
                continue

            level = target_data.get(
                "level",
                1,
            )

            candidates = []

            for source_id, source_data in nodes:
                if source_id == target_id:
                    continue

                if source_data.get(
                    "level",
                    0,
                ) != level - 1:
                    continue

                if graph.has_edge(
                    source_id,
                    target_id,
                ):
                    continue

                candidates.append(
                    (
                        source_id,
                        source_data,
                    )
                )

            if not candidates:
                continue

            candidates.sort(
                key=lambda item: (
                    -self._number(
                        item[1].get(
                            "influence_score",
                            0,
                        )
                    ),
                    str(item[0]),
                )
            )

            roll = rng.random()

            if roll > probability:
                continue

            source_id, source_data = candidates[
                0
            ]

            weight = self._edge_weight(
                source_data,
                target_data,
            )

            if target_data.get(
                "is_bot"
            ):
                weight *= bot_multiplier

            graph.add_edge(
                source_id,
                target_id,
                weight=round(
                    min(
                        self.config.MAX_EDGE_WEIGHT,
                        weight,
                    ),
                    3,
                ),
                interaction=self.config.CASCADE_EDGE,
            )

    def _finalize_nodes(
        self,
        graph: nx.DiGraph,
        source_id: str,
        publisher: Any,
        platform: str,
        predicted_reach: float,
    ) -> None:
        for node_id, data in graph.nodes(
            data=True
        ):
            if node_id == source_id:
                data["label"] = (
                    publisher
                    if publisher
                    else "Original Publisher"
                )
                data["publisher"] = publisher

            data["platform"] = platform

            in_degree = graph.in_degree(
                node_id
            )

            out_degree = graph.out_degree(
                node_id
            )

            data["in_degree"] = in_degree
            data["out_degree"] = out_degree
            data["degree"] = (
                in_degree
                + out_degree
            )

            influence = self._number(
                data.get(
                    "influence_score",
                    0,
                )
            )

            followers = self._number(
                data.get(
                    "followers",
                    0,
                )
            )

            data["reach"] = int(
                max(
                    followers,
                    predicted_reach
                    * (
                        influence / 100
                    )
                    * 0.1,
                )
            )

            if data.get(
                "is_bot"
            ):
                data["reach"] = int(
                    data["reach"] * 0.25
                )
                