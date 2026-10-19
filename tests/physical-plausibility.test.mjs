// Isolated cross-language plausibility tests; entirely synthetic Geoapify-shaped data.
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {classify} from "../docs/demo-model.mjs";

const base=JSON.parse(readFileSync(new URL("../docs/demo-input.json",import.meta.url),"utf8"));
function withRoute(distance,time){
  const d=structuredClone(base);
  d.routes[0].results[0]={distance,time};
  return classify(d).assessments[0];
}
test("cannot claim a 20m walk to a venue >=300m away in geodesic distance",()=>{
  const x=withRoute(20,240);
  assert.ok(x.directM>300);
  assert.equal(x.verdict,"INCONCLUSIVE");
  assert.match(x.reason,/distance|lower bound/i);
});
test("cannot claim a 550m walk completed in 2s as pedestrian route",()=>{
  const x=withRoute(550,2);
  assert.equal(x.verdict,"INCONCLUSIVE");
  assert.match(x.reason,/speed/i);
});
test("cannot claim zero time for nonzero walking distance",()=>{
  assert.equal(withRoute(550,0).verdict,"INCONCLUSIVE");
});
test("ordinary synthetic pedestrian evidence keeps original confirmed status",()=>{
  assert.equal(withRoute(550,470).verdict,"CONFIRMED_ESTIMATE");
});
