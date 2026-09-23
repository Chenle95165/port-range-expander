"""Port range expansion library.

Exposes the primary API for converting comma-and-dash port
specifications into a sorted set of individual port numbers.
"""

from .core import expand_port_range

__all__ = ["expand_port_range"]
