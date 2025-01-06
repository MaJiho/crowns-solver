import unittest

from board.board import Board
from debug_utils import load_board_state
from drawing_utils import draw_board_with_pygame
from settings import load_settings


class TestDrawingBoard(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by loading the board state.
        This method is executed before each test.
        """
        load_settings("../settings.json")
        self.board: Board = load_board_state()
        if not self.board:
            self.fail("Failed to load board state for testing.")

    def test_draw(self):
        draw_board_with_pygame(self.board)
