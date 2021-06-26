from abc import ABC, abstractmethod
from collections.abc import Set


class Watcher(ABC):
    """A context for monitoring filesystem events."""

    @abstractmethod
    def start(self):
        """Start watching for filesystem access events."""
        
    @abstractmethod
    def stop(self) -> Set[str]:
        """Stop watching access events.
        
        Returns all paths known to have been accessed while
        the watcher was active.
        """
