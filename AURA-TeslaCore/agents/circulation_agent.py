# agents/circulation_agent.py
# Evaluates and optimizes human flow inside the floor plan

from typing import Dict, List, Tuple
import networkx as nx

class CirculationAgent:
    def __init__(self, room_graph: nx.Graph):
        """
        Takes in a room adjacency graph. Nodes are rooms, edges represent connections (doors).
        """
        self.graph = room_graph

    def compute_flow_efficiency(self) -> float:
        """
        Uses shortest path averages to evaluate how navigable the floor plan is.
        Lower values = more efficient circulation.
        """
        all_lengths = []
        for source in self.graph.nodes:
            for target in self.graph.nodes:
                if source != target:
                    try:
                        length = nx.shortest_path_length(self.graph, source=source, target=target)
                        all_lengths.append(length)
                    except nx.NetworkXNoPath:
                        continue
        if not all_lengths:
            return 999.0  # Very poor
        return sum(all_lengths) / len(all_lengths)

    def detect_dead_ends(self) -> List[str]:
        """
        Identifies rooms with only one connection (possible dead-ends in circulation).
        """
        return [node for node in self.graph.nodes if self.graph.degree[node] == 1]

    def suggest_improvements(self) -> List[str]:
        """
        Returns improvement suggestions based on circulation inefficiencies.
        """
        suggestions = []
        eff = self.compute_flow_efficiency()
        if eff > 2.5:
            suggestions.append("🔁 Consider open plan to improve movement.")
        deads = self.detect_dead_ends()
        if deads:
            suggestions.append(f"🚪 Add secondary access to: {', '.join(deads)}")
        return suggestions


# Example usage:
if __name__ == "__main__":
    G = nx.Graph()
    G.add_edges_from([
        ("Living Room", "Dining"),
        ("Dining", "Kitchen"),
        ("Living Room", "Bedroom"),
        ("Bedroom", "Toilet"),
    ])

    agent = CirculationAgent(G)
    print("Efficiency Score:", agent.compute_flow_efficiency())
    print("Dead Ends:", agent.detect_dead_ends())
    print("Suggestions:", agent.suggest_improvements())
