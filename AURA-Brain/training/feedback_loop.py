# training/feedback_loop.py

import os
import json
from learner.graph_builder import RoomGraph, build_graph_from_json
from training.design_improver import DesignImprover
from datetime import datetime

DATA_DIR = "data/floorplans/"
LOG_FILE = "logs/feedback_log.jsonl"

class FeedbackLoop:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.improver = DesignImprover()

    def load_graphs(self):
        """Load all JSON graph files from dataset."""
        graphs = []
        for file in os.listdir(self.data_dir):
            if file.endswith(".json"):
                path = os.path.join(self.data_dir, file)
                with open(path, 'r') as f:
                    raw = json.load(f)
                    graph = build_graph_from_json(raw)
                    graphs.append((file, graph))
        return graphs

    def log_result(self, result: dict):
        """Append result to training log."""
        os.makedirs("logs", exist_ok=True)
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(result) + "\n")

    def run(self):
        """Run full feedback loop on dataset."""
        graphs = self.load_graphs()
        print(f"🧠 Loaded {len(graphs)} plans for evaluation...")

        for name, graph in graphs:
            result = self.improver.feedback_loop(graph)
            result['source'] = name
            result['timestamp'] = datetime.utcnow().isoformat()

            self.log_result(result)
            print(f"✅ Processed: {name} | Δ Quality: {result['after']['circulation'] - result['before']['circulation']}\n")

        print("🎯 Feedback loop complete. Logs saved.")


if __name__ == "__main__":
    loop = FeedbackLoop()
    loop.run()
