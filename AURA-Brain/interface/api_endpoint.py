# interface/api_endpoint.py

from learner.floorplan_parser import parse_floorplan_from_prompt
from learner.graph_builder import build_graph_from_rooms
from training.design_improver import DesignImprover
from utils.helpers import estimate_costs
from knowledge.cost_library import load_costs
import json

class AURA_API:
    def __init__(self):
        self.improver = DesignImprover()
        self.costs = load_costs()

    def generate_plan(self, prompt: str) -> dict:
        """
        Generate a floor plan graph from a natural language prompt.
        """
        rooms = parse_floorplan_from_prompt(prompt)
        graph = build_graph_from_rooms(rooms)
        return {
            "status": "success",
            "original_prompt": prompt,
            "graph": graph.to_dict(),
            "cost_estimate": estimate_costs(graph, self.costs),
            "materials": graph.extract_materials()
        }

    def improve_plan(self, raw_graph: dict) -> dict:
        """
        Improve an existing floor plan graph.
        """
        graph = build_graph_from_json(raw_graph)
        result = self.improver.feedback_loop(graph)
        return {
            "status": "improved",
            "before": result['before'],
            "after": result['after'],
            "improved_graph": result['graph'].to_dict(),
            "cost_delta": result['after']['cost'] - result['before']['cost']
        }

    def get_cost_library(self) -> dict:
        """
        Return latest material prices.
        """
        return self.costs


# Optional fast API interface (Future use)
if __name__ == "__main__":
    aura = AURA_API()
    prompt = "3-bedroom bungalow with master ensuite, open kitchen, living room, guest toilet"
    output = aura.generate_plan(prompt)
    print(json.dumps(output, indent=2))
