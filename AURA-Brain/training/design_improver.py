# training/design_improver.py

import json
from learner.graph_builder import RoomGraph
from knowledge.cost_library import get_material_costs
from datetime import datetime
import random

class DesignImprover:
    def __init__(self, rules_path="knowledge/room_rules.yaml"):
        self.rules = self.load_rules(rules_path)
        self.costs = get_material_costs()

    def load_rules(self, path):
        import yaml
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def score_design(self, graph: RoomGraph) -> dict:
        """Evaluate spatial quality and cost."""
        score = {
            "circulation": 0,
            "zoning": 0,
            "area_efficiency": 0,
            "material_cost": 0
        }

        total_area = 0
        zones = {"private": [], "public": [], "service": []}

        for node in graph.nodes(data=True):
            room = node[1]
            total_area += room.get("area", 0)
            rtype = room.get("type", "")
            if rtype in self.rules:
                zones[self.rules[rtype]['zone']].append(room)

        # Simplified heuristics
        score["area_efficiency"] = min(100, round((total_area / graph.total_footprint()) * 100, 2))
        score["circulation"] = self.evaluate_circulation(graph)
        score["zoning"] = self.evaluate_zoning(zones)
        score["material_cost"] = self.estimate_cost(graph)

        return score

    def evaluate_circulation(self, graph: RoomGraph):
        """Mock: penalize designs with many disconnected rooms."""
        disconnected = 0
        for node in graph.nodes():
            if graph.degree(node) < 1:
                disconnected += 1
        return max(0, 100 - disconnected * 10)

    def evaluate_zoning(self, zones):
        """Simple zoning quality by adjacency score."""
        if len(zones["private"]) < 1 or len(zones["service"]) < 1:
            return 0
        return 100  # Future: adjacency matrices

    def estimate_cost(self, graph: RoomGraph):
        """Rough cost estimation using wall lengths and area."""
        wall_m = graph.total_wall_length()
        floor_m2 = graph.total_footprint()
        return round(
            wall_m * self.costs["cement"] * 0.05 + 
            floor_m2 * self.costs["tile"] * 0.1 +
            floor_m2 * self.costs["wood"] * 0.05,
        2)

    def improve(self, graph: RoomGraph):
        """Suggest random room tweak (placeholder)."""
        proposals = []
        for node in graph.nodes(data=True):
            room = node[1]
            if random.random() < 0.3:
                original = room["area"]
                room["area"] *= round(random.uniform(0.9, 1.1), 2)
                proposals.append((room["name"], original, room["area"]))
        return proposals

    def feedback_loop(self, graph: RoomGraph):
        before = self.score_design(graph)
        print(f"🔍 Before: {json.dumps(before, indent=2)}")

        improvements = self.improve(graph)

        after = self.score_design(graph)
        print(f"✅ After: {json.dumps(after, indent=2)}")

        return {
            "before": before,
            "after": after,
            "improvements": improvements,
            "timestamp": datetime.utcnow().isoformat()
        }
