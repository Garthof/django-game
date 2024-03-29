from django.test import TestCase

from .models import Board, FieldState


class BoardModelTests(TestCase):
    def test_get_field_state_at_wrong_position_raises_exception(self) -> None:
        board = Board()
        self.assertRaises(ValueError, board.get_field_state, -1, +0)
        self.assertRaises(ValueError, board.get_field_state, +0, -1)
        self.assertRaises(ValueError, board.get_field_state, +3, +0)
        self.assertRaises(ValueError, board.get_field_state, +0, +3)

    def test_set_field_state_at_wrong_position_raises_exception(self) -> None:
        board = Board()
        self.assertRaises(ValueError, board.set_field_state, -1, +0, FieldState.EMPTY)
        self.assertRaises(ValueError, board.set_field_state, +0, -1, FieldState.EMPTY)
        self.assertRaises(ValueError, board.set_field_state, +3, +0, FieldState.EMPTY)
        self.assertRaises(ValueError, board.set_field_state, +0, +3, FieldState.EMPTY)

    def test_get_field_state_returns_correct_field_state(self) -> None:
        board = Board(state="XOXO X  O")
        self.assertEqual(board.get_field_state(0, 0), FieldState.X)
        self.assertEqual(board.get_field_state(1, 1), FieldState.EMPTY)
        self.assertEqual(board.get_field_state(2, 2), FieldState.O)

    def test_set_field_state_correctly_changes_board_state(self) -> None:
        board = Board(state="XOXO X  O")

        board.set_field_state(0, 0, FieldState.O)
        self.assertEqual(board.state, "OOXO X  O")
        board.set_field_state(1, 1, FieldState.X)
        self.assertEqual(board.state, "OOXOXX  O")
        board.set_field_state(2, 2, FieldState.EMPTY)
        self.assertEqual(board.state, "OOXOXX   ")
