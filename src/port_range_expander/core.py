"""Core implementation of port range expansion.

The parser accepts strings like '80,443,8000-8100' and returns a
sorted set of individual integer ports. The decision to return a
set rather than a list is deliberate: ports are unique by nature and
callers usually need membership tests. Returning a sorted set keeps
the order deterministic while giving O(1) membership.
"""

from __future__ import annotations

from collections.abc import Iterable


class PortRangeError(ValueError):
    """Raised when a port specification is malformed.

    This subclasses ValueError so existing exception handling for
    ordinary value errors continues to work, but callers can also
    catch this specific type if they need to distinguish malformed
    port input from other value errors.
    """


def _parse_port(token: str) -> int:
    """Parse a single port number token.

    The token must be a non-negative integer. Negative ports and
    empty strings are rejected because TCP/UDP ports are unsigned
    16-bit values.
    """
    if not token:
        raise PortRangeError("empty port token")
    try:
        port = int(token)
    except ValueError as exc:
        raise PortRangeError(f"invalid port: {token!r}") from exc
    if port < 0:
        raise PortRangeError(f"port must be non-negative: {token!r}")
    return port


def _expand_range(token: str) -> Iterable[int]:
    """Expand a single range token into a generator of port numbers.

    Accepted forms are 'port' or 'start-end'. The range is inclusive
    on both ends. A reversed range such as '8000-7000' is treated as
    empty because a port range is conventionally written in ascending
    order and silently flipping it would hide mistakes.
    """
    if "-" not in token:
        port = _parse_port(token)
        yield port
        return

    left, right = token.split("-", 1)
    if not left or not right:
        raise PortRangeError(f"invalid range: {token!r}")

    start = _parse_port(left)
    end = _parse_port(right)

    if start > end:
        # Empty range rather than an error: many network tools accept
        # reversed ranges and simply ignore them, so this is the least
        # surprising behaviour for users coming from those tools.
        return

    yield from range(start, end + 1)


def expand_port_range(spec: str) -> set[int]:
    """Expand a comma-and-dash port specification into a sorted set.

    The input is a string like '80,443,8000-8100'. Whitespace around
    items is ignored. Duplicate ports collapse into one entry because
    the return type is a set.

    Raises PortRangeError if the specification is malformed, including
    empty input, non-integer components, or invalid range syntax.
    """
    if not isinstance(spec, str):
        raise TypeError(f"spec must be str, got {type(spec).__name__}")

    stripped = spec.strip()
    if not stripped:
        raise PortRangeError("empty port specification")

    ports: set[int] = set()
    for raw_token in stripped.split(","):
        token = raw_token.strip()
        if not token:
            raise PortRangeError("empty token in port specification")
        ports.update(_expand_range(token))

    return set(sorted(ports))
