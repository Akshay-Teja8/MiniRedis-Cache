# MiniRedis Cache

A thread-safe in-memory key-value store built in Python featuring **LRU (Least Recently Used) eviction**, **TTL (Time-To-Live) expiration**, and a **FastAPI REST API**.

This project demonstrates the design and implementation of a production-inspired caching system with concurrent access, automatic expiration, comprehensive testing, and performance benchmarking.

---

## Features

- In-memory key-value storage
- LRU eviction policy
- TTL-based key expiration
- Lazy expiration on access
- Background sweeper thread for automatic cleanup
- Thread-safe implementation using `RLock`
- REST API built with FastAPI
- Comprehensive automated tests with Pytest
- Performance benchmarks
- HTTP load testing

---

## Project Structure

```
.
├── benchmarks/
│   ├── load_test.py
│   ├── cache_benchmark.py
│   └── results/
│       └── benchmark_results.txt
├── lru_cache.py
├── lru_cache_raw.py
├── main.py
├── requirements.txt
├── test_lru_cache.py
└── README.md
```

---

## Architecture

```
                Client
                   │
          HTTP Requests
                   │
             FastAPI Server
                   │
             LRU Cache Layer
                   │
        +----------------------+
        | OrderedDict Storage  |
        | TTL Management       |
        | LRU Eviction         |
        | Background Sweeper   |
        +----------------------+
```

---

## Cache Operations

| Operation | Complexity |
|-----------|------------|
| PUT | O(1) |
| GET | O(1) |
| DELETE | O(1) |
| CONTAINS | O(1) |
| LRU Eviction | O(1) |
| TTL Expiration Check | O(1) |

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Project information |
| GET | `/health` | Health check |
| GET | `/stats` | Cache statistics |
| GET | `/cache/{key}` | Retrieve a value |
| PUT | `/cache/{key}` | Insert/update a value |
| DELETE | `/cache/{key}` | Delete a key |
| DELETE | `/cache` | Clear cache |

Interactive API documentation is available at:

```
http://localhost:8000/docs
```

---

## Installation

Clone the repository.

```bash
git clone https://github.com/<your-username>/MiniRedis-Cache.git
cd MiniRedis-Cache
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## Running Tests

```bash
pytest -v
```

Current Status:

```
18 passed
```

---

## Performance Benchmark

Run:

```bash
python benchmarks/cache_benchmark.py
```

Example results:

```
PUT Benchmark

Operations : 100,000
Elapsed    : 0.0852 s
Ops/sec    : 1,173,383.90

GET Benchmark

Operations : 100,000
Elapsed    : 0.0724 s
Ops/sec    : 1,381,614.31

Concurrent PUT Benchmark

Threads    : 8
Operations : 800,000
Elapsed    : 3.1484 s
Ops/sec    : 254,094.33
```

---

## API Load Testing

Run:

```bash
python benchmarks/load_test.py
```

Example:

```
Load testing http://localhost:8000

20 threads
200 requests/thread

Completed successfully
Latency statistics displayed
```

---

## Design Decisions

### LRU Eviction

The cache uses Python's `OrderedDict` to maintain access order efficiently. Whenever a key is accessed or updated, it is moved to the most recently used position. When capacity is exceeded, the least recently used entry is evicted.

---

### TTL Expiration

Each cache entry optionally stores an expiration timestamp.

Expired entries are removed through two mechanisms:

- Lazy expiration during access (`get`)
- Background sweeper thread running at configurable intervals

This minimizes stale data while avoiding unnecessary overhead.

---

### Thread Safety

Concurrent access is protected using `threading.RLock`, ensuring atomic updates to shared cache state and preventing race conditions.

---

## Technologies Used

- Python 3
- FastAPI
- Pytest
- OrderedDict
- threading
- RLock
- Requests

---

## Future Improvements

- Persistent storage
- Asynchronous API
- Metrics endpoint (Prometheus)
- LFU eviction policy
- Distributed cache support
- Docker deployment
- CI/CD with GitHub Actions

