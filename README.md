# Port Range Expander

Expands comma-and-dash port specifications like `'80,443,8000-8100'` into a sorted set of individual port numbers.

```python
from port_range_expander import expand_port_range

ports = expand_port_range("80,443,8000-8100")
print(ports)
# {80, 443, 8000, 8001, ..., 8100}
```

## Why this library exists

Network tools and configuration files often accept port lists in a compact human-readable form: `80,443,8000-8100`. Programmatic consumers typically need the individual port numbers to open sockets, build firewall rules, or validate service availability. This library provides a tiny, dependency-free parser for that format.

A deliberate trade-off is the return type: a sorted `set` rather than a list. Ports are unique by nature, and callers usually want membership tests (`if port in ports`) more than positional access. Using a set also collapses duplicates naturally.

## Edge case to note

Reversed ranges such as `'8000-7000'` are treated as empty rather than raising an error. This matches the behaviour of many command-line tools that silently ignore reversed ranges, but it means a typo can produce an unexpectedly empty set. If you need stricter validation, check for empty output after parsing.

Malformed input — empty strings, non-integer tokens, missing range endpoints, negative ports — raises `PortRangeError`, a subclass of `ValueError`.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

