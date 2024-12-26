import unittest

from board.line import trim_segment


class Cell:
    def __init__(self, state="empty"):
        self.state = state

    def is_empty(self) -> bool:
        return self.state == "empty"

    def __repr__(self):
        return f"Cell(state={self.state})"


class TestTrimSegment(unittest.TestCase):
    def test_trim_both_ends(self):
        segment = [Cell("cross"), Cell("empty"), Cell("crown"), Cell("empty"), Cell("cross")]
        expected = [Cell("empty"), Cell("crown"), Cell("empty")]
        trimmed = trim_segment(segment)
        self.assertEqual([cell.state for cell in trimmed], [cell.state for cell in expected])

    def test_trim_only_left(self):
        segment = [Cell("cross"), Cell("crown"), Cell("empty"), Cell("empty")]
        expected = [Cell("empty"), Cell("empty")]
        trimmed = trim_segment(segment)
        self.assertEqual([cell.state for cell in trimmed], [cell.state for cell in expected])

    def test_trim_only_right(self):
        segment = [Cell("empty"), Cell("empty"), Cell("crown"), Cell("cross")]
        expected = [Cell("empty"), Cell("empty")]
        trimmed = trim_segment(segment)
        self.assertEqual([cell.state for cell in trimmed], [cell.state for cell in expected])

    def test_no_trim_needed(self):
        segment = [Cell("empty"), Cell("crown"), Cell("empty")]
        expected = [Cell("empty"), Cell("crown"), Cell("empty")]
        trimmed = trim_segment(segment)
        self.assertEqual([cell.state for cell in trimmed], [cell.state for cell in expected])

    def test_empty_segment(self):
        segment = []
        expected = []
        trimmed = trim_segment(segment)
        self.assertEqual(trimmed, expected)

    def test_all_non_empty_segment(self):
        segment = [Cell("cross"), Cell("crown"), Cell("cross")]
        expected = []
        trimmed = trim_segment(segment)
        self.assertEqual(trimmed, expected)
