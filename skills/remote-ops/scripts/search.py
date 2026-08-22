#!/usr/bin/env python3
"""
Remote-Ops Search — find remote VM / SSH / offline-environment fixes.
Usage: python search.py "<query>" [--max-results 5]
"""
import argparse, csv, os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FILES = {"remote": "remote-bugs.csv"}

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
    hits = sorted([(score(r, terms), dn, r) for dn, fn in FILES.items() for r in load_csv(fn) if score(r, terms) > 0], key=lambda x: -x[0])[:args.max_results]
    if not hits: print(f"No results for '{args.query}'"); return
    print(f"## Remote-Ops Search: '{args.query}'\nFound {len(hits)} result(s)\n")
    for s, dn, row in hits:
        print(f"### [{dn}] (score={s})")
        [print(f"  {k}: {v}") for k, v in row.items()]
        print()

if __name__ == "__main__": main()
