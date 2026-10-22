#!/usr/bin/env python3
"""ATLAS VOYAGEUR B6.4 — local-only usage ledger. No API/network calls."""
import argparse
import csv
import datetime as dt
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
CASES = ROOT / "cases.csv"
EVENTS = ROOT / "events.csv"
COLUMNS = ["timestamp_utc","case_id","provider","endpoint","method","http_status","attempt","api_units_reported","geo_credits_reported","billing_evidence","request_id","duration_ms","cache_hit","error_type","notes"]

def load_cases():
    with CASES.open(newline="", encoding="utf-8") as f:
        return {r["case_id"]: r for r in csv.DictReader(f)}

def load_events():
    with EVENTS.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            raise ValueError("events.csv columns are unexpected")
        return list(reader)

def check():
    cases=load_cases()
    assert len(cases)==20 and len(set(cases))==20, "Expected 20 unique cases"
    events=load_events()
    assert all(e["case_id"] in cases for e in events), "Unknown case in journal"
    print(f"OK: {len(cases)} test cases; {len(events)} recorded events; zero network calls")

def add(args):
    cases=load_cases()
    if args.case not in cases:
        raise ValueError("Unknown case_id")
    if args.units is not None and args.units < 0: raise ValueError("Negative units")
    if args.credits is not None and args.credits < 0: raise ValueError("Negative credits")
    if (args.units is not None or args.credits is not None) and not args.evidence:
        raise ValueError("Billing evidence required when entering reported units/credits")
    if args.provider=="AeroDataBox" and args.credits is not None:
        raise ValueError("Geoapify credits on AeroDataBox record")
    if args.provider=="Geoapify" and args.units is not None:
        raise ValueError("AeroDataBox units on Geoapify record")
    event=dict.fromkeys(COLUMNS,"")
    event.update(timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),case_id=args.case,provider=args.provider,endpoint=args.endpoint,method=args.method,http_status=str(args.status),attempt=str(args.attempt),api_units_reported="" if args.units is None else str(args.units),geo_credits_reported="" if args.credits is None else str(args.credits),billing_evidence=args.evidence or "",request_id=args.request_id or "",duration_ms="" if args.duration is None else str(args.duration),cache_hit=str(args.cached).lower(),error_type=args.error or "",notes=args.note or "")
    with EVENTS.open("a",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS)
        writer.writerow(event)
    print("Recorded",args.case,args.provider,args.endpoint)

def report():
    cases=load_cases()
    events=load_events()
    by=defaultdict(list)
    for e in events: by[e["case_id"]].append(e)
    print("case | calls | failures | Aero units | Geo credits | unknown billing | follow-up span(min)")
    for code in sorted(cases):
        group=by[code]
        au=sum(int(e["api_units_reported"]) for e in group if e["api_units_reported"])
        gc=sum(int(e["geo_credits_reported"]) for e in group if e["geo_credits_reported"])
        failures=sum(int(e["http_status"])>=400 or bool(e["error_type"]) for e in group)
        unknown=sum((e["provider"]=="AeroDataBox" and not e["api_units_reported"]) or (e["provider"]=="Geoapify" and not e["geo_credits_reported"]) for e in group if e["cache_hit"]!="true")
        ts=sorted(dt.datetime.fromisoformat(e["timestamp_utc"]) for e in group)
        span=round((ts[-1]-ts[0]).total_seconds()/60,1) if len(ts)>1 else 0
        print(f"{code} | {len(group)} | {failures} | {au} | {gc} | {unknown} | {span}")
    print("CAUTION: These are usage measurements, NOT euro costs; prices, taxes and fixed fees require verified supplier billing.")

def main():
    parser=argparse.ArgumentParser(description="Offline measurement ledger — no API calls")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("check")
    sub.add_parser("report")
    addp=sub.add_parser("add")
    addp.add_argument("case")
    addp.add_argument("provider",choices=["AeroDataBox","Geoapify","Other"])
    addp.add_argument("endpoint")
    addp.add_argument("status",type=int)
    addp.add_argument("--method",default="GET")
    addp.add_argument("--attempt",type=int,default=1)
    addp.add_argument("--units",type=int)
    addp.add_argument("--credits",type=int)
    addp.add_argument("--evidence")
    addp.add_argument("--request-id")
    addp.add_argument("--duration",type=int)
    addp.add_argument("--cached",action="store_true")
    addp.add_argument("--error")
    addp.add_argument("--note")
    args=parser.parse_args()
    if args.command=="check": check()
    elif args.command=="report": report()
    else: add(args)

if __name__=="__main__":
    main()
