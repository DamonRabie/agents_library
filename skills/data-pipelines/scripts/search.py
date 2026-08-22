#!/usr/bin/env python3
"""
Data-Pipelines Search — find DAG patterns and Spark sizing fixes.
Usage: python search.py "<query>" [--domain <domain>] [--max-results 5]
Domains: dag, spark (default: all)
"""
import argparse, csv, os, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FILES = {"dag": "dag-patterns.csv", "spark": "spark-sizing.csv"}

def load_csv(f):
    p = os.path.join(DATA_DIR, f)
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if os.path.exists(p) else []

def score(row, terms):
    return sum(" ".join(str(v) for v in row.values()).lower().count(t) for t in terms)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query"); p.add_argument("--domain", choices=list(FILES)); p.add_argument("--max-results", type=int, default=5)
    args = p.parse_args()
    terms = args.query.lower().split()
    sources = {args.domain: FILES[args.domain]} if args.domain else FILES
    hits = sorted([(score(row, terms), dn, row) for dn, fn in sources.items() for row in load_csv(fn) if score(row, terms) > 0], key=lambda x: -x[0])[:args.max_results]
    if not hits: print(f"No results for '{args.query}'"); return
    print(f"## Data-Pipelines Search: '{args.query}'\nFound {len(hits)} result(s)\n")
    for s, dn, row in hits:
        print(f"### [{dn}] (score={s})")
        [print(f"  {k}: {v}") for k, v in row.items()]
        print()

if __name__ == "__main__": main()
