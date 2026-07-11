from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FORECAST_PATH = ROOT / "forecast.py"


def load_forecast_module():
    spec = importlib.util.spec_from_file_location("profit_forecast", FORECAST_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ForecastEngineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forecast = load_forecast_module()
        cls.nodes = cls.forecast.load_nodes()
        cls.configs = cls.forecast.configurations_by_id(cls.forecast.load_configurations())

    def test_current_nodes_keep_baseline_scores_and_levers(self):
        result = self.forecast.score_nodes(self.nodes)

        self.assertAlmostEqual(result["groups"]["pilot"]["base"], 0.064152)
        self.assertAlmostEqual(result["groups"]["unit"]["base"], 0.325)
        self.assertAlmostEqual(result["groups"]["scale"]["base"], 0.45)
        self.assertEqual(result["groups"]["pilot"]["top_lever"]["node_id"], "Z3")
        self.assertEqual(result["groups"]["unit"]["top_lever"]["node_id"], "Z7")
        self.assertEqual(result["groups"]["scale"]["top_lever"]["node_id"], "Z9")

    def test_dog_owners_without_studios_kills_pilot_chain(self):
        dog_nodes = self.forecast.apply_configuration(
            self.nodes,
            self.configs["dog_owners_without_print_studios"],
        )
        dog_result = self.forecast.score_nodes(dog_nodes)

        self.assertEqual(dog_result["groups"]["pilot"]["base"], 0.0)
        changed_to_zero = {
            node["node_id"]
            for node in dog_result["groups"]["pilot"]["members"]
            if node["active"] is False and node["p_base"] == 0.0
        }
        self.assertEqual(changed_to_zero, {"Z2", "Z3", "Z6"})

    def test_model_recommends_studios_over_dog_owners(self):
        comparison = self.forecast.compare_configurations(
            self.nodes,
            self.configs["dog_owners_without_print_studios"],
            self.configs["studios_current"],
        )

        self.assertEqual(comparison["status"], "model_recommendation")
        self.assertEqual(comparison["recommended_config_id"], "studios_current")
        self.assertEqual(comparison["owner_gate"], "owner_accepts_risk_before_canon_patch")
        self.assertEqual(comparison["group_deltas"]["pilot"]["from"], 0.0)
        self.assertAlmostEqual(comparison["group_deltas"]["pilot"]["to"], 0.064152)
        self.assertGreater(len(comparison["changed_decisions"]), 0)
        changed_nodes = {change["node_id"] for change in comparison["changed_nodes"]}
        self.assertEqual(changed_nodes, {"Z2", "Z3", "Z6"})


if __name__ == "__main__":
    unittest.main()
