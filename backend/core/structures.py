from typing import Generic, TypeVar, List, Optional
import threading

T = TypeVar("T")

class RingBuffer(Generic[T]):
    """
    High-Performance Circular Buffer.
    Provides O(1) time complexity for insertions and retrieval,
    engineered to eliminate memory bloat and entropic decay.
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer: List[Optional[T]] = [None] * capacity
        self.index = 0
        self.size = 0
        self._lock = threading.Lock()

    def append(self, item: T):
        """Adds a packet to the buffer, overwriting the oldest entry if capacity is reached."""
        with self._lock:
            self.buffer[self.index] = item
            self.index = (self.index + 1) % self.capacity
            if self.size < self.capacity:
                self.size += 1

    def get_all(self) -> List[T]:
        """Returns all valid packets in the buffer, ordered from oldest to newest."""
        with self._lock:
            if self.size < self.capacity:
                return [x for x in self.buffer[:self.index] if x is not None]
            else:
                # Reorder the circular buffer
                return [self.buffer[i % self.capacity] for i in range(self.index, self.index + self.capacity) if self.buffer[i % self.capacity] is not None]

    def clear(self):
        """Purges the buffer memory."""
        with self._lock:
            self.buffer = [None] * self.capacity
            self.index = 0
            self.size = 0
