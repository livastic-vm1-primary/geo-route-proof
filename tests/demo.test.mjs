import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {classify,haversineM} from "../docs/demo-model.mjs";
const data=JSON.parse(readFileSync(new URL("../docs/demo-input.json",import.meta.url),"utf8"));
test("fixture is explicitly fictional",()=>assert.equal(data.synthetic,true));
test("original Python synthetic outcomes agree at 10 min",()=>{
 const r=classify(data,{minutes:10});
 assert.deepEqual(r.counts,[1,1,1]);
 assert.deepEqual(r.assessments.map(x=>x.verdict),[
  "CONFIRMED_ESTIMATE","CONTRADICTED_ESTIMATE","INCONCLUSIVE"]);
});
test("4 minute budget rejects both existing routes",()=>assert.deepEqual(classify(data,{minutes:4}).counts,[0,2,1]));
test("14 minute budget accepts 470s and 800s, not missing route",()=>assert.deepEqual(classify(data,{minutes:14}).counts,[2,0,1]));
test("ambiguous origin makes all observations inconclusive",()=>assert.deepEqual(classify(data,{minutes:20,confidenceOverride:0.4}).counts,[0,0,3]));
test("routing exactly matches time budget",()=>{
 const d=structuredClone(data);d.routes[0].results[0].time=600;
 assert.equal(classify(d,{minutes:10}).assessments[0].verdict,"CONFIRMED_ESTIMATE");
});
test("geospatial convention [lon,lat] is validated",()=>{
 assert.ok(classify(data).assessments[0].directM>300);
 const d=structuredClone(data);d.places.features[0].geometry.coordinates=[400,37];
 assert.throws(()=>classify(d),/coordinates/);
});
test("non numeric route duration cannot count as proof",()=>{
 const d=structuredClone(data);d.routes[0].results[0].time="470";
 assert.equal(classify(d).assessments[0].verdict,"INCONCLUSIVE");
});
test("must not quietly accept unsourced real-world data or invented time threshold",()=>{
 const d=structuredClone(data);d.synthetic=false;
 assert.throws(()=>classify(d),/synthetic/);
 assert.throws(()=>classify(data,{minutes:0}),/limit/);
 assert.throws(()=>classify(data,{minutes:31}),/limit/);
});
test("distance calculation never accepts invalid lat/lon",()=>{
 assert.throws(()=>haversineM([126.97,37.5],[126.98,37.6]),/coordinates/);
});
