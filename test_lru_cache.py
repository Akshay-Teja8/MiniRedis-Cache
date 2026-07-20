import threading
import time

import pytest

from lru_cache import LRUcache
from lru_cache_raw import LRUcacheRaw


# LRUcacheRaw  

def test_raw_basic_get_put():
    cache = LRUcacheRaw(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    assert cache.get("b") == 2
    assert cache.get("missing") is None


def test_raw_eviction_order():
    cache = LRUcacheRaw(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")       
    cache.put("c", 3)       
    assert cache.get("a") == 1
    assert cache.get("b") is None
    assert cache.get("c") == 3


def test_raw_update_existing_key_moves_to_front():
    cache = LRUcacheRaw(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 100)   
    cache.put("c", 3)     
    assert cache.get("a") == 100
    assert cache.get("b") is None
    assert cache.get("c") == 3


# LRUcache 

def test_basic_get_put():
    cache = LRUcache(capacity=2)
    cache.put("a", 1)
    assert cache.get("a") == 1
    assert cache.get("missing") is None


def test_eviction_when_over_capacity():
    cache = LRUcache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)  
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3
    assert cache.get_stats()["evictions"] == 1


def test_get_refreshes_recency():
    cache = LRUcache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")      
    cache.put("c", 3)   
    assert cache.get("a") == 1
    assert cache.get("b") is None

def test_update_existing_key():
    cache = LRUcache(capacity=2)

    cache.put("a", 1)
    cache.put("a", 100)

    assert cache.get("a") == 100
    assert len(cache) == 1

def test_capacity_one():
    cache = LRUcache(capacity=1)

    cache.put("a", 1)
    cache.put("b", 2)

    assert cache.get("a") is None
    assert cache.get("b") == 2

def test_multiple_ttls():

    cache = LRUcache(capacity=10)

    cache.put("a", 1, ttl=0.05)
    cache.put("b", 2, ttl=0.2)

    time.sleep(0.1)

    assert cache.get("a") is None
    assert cache.get("b") == 2

def test_clear():

    cache = LRUcache(capacity=10)

    cache.put("a", 1)
    cache.put("b", 2)

    cache.clear()

    assert len(cache) == 0

def test_contains():

    cache = LRUcache(capacity=10)

    cache.put("a", 1)

    assert cache.contains("a")
    assert not cache.contains("b")

def test_contains_operator():

    cache = LRUcache(capacity=10)

    cache.put("a", 1)

    assert "a" in cache
    assert "b" not in cache

def test_multiple_evictions():

    cache = LRUcache(capacity=2)

    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    cache.put("d", 4)

    assert cache.get("a") is None
    assert cache.get("b") is None
    assert cache.get("c") == 3
    assert cache.get("d") == 4

def test_ttl_expiry():
    cache = LRUcache(capacity=10)
    cache.put("a", 1, ttl=0.05)  # 50ms TTL
    assert cache.get("a") == 1
    time.sleep(0.1)
    assert cache.get("a") is None
    assert cache.get_stats()["expired_evictions"] == 1


def test_no_ttl_never_expires():
    cache = LRUcache(capacity=10)
    cache.put("a", 1)  # no ttl
    time.sleep(0.05)
    assert cache.get("a") == 1


def test_delete():
    cache = LRUcache(capacity=10)
    cache.put("a", 1)
    assert cache.delete("a") is True
    assert cache.get("a") is None
    assert cache.delete("a") is False  # already gone


def test_background_sweeper_removes_expired_keys():
    cache = LRUcache(capacity=10, sweep_interval=0.05)
    cache.put("a", 1, ttl=0.05)
    time.sleep(0.2)  # give sweeper time to run at least once
    assert cache.get_stats()["current_size"] == 0
    cache.stop_sweeper()


def test_thread_safety_concurrent_puts():
    """
    Hammer the cache with concurrent writers and readers and make sure
    nothing crashes or corrupts internal state (size never exceeds capacity).
    """
    cache = LRUcache(capacity=50)
    errors = []

    def writer(thread_id: int):
        try:
            for i in range(200):
                cache.put(f"t{thread_id}-{i}", i)
                cache.get(f"t{thread_id}-{i}")
        except Exception as e:  
            errors.append(e)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert len(cache) <= 50  

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
