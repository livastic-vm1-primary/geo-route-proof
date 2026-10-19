import json
import math
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import route_reality as r

class GeoRouteClaimTests(unittest.TestCase):
    def setUp(self):
        self.f=json.loads((pathlib.Path(__file__).parent/"fixtures"/"demo.json").read_text())
    def test_offline_fixture_tri_state(self):
        x=r.audit(self.f["geocode"],self.f["places"],self.f["routes"])
        self.assertEqual([a["verdict"] for a in x["assessments"]],
                         ["CONFIRMED_ESTIMATE","CONTRADICTED_ESTIMATE","INCONCLUSIVE"])
    def test_haversine_symmetric_and_zero(self):
        a,b=(37.555,126.972),(37.557,126.975)
        self.assertEqual(r.distance_m(a,a),0)
        self.assertAlmostEqual(r.distance_m(a,b),r.distance_m(b,a))
    def test_coordinate_rejects_bool_and_nonfinite(self):
        for a,b in [(True,12),(float("nan"),12),(1,float("inf")),(91,0),(0,-181)]:
            with self.subTest(value=(a,b)):
                with self.assertRaises(r.InvalidResult):r.point(a,b)
    def test_geojson_coordinates_are_lon_lat(self):
        p=r.venues_of(self.f["places"],1)[0]
        self.assertEqual((p["lat"],p["lon"]),(37.557,126.975))
    def test_low_confidence_never_claims_route(self):
        d=json.loads(json.dumps(self.f))
        d["geocode"]["results"][0]["rank"]["confidence"]=0.20
        x=r.audit(d["geocode"],d["places"],d["routes"])
        self.assertTrue(all(y["verdict"]=="INCONCLUSIVE" for y in x["assessments"]))
    def test_missing_geocoder_confidence_stops(self):
        self.f["geocode"]["results"][0].pop("rank")
        with self.assertRaises(r.InvalidResult):r.origin_of(self.f["geocode"])
    def test_no_geocoder_candidates_stops(self):
        with self.assertRaises(r.InvalidResult):r.origin_of({"results":[]})
    def test_invalid_route_not_guessed(self):
        self.assertIsNone(r.route_of({"results":[{"distance":1,"time":float("nan")}]}))
    def test_negative_route_not_guessed(self):
        self.assertIsNone(r.route_of({"results":[{"distance":-1,"time":7}]}))
    def test_unexpected_api_path_blocked(self):
        c=r.Client("synthetic_private_key_test")
        with self.assertRaises(ValueError):c.get("/arbitrary-host-or-path")
    def test_category_rejects_injection(self):
        with self.assertRaises(ValueError):
            r.real_run("Seoul Station","catering.cafe&apiKey=leak",10,3,1200,"synthetic_private_key_test")
    def test_provider_call_bounds(self):
        with self.assertRaises(ValueError):
            r.real_run("Seoul Station","catering.cafe",10,15,1200,"synthetic_private_key_test")
    def test_demo_output_no_api_key(self):
        result=json.dumps(r.audit(self.f["geocode"],self.f["places"],self.f["routes"]))
        self.assertNotIn("GEOAPIFY_API_KEY",result)
        self.assertNotIn("synthetic_private_key_test",result)

if __name__=="__main__":
    unittest.main()
