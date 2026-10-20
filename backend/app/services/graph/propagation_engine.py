from __future__ import annotations

import csv
import hashlib
import math
import os
import random
from pathlib import Path
from typing import Any

import networkx as nx

from app.services.graph.graph_config import GraphConfig


class PropagationEngine:
    """
    Generates a SIMULATED propagation graph from observed engagement data.

    The graph is not a record of actual users who shared a post.
    The spreading level comes from dated engagement observations.
    """
    # Dataset-based future audience exposure reference boundaries.
    # These are model estimates, not guaranteed real-world limits.
    MIN_REFERENCE_EXPOSURE = 152.0
    MAX_REFERENCE_EXPOSURE = 8_959_565.0

    # Minimum and maximum number of simulated graph nodes.
    MIN_GRAPH_NODES = 10
    MAX_GRAPH_NODES = 100
    MEMBER_NAMES_CSV = (
        Path(__file__).resolve().parents[3]
        / "data"
        / "random_200_members_india_regions.csv"
    )

    @classmethod
    def _load_member_names(cls) -> list[str]:
        csv_path = Path(
            os.getenv(
                "PROPAGATION_MEMBER_NAMES_CSV",
                str(cls.MEMBER_NAMES_CSV),
            )
        )

        try:
            with csv_path.open(
                "r", encoding="utf-8-sig", newline=""
            ) as file:
                reader = csv.DictReader(file)
                names = [
                    row["Member_Name"].strip()
                    for row in reader
                    if row.get("Member_Name")
                    and row["Member_Name"].strip()
                ]

            return list(dict.fromkeys(names))

        except (OSError, KeyError, csv.Error):
            return []
    ENGAGEMENT_METRICS = (
        "views",
        "likes",
        "comments",
        "shares",
        "reposts",
        "bookmarks",
        "replies",
        "quotes",
        "reactions",
    )

    def __init__(self, config: GraphConfig | None = None) -> None:
        self.config = config or GraphConfig()

    def generate(
        self,
        analysis: dict[str, Any],
        engagement: dict[str, Any],
        audience_exposure_result: dict[str, Any] | None = None,
    ) -> nx.DiGraph:
        observations = analysis.get("engagement_observations", [])
        spreading = analysis.get("spreading_level", {})
        level_name = str(spreading.get("level", "Insufficient historical data"))

        metrics = self._clean_metrics(engagement)
        seed = self._build_seed(analysis, metrics, observations)
        rng = random.Random(seed)

        member_names = self._load_member_names()
        rng.shuffle(member_names)
        member_name_index = 0

        def next_member_name(fallback: str) -> str:
            nonlocal member_name_index

            if member_name_index < len(member_names):
                name = member_names[member_name_index]
                member_name_index += 1
                return f"Simulated: {name}"

            return f"Simulated: {fallback}"

        platform = str(analysis.get("platform", "Unknown"))
        publisher = self._publisher_name(analysis)

        # Prefer the Future Audience Exposure result when a valid estimate
        # is supplied. Preserve the previous node-count method as a safe
        # compatibility fallback until every caller passes the forecast.
        if audience_exposure_result is None:
            candidate = (
                analysis.get("future_audience_exposure")
                or analysis.get("audience_exposure")
            )
            if isinstance(candidate, dict):
                audience_exposure_result = candidate

        exposure_value = self._read_predicted_exposure(audience_exposure_result)
        total_nodes = self._calculate_node_count(
            metrics=metrics,
            spreading_level=level_name,
            observations=observations,
            predicted_exposure=exposure_value,
        )
        scaling_method = (
            "future_audience_exposure_min_max"
            if exposure_value is not None
            else "legacy_fallback_missing_or_invalid_exposure"
        )

        influencer_count = self._calculate_influencer_count(
            total_nodes,
            level_name,
        )

        # Bot nodes are simulation placeholders, NOT detected bot accounts.
        bot_count = self._calculate_simulated_bot_count(
            total_nodes,
            level_name,
        )

        bot_count = min(
            bot_count,
            max(0, total_nodes - 1 - influencer_count),
        )

        user_count = max(
            0,
            total_nodes - 1 - influencer_count - bot_count,
        )

        graph = nx.DiGraph()
        graph.graph.update(
            {
                "simulation": True,
                "graph_type": "simulated_propagation",
                "spreading_level": level_name,
                "spreading_method": spreading.get("method"),
                "daily_log_growth": spreading.get("daily_log_growth"),
                "elapsed_days": spreading.get("elapsed_days"),
                "observation_count": len(observations),
                "engagement_metrics_used": sorted(metrics.keys()),
                "platform": platform,
                "predicted_audience_exposure": exposure_value,
                "graph_scaling_method": scaling_method,
                "exposure_reference_min": self.MIN_REFERENCE_EXPOSURE,
                "exposure_reference_max": self.MAX_REFERENCE_EXPOSURE,
                "target_node_count": total_nodes,
                "warning": (
                    "Nodes and propagation edges are simulated. "
                    "They do not establish actual sharing, unique reach, "
                    "or bot activity."
                ),
            }
        )

        source_id = "source-0"
        source_label = publisher or "Original Publisher"

        source_followers = self._number(
            metrics.get(
                "followers_count",
                metrics.get("followers", 0),
            )
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
            node_type=getattr(self.config, "SOURCE_NODE", "source"),
            followers=int(source_followers) if source_followers > 0 else None,
            is_leader=True,
            is_bot=False,
            is_simulated=True,
            is_viral=level_name == "High",
            community=0,
            publisher=publisher,
            platform=platform,
            influence_score=100.0,
            share_probability=self._base_share_probability(level_name),
            level=0,
        )

        influencer_ids: list[str] = []
        user_ids: list[str] = []
        bot_ids: list[str] = []

        # Create simulated influencers.
        for index in range(influencer_count):
            node_id = f"influencer-{index + 1}"
            influence = round(rng.uniform(45, 90), 2)
            followers = self._influencer_followers(rng, level_name)

            if influence >= 75 and followers >= 50000:
                role = "influencer"
                fallback = f"Major Influencer {index + 1}"
            elif influence >= 60:
                role = "community_leader"
                fallback = f"Community Leader {index + 1}"
            else:
                role = "micro_influencer"
                fallback = f"Micro Influencer {index + 1}"

            label = next_member_name(fallback)
            community = index % max(1, min(6, influencer_count))

            graph.add_node(
                node_id,
                label=label,
                display_name=label,
                username=f"@simulated_influencer_{index + 1}",
                role=role,
                node_type="influencer",
                followers=followers,
                is_leader=True,
                is_bot=False,
                is_simulated=True,
                is_viral=level_name == "High",
                community=community,
                publisher=None,
                platform=platform,
                influence_score=influence,
                share_probability=self._share_probability(
                    level_name,
                    influence,
                    followers,
                ),
                level=1,
            )

            graph.add_edge(
                source_id,
                node_id,
                weight=self._edge_weight(
                    graph.nodes[source_id],
                    graph.nodes[node_id],
                ),
                interaction=getattr(
                    self.config, "PUBLISH_EDGE", "publish"
                ),
                is_simulated=True,
            )

            influencer_ids.append(node_id)

        # Create a hierarchical cascade of simulated users.
        parents = influencer_ids[:] or [source_id]
        created_users = 0
        current_level = 2

        while created_users < user_count and parents:
            next_level: list[str] = []

            for parent_id in parents:
                if created_users >= user_count:
                    break

                parent = graph.nodes[parent_id]
                parent_influence = self._number(
                    parent.get("influence_score", 20)
                )

                branch_size = self._branch_size(
                    parent_id,
                    parent_influence,
                    level_name,
                    rng,
                )
                branch_size = min(
                    branch_size,
                    user_count - created_users,
                )

                for _ in range(branch_size):
                    if created_users >= user_count:
                        break

                    node_id = f"user-{created_users + 1}"
                    label = next_member_name(
                        f"User {created_users + 1}"
                    )
                    followers = rng.randint(100, 8000)
                    influence = round(
                        max(
                            5,
                            min(
                                100,
                                parent_influence * rng.uniform(0.72, 0.92),
                            ),
                        ),
                        2,
                    )

                    graph.add_node(
                        node_id,
                        label=label,
                        display_name=label,
                        username=f"@simulated_user_{created_users + 1}",
                        role="user",
                        node_type="user",
                        followers=followers,
                        is_leader=False,
                        is_bot=False,
                        is_simulated=True,
                        is_viral=level_name == "High" and influence >= 70,
                        community=parent.get("community", 0),
                        publisher=None,
                        platform=platform,
                        influence_score=influence,
                        share_probability=self._share_probability(
                            level_name,
                            influence,
                            followers,
                        ),
                        level=current_level,
                    )

                    graph.add_edge(
                        parent_id,
                        node_id,
                        weight=self._edge_weight(
                            graph.nodes[parent_id],
                            graph.nodes[node_id],
                        ),
                        interaction=getattr(
                            self.config, "SHARE_EDGE", "share"
                        ),
                        is_simulated=True,
                    )

                    user_ids.append(node_id)
                    next_level.append(node_id)
                    created_users += 1

            parents = next_level
            current_level += 1

        # Preserve the existing bot entity type for graph compatibility.
        # These are generated placeholders, not actual bot detections.
        parent_pool = influencer_ids + user_ids

        for index in range(bot_count):
            node_id = f"bot-{index + 1}"
            parent_id = parent_pool[index % len(parent_pool)] if parent_pool else source_id
            parent = graph.nodes[parent_id]

            followers = rng.randint(300, 7000)
            influence = round(rng.uniform(10, 45), 2)

            graph.add_node(
                node_id,
                label="Simulated Bot Placeholder",
                display_name="Simulated Bot Placeholder",
                username=f"@simulated_bot_{index + 1}",
                role="bot",
                node_type="bot",
                followers=followers,
                is_leader=False,
                is_bot=True,
                is_simulated=True,
                bot_status="simulated_placeholder_not_detected",
                is_viral=False,
                community=parent.get("community", 0),
                publisher=None,
                platform=platform,
                influence_score=influence,
                share_probability=self._share_probability(
                    level_name,
                    influence,
                    followers,
                ),
                level=parent.get("level", 0) + 1,
            )

            graph.add_edge(
                parent_id,
                node_id,
                weight=self._edge_weight(
                    graph.nodes[parent_id],
                    graph.nodes[node_id],
                ),
                interaction=getattr(self.config, "BOT_EDGE", "simulated_bot"),
                is_simulated=True,
            )

            bot_ids.append(node_id)

        if graph.number_of_nodes() != total_nodes:
            raise RuntimeError(
                "Graph node count mismatch: "
                f"target={total_nodes}, actual={graph.number_of_nodes()}"
            )

        self._finalize_nodes(graph, platform)

        return graph

    def _clean_metrics(self, metrics: dict[str, Any]) -> dict[str, float]:
        cleaned = {}

        for key, value in metrics.items():
            if isinstance(value, bool) or value is None:
                continue

            try:
                number = float(value)
            except (TypeError, ValueError):
                continue

            if math.isfinite(number) and number >= 0:
                cleaned[key] = number

        return cleaned

    def _build_seed(
        self,
        analysis: dict[str, Any],
        engagement: dict[str, Any],
        observations: list,
    ) -> int:
        # Use stable input ordering so the same observations produce
        # the same simulated graph.
        stable = repr(
            (
                self._stable_value(analysis.get("analysis_id")),
                self._stable_value(analysis.get("platform")),
                self._stable_value(analysis.get("spreading_level", {})),
                self._stable_value(engagement),
                self._stable_value(observations),
            )
        )

        digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()
        return int(digest[:16], 16)

    def _stable_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return tuple(
                (key, self._stable_value(value[key]))
                for key in sorted(value)
            )

        if isinstance(value, list):
            return tuple(self._stable_value(item) for item in value)

        return value

    def _number(self, value: Any) -> float:
        try:
            number = float(value)
            return number if math.isfinite(number) else 0.0
        except (TypeError, ValueError):
            return 0.0

    def _read_predicted_exposure(
        self,
        exposure_result: dict[str, Any] | None,
    ) -> float | None:
        """Return a valid predicted exposure, or None for safe fallback."""
        if not isinstance(exposure_result, dict):
            return None

        # Accept successful status values emitted by the current forecasting
        # endpoint. Reject explicit failures or unknown statuses.
        status = exposure_result.get("status")
        successful_statuses = {
            "experimental_estimate",
            "experimental_engagement_adjusted_forecast",
            "future_view_prediction",
            "observed_baseline",
        }
        if status is not None and status not in successful_statuses:
            return None

        # The forecast API's canonical field is audience_exposure_proxy;
        # predicted_views is retained as a compatible alias. Neither field
        # represents verified unique reach.
        value = exposure_result.get("predicted_audience_exposure")
        if value is None:
            value = exposure_result.get("audience_exposure_proxy")
        if value is None:
            value = exposure_result.get("predicted_views")
        if isinstance(value, bool) or value is None:
            return None

        try:
            exposure = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(exposure) or exposure < 0:
            return None

        return exposure

    def _calculate_node_count(
        self,
        metrics: dict[str, float],
        spreading_level: str,
        observations: list,
        predicted_exposure: float | None = None,
    ) -> int:
        """
        Scale simulated graph nodes using the future audience exposure estimate.

        Reference mapping:
            Exposure <= 152       -> 10 nodes
            Exposure >= 8,959,565 -> 100 nodes

        Intermediate exposure values are mapped linearly.
        If exposure is missing or invalid, retain the legacy fallback.
        """
        minimum = self.MIN_GRAPH_NODES

        configured_maximum = int(
            getattr(self.config, "MAX_NODES", self.MAX_GRAPH_NODES)
        )

        maximum = max(
            minimum,
            min(configured_maximum, self.MAX_GRAPH_NODES),
        )

        if predicted_exposure is not None:
            boundary_span = (
                self.MAX_REFERENCE_EXPOSURE
                - self.MIN_REFERENCE_EXPOSURE
            )

            if boundary_span <= 0:
                return minimum

            ratio = (
                predicted_exposure - self.MIN_REFERENCE_EXPOSURE
            ) / boundary_span

            # Clamp exposure to the reference interval.
            ratio = max(0.0, min(1.0, ratio))

            node_count = minimum + round(
                ratio * (maximum - minimum)
            )

            return max(
                minimum,
                min(maximum, node_count),
            )

        # Legacy fallback when no valid exposure estimate is supplied.
        engagement_total = sum(
            metrics.get(key, 0.0)
            for key in (
                "likes",
                "comments",
                "shares",
                "reposts",
                "bookmarks",
                "replies",
                "quotes",
                "reactions",
            )
        )

        engagement_score = min(
            1.0,
            math.log10(engagement_total + 1) / 6.0,
        )

        history_score = min(
            1.0,
            max(0, len(observations) - 1) / 4.0,
        )

        level_score = {
            "Low": 0.20,
            "Medium": 0.55,
            "High": 0.90,
        }.get(spreading_level, 0.25)

        if spreading_level == "Insufficient historical data":
            level_score = 0.25

        intensity = (
            0.50 * engagement_score
            + 0.30 * level_score
            + 0.20 * history_score
        )

        intensity = max(0.0, min(1.0, intensity))

        node_count = minimum + round(
            intensity * (maximum - minimum)
        )

        return max(
            minimum,
            min(maximum, node_count),
        )
    
    def _calculate_influencer_count(
        self,
        total_nodes: int,
        spreading_level: str,
    ) -> int:
        ratio = {
            "Low": 0.04,
            "Medium": 0.08,
            "High": 0.14,
        }.get(spreading_level, 0.04)

        max_ratio = float(
            getattr(self.config, "MAX_INFLUENCER_RATIO", 0.20)
        )
        count = round(total_nodes * min(ratio, max_ratio))

        return min(total_nodes - 1, max(1, count))

    def _calculate_simulated_bot_count(
        self,
        total_nodes: int,
        spreading_level: str,
    ) -> int:
        # Small, bounded number of placeholders for visualization only.
        # No engagement metric can establish that an account is a bot.
        ratio = {
            "Low": 0.01,
            "Medium": 0.02,
            "High": 0.03,
        }.get(spreading_level, 0.0)

        return max(0, min(round(total_nodes * ratio), total_nodes // 10))

    def _base_share_probability(self, spreading_level: str) -> float:
        return {
            "Low": 0.20,
            "Medium": 0.45,
            "High": 0.70,
        }.get(spreading_level, 0.20)

    def _share_probability(
        self,
        spreading_level: str,
        influence: float,
        followers: int,
    ) -> float:
        base = self._base_share_probability(spreading_level)
        influence_component = max(0.0, min(100.0, influence)) / 500
        follower_component = min(max(0, followers), 100000) / 500000

        return round(
            max(0.01, min(1.0, base + influence_component + follower_component)),
            3,
        )

    def _influencer_followers(
        self,
        rng: random.Random,
        spreading_level: str,
    ) -> int:
        upper_bound = {
            "Low": 50000,
            "Medium": 150000,
            "High": 500000,
        }.get(spreading_level, 50000)

        return rng.randint(8000, upper_bound)

    def _branch_size(
        self,
        parent_id: str,
        parent_influence: float,
        spreading_level: str,
        rng: random.Random,
    ) -> int:
        if parent_id.startswith("influencer-"):
            base = 3 if parent_influence >= 75 else 2
        else:
            base = 2 if parent_influence >= 35 else 1

        if spreading_level == "High" and base < 3 and rng.random() < 0.35:
            base += 1

        return base

    def _edge_weight(
        self,
        source: dict[str, Any],
        target: dict[str, Any],
    ) -> float:
        source_probability = self._number(
            source.get("share_probability", 0.1)
        )
        target_probability = self._number(
            target.get("share_probability", 0.1)
        )
        source_influence = self._number(
            source.get("influence_score", 0)
        )
        target_influence = self._number(
            target.get("influence_score", 0)
        )

        weight = (
            ((source_probability + target_probability) / 2) * 0.5
            + ((source_influence + target_influence) / 200) * 0.5
        )

        minimum = float(getattr(self.config, "MIN_EDGE_WEIGHT", 0.05))
        maximum = float(getattr(self.config, "MAX_EDGE_WEIGHT", 1.0))

        return round(max(minimum, min(maximum, weight)), 3)

    def _publisher_name(self, analysis: dict[str, Any]) -> str | None:
        publisher = (
            analysis.get("publisher")
            or analysis.get("source")
            or analysis.get("source_name")
            or analysis.get("publisher_name")
            or analysis.get("author")
        )

        if isinstance(publisher, dict):
            publisher = (
                publisher.get("name")
                or publisher.get("displayname")
                or publisher.get("username")
                or publisher.get("handle")
            )

        return str(publisher).strip() if publisher else None

    def _finalize_nodes(
        self,
        graph: nx.DiGraph,
        platform: str,
    ) -> None:
        for node_id, data in graph.nodes(data=True):
            data["platform"] = platform
            data["in_degree"] = graph.in_degree(node_id)
            data["out_degree"] = graph.out_degree(node_id)
            data["degree"] = (
                graph.in_degree(node_id) + graph.out_degree(node_id)
            )

            # Do not fabricate predicted reach. Followers are a separate
            # node attribute and are not equivalent to views or unique reach.
            data["reach"] = None
            data["is_simulated"] = True
