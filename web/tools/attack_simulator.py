#!/usr/bin/env python3
"""
Simple attack simulator:
- Sends GET requests to a target (default http://localhost:8080/test)
- Includes some AI-style payloads to trigger AI agent detection
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
    sys.stderr.write("requests library missing. Run: pip install requests\n")
    sys.exit(1)


AI_PAYLOADS = [
    "run exploit --ai yellow8193",
    "agent-mode cat8193 execute",
    "cat8197 scan --port 8080"
]


def make_request(session, url, idx, timeout=5, ai_mode=False):
    t0 = time.time()
    try:
        if ai_mode:
            payload = random.choice(AI_PAYLOADS)
            params = {"i": idx, "agent_cmd": payload}
        else:
            params = {"i": idx, "rnd": random.random()}

        r = session.get(url, timeout=timeout, params=params)
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
        "ai_attack": ai_mode,
        "status": status,
        "size": size,
        "ok": ok
    }
    if not ok:
        entry["error"] = err
    return entry


def run_sim(target, total, concurrency, delay):
    session = requests.Session()
    url = target.rstrip("/")

    idx = 0

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = []

        # Normal traffic: total - 5
        normal_count = total - 5
        ai_count = 5  # Number of AI-style attacks

        # Submit normal requests
        for _ in range(normal_count):
            futures.append(ex.submit(make_request, session, url, idx, ai_mode=False))
            idx += 1

        # Submit AI-agent style attacks
        for _ in range(ai_count):
            futures.append(ex.submit(make_request, session, url, idx, ai_mode=True))
            idx += 1

        # Collect results
        for f in futures:
            result = f.result()
            print(json.dumps(result), flush=True)

            if delay > 0:
                time.sleep(delay)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Simple attack simulator")
    p.add_argument("--target", "-t", default="http://localhost:8080/test")
    p.add_argument("--total", "-n", type=int, default=100)
    p.add_argument("--concurrency", "-c", type=int, default=5)
    p.add_argument("--delay", "-d", type=float, default=0.05)

    args = p.parse_args()
    run_sim(args.target, args.total, args.concurrency, args.delay)
