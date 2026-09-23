"""Tests for port range expansion."""

import unittest

from port_range_expander import expand_port_range
from port_range_expander.core import PortRangeError


class TestExpandPortRange(unittest.TestCase):
    def test_single_port(self):
        self.assertEqual(expand_port_range("80"), {80})

    def test_multiple_ports(self):
        self.assertEqual(expand_port_range("80,443"), {80, 443})

    def test_simple_range(self):
        self.assertEqual(expand_port_range("8000-8002"), {8000, 8001, 8002})

    def test_mixed_spec(self):
        self.assertEqual(
            expand_port_range("80,443,8000-8100"),
            set(range(8000, 8101)) | {80, 443},
        )

    def test_whitespace_is_ignored(self):
        self.assertEqual(expand_port_range(" 80 , 443 , 8000 - 8100 "), {80, 443} | set(range(8000, 8101)))

    def test_duplicate_ports_collapse(self):
        self.assertEqual(expand_port_range("80,80,443"), {80, 443})

    def test_overlapping_ranges_collapse(self):
        self.assertEqual(expand_port_range("8000-8005,8003-8010"), set(range(8000, 8011)))

    def test_reversed_range_is_empty(self):
        self.assertEqual(expand_port_range("8000-7000"), set())

    def test_empty_input_raises(self):
        with self.assertRaises(PortRangeError):
            expand_port_range("")

    def test_whitespace_only_raises(self):
        with self.assertRaises(PortRangeError):
            expand_port_range("   ")

    def test_empty_token_raises(self):
        with self.assertRaises(PortRangeError):
            expand_port_range("80,,443")

    def test_invalid_port_raises(self):
        with self.assertRaises(PortRangeError):
            expand_port_range("abc")

    def test_negative_port_raises(self):
        with self.assertRaises(PortRangeError):
            expand_port_range("-1")

    def test_invalid_range_missing_end_raises(self):
        with self.assertRaises(PortRangeError):
            expand_port_range("8000-")

    def test_invalid_range_missing_start_raises(self):
        with self.assertRaises(PortRangeError):
            expand_port_range("-8000")

    def test_non_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            expand_port_range(80)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
