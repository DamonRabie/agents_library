#!/usr/bin/env python3
"""
Idea-to-Issues Search — find sizing rules and issue patterns.
Usage: python search.py "<query>" [--max-results 5]
"""
import argparse, csv, os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_csv(f):
    p = os.path.join(DATA_DIR, f)
    return list(csv.DictReader(open(p, newline="", encoding="utf-8"))) if os.path.exists(p) else []

def score(row, terms):
    return sum(" ".join(str(v) for v in row.values()).lower().count(t) for t in terms)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query"); p.add_argument("--max-results", type=int, default=5)
    args = p.parse_args()
    terms = args.query.lower().split()
    rows = [("sizing", r) for r in load_csv("sizing-rules.csv")] + \
           [("quality", r) for r in load_csv("quality-checks.csv")]
    hits = sorted([(score(r, terms), dn, r) for dn, r in rows if score(r, terms) > 0], key=lambda x: -x[0])[:args.max_results]
    if not hits: print(f"No results for '{args.query}'"); return
    print(f"## Idea-to-Issues Search: '{args.query}'\nFound {len(hits)} result(s)\n")
    for s, dn, row in hits:
        label = row.get('slice_type') or row.get('check', '')
        print(f"### [{dn}] {label} (score={s})")
        [print(f"  {k}: {v}") for k, v in row.items()]
        print()

if __name__ == "__main__": main()
