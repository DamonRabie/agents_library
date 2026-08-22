#!/usr/bin/env python3
"""
Data-Warehouse Search — find engine choices, SQL checklist items, optimization techniques.
Usage: python search.py "<query>" [--domain <domain>] [--max-results 5]
Domains: engines, checklist, optimization (default: all)
"""
import argparse, csv, os, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FILES = {"engines": "engines.csv", "checklist": "sql-checklist.csv", "optimization": "optimization.csv"}

def load_csv(f):
    p = os.path.join(DATA_DIR, f)
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if os.path.exists(p) else []

def score(row, terms):
    text = " ".join(str(v) for v in row.values()).lower()
    return sum(text.count(t) for t in terms)

def search(query, domain=None, max_results=5):
    terms = query.lower().split()
    sources = {domain: FILES[domain]} if domain and domain in FILES else FILES
    results = [(score(row, terms), dn, row) for dn, fn in sources.items() for row in load_csv(fn) if score(row, terms) > 0]
    return sorted(results, key=lambda x: -x[0])[:max_results]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query"); p.add_argument("--domain", choices=list(FILES)); p.add_argument("--max-results", type=int, default=5)
    args = p.parse_args()
    hits = search(args.query, args.domain, args.max_results)
    if not hits: print(f"No results for '{args.query}'"); return
    print(f"## Data-Warehouse Search: '{args.query}'\nFound {len(hits)} result(s)\n")
    for s, dn, row in hits:
        print(f"### [{dn}] (score={s})")
        for k, v in row.items(): print(f"  {k}: {v}")
        print()

if __name__ == "__main__": main()
