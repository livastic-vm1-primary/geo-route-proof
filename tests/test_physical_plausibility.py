"""Independent VM5 negative-path QA for VM1 GeoRouteProof program, synthetic data only."""
import copy
import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import route_reality as r

class WalkRoutePhysicalPlausibility(unittest.TestCase):
    def setUp(self):
        self.demo=json.loads((ROOT/"tests"/"fixtures"/"demo.json").read_text())

    def verdict(self,*,distance=None,duration=None,confidence=None):
        specimen=copy.deepcopy(self.demo)
        route=specimen["routes"][0]["results"][0]
        if distance is not None:route["distance"]=distance
        if duration is not None:route["time"]=duration
        if confidence is not None:specimen["geocode"]["results"][0]["rank"]["confidence"]=confidence
        return r.audit(specimen["geocode"],specimen["places"],specimen["routes"])["assessments"][0]

    def test_cannot_confirm_route_shorter_than_haversine_lower_bound(self):
        x=self.verdict(distance=20,duration=240)
        self.assertGreater(x["straightLineM"],300)
        self.assertEqual(x["verdict"],"INCONCLUSIVE")
        self.assertIn("distance",x["reason"])

    def test_cannot_confirm_400m_walk_in_two_seconds(self):
        x=self.verdict(distance=550,duration=2)
        self.assertEqual(x["verdict"],"INCONCLUSIVE")
        self.assertIn("speed",x["reason"])

    def test_zero_walk_duration_for_nonzero_distance_inconclusive(self):
        x=self.verdict(distance=550,duration=0)
        self.assertEqual(x["verdict"],"INCONCLUSIVE")

    def test_realistic_synthetic_route_keeps_confirmed_estimate(self):
        x=self.verdict(distance=550,duration=470)
        self.assertEqual(x["verdict"],"CONFIRMED_ESTIMATE")
        self.assertEqual(x["route"]["walkDistanceM"],550.0)

    def test_low_geocoder_confidence_stays_inconclusive_even_if_route_realistic(self):
        self.assertEqual(self.verdict(distance=550,duration=470,confidence=.40)["verdict"],"INCONCLUSIVE")

if __name__=="__main__":
    unittest.main()
