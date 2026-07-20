"""
Simple concurrent load test for the running LRU cache API.

Usage:
    # start the server first: uvicorn app.main:app --port 8000
    python loadtest.py --url http://localhost:8000 --threads 20 --requests 200
"""

import argparse
import statistics
import threading
import time

import requests


def worker(base_url: str, thread_id: int, num_requests: int, latencies: list, errors: list):
    for i in range(num_requests):
        key = f"t{thread_id}-{i}"
        try:
            start = time.perf_counter()
            r = requests.put(
                f"{base_url}/cache/{key}",
                json={"value": i, "ttl": 10},
                timeout=5,
            )
            r.raise_for_status()

            r = requests.get(f"{base_url}/cache/{key}", timeout=5)
            r.raise_for_status()
            latencies.append(time.perf_counter() - start)
        except Exception as e:
            errors.append(str(e))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--threads", type=int, default=20)
    parser.add_argument("--requests", type=int, default=200, help="requests per thread")
    args = parser.parse_args()

    latencies: list = []
    errors: list = []

    print(f"Load testing {args.url} with {args.threads} threads x {args.requests} req/thread "
          f"({args.threads * args.requests * 2} total HTTP calls: put+get pairs)")

    start = time.perf_counter()
    threads = [
        threading.Thread(target=worker, args=(args.url, i, args.requests, latencies, errors))
        for i in range(args.threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start

    total_pairs = args.threads * args.requests
    print(f"\nCompleted {total_pairs} put+get pairs in {elapsed:.2f}s "
          f"({total_pairs / elapsed:.1f} pairs/sec)")

    if latencies:
        print(f"Latency (per put+get pair, ms): "
              f"p50={statistics.median(latencies)*1000:.2f} "
              f"p95={statistics.quantiles(latencies, n=20)[18]*1000:.2f} "
              f"max={max(latencies)*1000:.2f}")

    print(f"Errors: {len(errors)}")
    if errors[:5]:
        print("Sample errors:", errors[:5])


if __name__ == "__main__":
    main()
