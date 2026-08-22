#!/usr/bin/env python3
"""
CI-Deploy Search — find CI patterns, Docker patterns, deploy checklist items.
Usage: python search.py "<query>" [--domain <domain>] [--max-results 5]
Domains: ci, docker, deploy (default: all)
"""
import argparse
import csv
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

FILES = {
    "ci":     "ci-patterns.csv",
    "docker": "docker-patterns.csv",
    "deploy": "deploy-checklist.csv",
}


def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def score(row, terms):
    text = " ".join(str(v) for v in row.values()).lower()
    return sum(text.count(t) for t in terms)


def search(query, domain=None, max_results=5):
    terms = query.lower().split()
    sources = {domain: FILES[domain]} if domain and domain in FILES else FILES
    results = []
    for domain_name, filename in sources.items():
        for row in load_csv(filename):
            s = score(row, terms)
            if s > 0:
                results.append((s, domain_name, row))
    results.sort(key=lambda x: -x[0])
    return results[:max_results]


def main():
    parser = argparse.ArgumentParser(description="CI-Deploy search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", choices=list(FILES.keys()), help="Limit to domain")
    parser.add_argument("--max-results", type=int, default=5)
    args = parser.parse_args()

    hits = search(args.query, args.domain, args.max_results)
    if not hits:
        print(f"No results for '{args.query}'")
        sys.exit(0)

    print(f"## CI-Deploy Search: '{args.query}'")
    print(f"Found {len(hits)} result(s)\n")
    for score_val, domain_name, row in hits:
        print(f"### [{domain_name}] (score={score_val})")
        for k, v in row.items():
            print(f"  {k}: {v}")
        print()


if __name__ == "__main__":
    main()
