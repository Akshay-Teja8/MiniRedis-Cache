"""
Benchmark the core LRU cache implementation.

Measures raw cache performance without HTTP or FastAPI overhead.
"""
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import time
import threading
from lru_cache import LRUcache

# Benchmarking the LRUcache implementation
N = 100000

cache = LRUcache(capacity=N)

print("PUT Benchmark")
print()

start = time.perf_counter()

for i in range(N):
    cache.put(f"key{i}", i)

elapsed = time.perf_counter() - start
put_ops = N / elapsed
print(f"Operations : {N:,}")
print(f"Elapsed    : {elapsed:.4f} seconds")
print(f"Ops/sec    : {put_ops:,.2f}")



print()

print("GET Benchmark")
print()

start = time.perf_counter()

for i in range(N):
    cache.get(f"key{i}")

elapsed = time.perf_counter() - start
get_ops = N / elapsed
print(f"Operations : {N:,}")
print(f"Elapsed    : {elapsed:.4f} seconds")
print(f"Ops/sec    : {get_ops:,.2f}")

print()

print("Concurrent PUT Benchmark")
print()

THREADS = 8
OPS_PER_THREAD = 100000

cache = LRUcache(capacity=THREADS * OPS_PER_THREAD)


def worker(thread_id):
    for i in range(OPS_PER_THREAD):
        cache.put(f"{thread_id}-{i}", i)


threads = []

start = time.perf_counter()

for t in range(THREADS):
    thread = threading.Thread(target=worker, args=(t,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

elapsed = time.perf_counter() - start

total_ops = THREADS * OPS_PER_THREAD
concurrent_ops = total_ops / elapsed
print(f"Threads    : {THREADS}")
print(f"Operations : {total_ops:,}")
print(f"Elapsed    : {elapsed:.4f} seconds")
print(f"Ops/sec    : {concurrent_ops:,.2f}")

# Save results to a file for later analysis

results_dir = Path(__file__).parent / "results"
results_dir.mkdir(exist_ok=True)

with open(results_dir / "benchmark_results.txt", "w") as f:
    f.write("LRU Cache Benchmark Results\n")
    f.write("\n\n")

    f.write(f"PUT Ops/sec        : {put_ops:,.2f}\n")
    f.write(f"GET Ops/sec        : {get_ops:,.2f}\n")
    f.write(f"Concurrent Ops/sec : {concurrent_ops:,.2f}\n")

