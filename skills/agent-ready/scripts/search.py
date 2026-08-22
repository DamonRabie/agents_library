#!/usr/bin/env python3
"""
Agent-Ready Search — find repo checklist items and fix recipes.
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
    rows = load_csv("repo-checklist.csv")
    hits = sorted([(score(r, terms), r) for r in rows if score(r, terms) > 0], key=lambda x: -x[0])[:args.max_results]
    if not hits: print(f"No results for '{args.query}'"); return
    print(f"## Agent-Ready Search: '{args.query}'\nFound {len(hits)} result(s)\n")
    for s, row in hits:
        print(f"### [{row.get('priority', '?')}] {row.get('check', '')} (score={s})")
        [print(f"  {k}: {v}") for k, v in row.items()]
        print()

if __name__ == "__main__": main()
