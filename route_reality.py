#!/usr/bin/env python3
"""Reproducible Geoapify geocoding + places + walking-route claim audit."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_ROOT = "https://api.geoapify.com"
API_PATHS = frozenset(("/v1/geocode/search", "/v2/places", "/v1/routing"))
CATEGORY = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){0,4}\Z")

class InvalidResult(ValueError):
    pass

def point(lat, lon):
    if type(lat) not in (int, float) or type(lon) not in (int, float):
        raise InvalidResult("non-numeric coordinates")
    a, b = float(lat), float(lon)
    if not (math.isfinite(a) and math.isfinite(b) and -90 <= a <= 90 and -180 <= b <= 180):
        raise InvalidResult("invalid Earth coordinates")
    return a, b

def distance_m(a, b):
    a1, a2 = point(*a)
    b1, b2 = point(*b)
    ra, rb = math.radians(a1), math.radians(b1)
    x = math.sin((rb-ra)/2)**2 + math.cos(ra)*math.cos(rb)*math.sin(math.radians(b2-a2)/2)**2
    return 6371000 * 2 * math.asin(min(1, math.sqrt(x)))

def origin_of(geocode):
    rows = geocode.get("results")
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        raise InvalidResult("geocode candidates missing")
    rec = rows[0]
    lat, lon = point(rec.get("lat"), rec.get("lon"))
    rank = rec.get("rank")
    confidence = rank.get("confidence") if isinstance(rank, dict) else None
    if (type(confidence) not in (float, int) or not math.isfinite(confidence)
            or not 0 <= confidence <= 1):
        raise InvalidResult("geocode confidence missing")
    return {"lat":lat, "lon":lon, "label":str(rec.get("formatted") or "")[:180],
            "confidence":float(confidence), "confident":confidence >= 0.65}

def venues_of(places, limit=3):
    rows = places.get("features")
    if not isinstance(rows, list):
        raise InvalidResult("places features missing")
    out = []
    for row in rows[:limit]:
        try:
            coords = row["geometry"]["coordinates"]
            lat, lon = point(coords[1], coords[0])
            props = row["properties"]
            if not isinstance(props, dict):
                continue
            out.append({"lat":lat,"lon":lon,
                        "name":str(props.get("name") or "Unnamed public place")[:160],
                        "id":str(props.get("place_id") or "")[:128]})
        except (KeyError, TypeError, IndexError, InvalidResult):
            continue
    return out

def route_of(data):
    rows = data.get("results") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        return None
    raw = rows[0]
    distance, time = raw.get("distance"), raw.get("time")
    if (type(distance) not in (int, float) or type(time) not in (int, float)
            or not math.isfinite(distance) or not math.isfinite(time)
            or distance < 0 or time < 0):
        return None
    return {"walkDistanceM":round(float(distance),1),"walkDurationS":round(float(time),1)}

def audit(geocode, places, routes, *, minutes=10, limit=3):
    if not (1 <= minutes <= 60 and 1 <= limit <= 6):
        raise ValueError("limits out of range")
    origin = origin_of(geocode)
    out = []
    for i, p in enumerate(venues_of(places,limit)):
        straight = round(distance_m((origin["lat"],origin["lon"]),(p["lat"],p["lon"])),1)
        route = route_of(routes[i]) if i < len(routes) else None
        if not origin["confident"]:
            verdict,why="INCONCLUSIVE","origin geocoding ambiguous"
        elif route is None:
            verdict,why="INCONCLUSIVE","route missing or malformed"
        elif route["walkDurationS"] <= 60*minutes:
            verdict,why="CONFIRMED_ESTIMATE","walk route estimate within budget"
        else:
            verdict,why="CONTRADICTED_ESTIMATE","walk route estimate exceeds budget"
        out.append({"place":p["name"],"placeId":p["id"],
                    "straightLineM":straight,"route":route,"verdict":verdict,"reason":why})
    return {"schema":1,"origin":origin,"walkBudgetMinutes":minutes,"assessments":out,
            "officialGeoapifyPaths":["/v1/geocode/search","/v2/places","/v1/routing"],
            "caveat":"Estimate only; not store-hours, accessibility, mobility or public safety proof"}

class Client:
    def __init__(self,key):
        if not isinstance(key,str) or not (12 <= len(key) <= 512):
            raise ValueError("valid GEOAPIFY_API_KEY needed for live calls")
        self.__key=key
    def get(self,path,**args):
        if path not in API_PATHS:raise ValueError("path outside allowlist")
        url=API_ROOT+path+"?"+urlencode({**args,"apiKey":self.__key})
        req=Request(url,headers={"Accept":"application/json","User-Agent":"GeoRouteProof-AI-assisted-v0.1"})
        try:
            with urlopen(req,timeout=12) as r:
                if r.status!=200:raise InvalidResult("provider returned non-200")
                raw=r.read(1500001)
            if len(raw)>1500000:raise InvalidResult("provider reply too large")
            val=json.loads(raw)
            if not isinstance(val,dict):raise InvalidResult("not JSON object")
            return val
        except Exception:
            # HTTPError includes API key in its URL. Redact entirely.
            raise InvalidResult("Geoapify unavailable, invalid key or provider error") from None

def real_run(origin,category,minutes,limit,radius,key):
    if not isinstance(origin,str) or not 3<=len(origin)<=160:
        raise ValueError("use a public place name with length 3..160")
    if not CATEGORY.fullmatch(category):raise ValueError("invalid places category")
    if not (1<=limit<=6 and 1<=minutes<=60 and 200<=radius<=3000):
        raise ValueError("bound limits exceeded")
    c=Client(key)
    geocode=c.get("/v1/geocode/search",text=origin,format="json",limit=3)
    pin=origin_of(geocode)
    if not pin["confident"]:
        return audit(geocode,{"features":[]},[],minutes=minutes,limit=limit)
    lon,lat=pin["lon"],pin["lat"]
    places=c.get("/v2/places",categories=category,
                 filter=f"circle:{lon},{lat},{radius}",
                 bias=f"proximity:{lon},{lat}",limit=limit)
    routes=[]
    for p in venues_of(places,limit):
        waypoints=f"{lat},{lon}|{p['lat']},{p['lon']}"
        try:routes.append(c.get("/v1/routing",waypoints=waypoints,mode="walk",format="json"))
        except InvalidResult:routes.append({"results":[]})
    out=audit(geocode,places,routes,minutes=minutes,limit=limit)
    out["checkedAtUTC"]=datetime.now(timezone.utc).isoformat()
    out["maxProviderCalls"]=2+limit
    out["privateAPIKeyInOutput"]=False
    return out

def main():
    p=argparse.ArgumentParser(description="Evidence-grounded Geoapify walking-time check")
    p.add_argument("--demo",action="store_true",help="offline synthetic fixture; no API key or network")
    p.add_argument("--origin",default="Seoul Station, Seoul, South Korea")
    p.add_argument("--category",default="catering.cafe")
    p.add_argument("--minutes",type=int,default=10)
    p.add_argument("--limit",type=int,default=3)
    p.add_argument("--radius",type=int,default=1200)
    args=p.parse_args()
    if args.demo:
        data=json.loads(Path(__file__).with_name("tests").joinpath("fixtures","demo.json").read_text())
        out=audit(data["geocode"],data["places"],data["routes"],
                  minutes=args.minutes,limit=args.limit)
        out["fixtureIsSyntheticNotRealGeoapifyResult"]=True
    else:
        key=os.getenv("GEOAPIFY_API_KEY")
        if not key:p.error("set private GEOAPIFY_API_KEY for live results; use --demo otherwise")
        out=real_run(args.origin,args.category,args.minutes,args.limit,args.radius,key)
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=="__main__":
    try:main()
    except (InvalidResult,ValueError) as e:
        print("INCONCLUSIVE: "+str(e),file=sys.stderr)
        raise SystemExit(2)
