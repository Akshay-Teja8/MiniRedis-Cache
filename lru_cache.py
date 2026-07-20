import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Entry:
    value: Any
    expires_at: Optional[float] # None = never expires

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return self.expires_at <= time.monotonic()
    

class LRUcache:

    """
        Thread-safe in-memory LRU cache with optional per-key TTL.

        Features:
        - O(1) get/put using OrderedDict
        - Optional TTL expiration
        - Background sweeper thread
        - Thread-safe operations using RLock
        - Cache statistics

        Designed as a simplified Redis-style cache for learning
        backend systems and cache design.
    """
    
    def __init__(self, capacity: int, sweep_interval: Optional[float] = None):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self.capacity = capacity
        self.cache: "OrderedDict[Any, Entry]" = OrderedDict()
        self.lock = threading.RLock()  # Ensure thread safety

        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expired_evictions = 0

        self.sweeper_thread: Optional[threading.Thread] = None
        self.sweeper_stop_event = threading.Event()
        if sweep_interval is not None:
            self.sweeper_thread = threading.Thread(target=self._sweeper, args=(sweep_interval,), daemon=True)
            self.sweeper_thread.start()
        
    
    def _sweeper(self, sweep_interval: float):
        while not self.sweeper_stop_event.is_set():
            self.sweeper_stop_event.wait(sweep_interval)
            with self.lock:
                keys_to_remove = [key for key, entry in self.cache.items() if entry.is_expired()]
                for key in keys_to_remove:
                    del self.cache[key]
                    self.expired_evictions += 1
    
    def stop_sweeper(self):
        if self.sweeper_thread is not None:
            self.sweeper_stop_event.set()
            self.sweeper_thread.join()

    def get(self, key: Any) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                entry = self.cache.pop(key)
                if entry.is_expired():
                    self.expired_evictions += 1
                    return None
                self.cache[key] = entry  # Move to the end (most recently used)
                self.hits += 1
                return entry.value
            else:
                self.misses += 1
                return None

    def put(self, key: Any, value: Any, ttl: Optional[float] = None):
        with self.lock:
            expires_at = time.monotonic() + ttl if ttl is not None else None
            entry = Entry(value, expires_at)

            if key in self.cache:
                self.cache.pop(key)  # Remove the old entry
            elif len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)  # Remove the least recently used item
                self.evictions += 1

            self.cache[key] = entry  # Insert the new entry at the end (most recently used)
        
    def delete(self, key: Any):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.evictions += 1
                return True
            return False
        
    def clear(self):
        with self.lock:
            self.cache.clear()
    
    def contains(self, key: Any) -> bool:
        return self.get(key) is not None
    
    def __len__(self) -> int:
        with self.lock:
            return len(self.cache)

    def __del__(self):
        self.stop_sweeper()

    def __contains__(self, key: Any) -> bool:
        return self.contains(key)
    
    def get_stats(self) -> dict:
        with self.lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "expired_evictions": self.expired_evictions,
                "current_size": len(self.cache),
            }        
        
    def __repr__(self):
        return (
            f"LRUcache("
            f"size={len(self)}, "
            f"capacity={self.capacity})"
        )
    