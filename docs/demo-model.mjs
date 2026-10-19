// Original GeoRouteProof: fail-closed, fictional, never live venue data.
export function haversineM(a,b) {
  const valid=p=>Array.isArray(p)&&p.length===2&&
    typeof p[0]==="number"&&typeof p[1]==="number"&&
    Number.isFinite(p[0])&&Number.isFinite(p[1])&&
    Math.abs(p[0])<=90&&Math.abs(p[1])<=180;
  if(!valid(a)||!valid(b))throw Error("Invalid Earth coordinates");
  const rad=Math.PI/180;
  const x=Math.sin((b[0]-a[0])*rad/2)**2+
    Math.cos(a[0]*rad)*Math.cos(b[0]*rad)*Math.sin((b[1]-a[1])*rad/2)**2;
  return Math.round(6371000*2*Math.asin(Math.min(1,Math.sqrt(x)))*10)/10;
}
export function classify(input,{minutes=10,confidenceOverride=null}={}) {
  if(!input||input.synthetic!==true||input.schema!=="georouteproof-demo-v1")
    throw Error("Source is not an explicitly synthetic fixture");
  if(!Number.isInteger(minutes)||minutes<2||minutes>30)throw Error("Unsupported time limit");
  const orig=input.geocode?.results?.[0];
  const features=input.places?.features;
  const routes=input.routes;
  if(!orig||!Array.isArray(features)||!Array.isArray(routes)||features.length!==3||routes.length!==3)
    throw Error("Malformed synthetic provider payload");
  const start=[orig.lat,orig.lon];haversineM(start,start);
  const conf=confidenceOverride===null?orig.rank?.confidence:confidenceOverride;
  if(typeof conf!=="number"||!Number.isFinite(conf)||conf<0||conf>1)
    throw Error("Invalid geocoding confidence");
  const assessments=features.map((f,i)=>{
    const coords=f.geometry?.coordinates;
    if(!Array.isArray(coords)||coords.length!==2)throw Error("GeoJSON point missing");
    // GeoJSON [longitude,latitude] differs from Routing lat,lon waypoints.
    const dest=[coords[1],coords[0]];
    const direct=haversineM(start,dest);
    const r=routes[i]?.results?.[0];
    const valid=r&&typeof r.time==="number"&&Number.isFinite(r.time)&&r.time>=0&&
      typeof r.distance==="number"&&Number.isFinite(r.distance)&&r.distance>=0;
    const seconds=valid?r.time:null;
    const verdict=conf<0.65||!valid?"INCONCLUSIVE":
      seconds<=minutes*60?"CONFIRMED_ESTIMATE":"CONTRADICTED_ESTIMATE";
    const reason=conf<0.65?"Origin has low confidence; cannot assert walking time.":
      !valid?"No valid walking route; direct distance is not enough.":
      verdict==="CONFIRMED_ESTIMATE"?"Synthetic pedestrian route fits the budget.":
      "Synthetic pedestrian route exceeds the budget.";
    return {
      name:String(f.properties?.name||"Fictional venue").slice(0,120),
      directM:direct,seconds,verdict,reason
    };
  });
  return {synthetic:true,origin:String(orig.formatted||"Fictional origin").slice(0,120),
    confidence:conf,minutes,assessments,
    counts:["CONFIRMED_ESTIMATE","CONTRADICTED_ESTIMATE","INCONCLUSIVE"].map(
      v=>assessments.filter(x=>x.verdict===v).length)};
}
