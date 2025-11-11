#!/usr/bin/env python3
"""
Simple attack simulator:
- Sends GET requests to a target (default http://localhost:8080/test).
- Prints one JSON object per request to stdout (newline-delimited).
- Parameters: --target / -t, --total / -n, --concurrency / -c, --delay / -d
"""
import sys
import time
import json
import argparse
import random
from concurrent.futures import ThreadPoolExecutor
try:
    import requests
except Exception:
    sys.stderr.write("requests library missing. In VS Code terminal run: pip install requests\n")
    sys.exit(1)


def make_request(session, url, idx, timeout=5):
    t0 = time.time()
    try:
        r = session.get(url, timeout=timeout, params={"i": idx, "rnd": random.random()})
        status = r.status_code
        size = len(r.content)
        ok = True
    except Exception as e:
        status = None
        size = 0
        ok = False
        err = str(e)
    t1 = time.time()
    entry = {
        "ts": int(t1),
        "elapsed": round(t1 - t0, 4),
        "target": url,
        "index": idx,
        "status": status,
        "size": size,
        "ok": ok
    }
    if not ok:
        entry["error"] = err
    return entry


def run_sim(target, total, concurrency, delay):
    session = requests.Session()
    # allow target with or without trailing path
    url = target.rstrip("/")
    idx = 0
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = []
        while idx < total:
            # submit up to concurrency tasks
            for _ in range(min(concurrency, total - idx)):
                futures.append(ex.submit(make_request, session, url, idx))
                idx += 1
            # collect all submitted tasks
            while futures:
                f = futures.pop(0)
                result = f.result()
                # print each JSON line (newline delimited)
                print(json.dumps(result), flush=True)
            if delay > 0 and idx < total:
                time.sleep(delay)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Simple attack simulator")
    p.add_argument("--target", "-t", default="http://localhost:8080/test", help="Target URL")
    p.add_argument("--total", "-n", type=int, default=100, help="Total requests")
    p.add_argument("--concurrency", "-c", type=int, default=5, help="Concurrent threads")
    p.add_argument("--delay", "-d", type=float, default=0.1, help="Delay between batches (seconds)")
    args = p.parse_args()
    run_sim(args.target, args.total, args.concurrency, args.delay)
