from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.password = "test"
        cls.user1 = User.objects.create_user(username="test1", password=cls.password)
        cls.user2 = User.objects.create_user(username="test2", password=cls.password)
        cls.user3 = User.objects.create_user(username="test3", password=cls.password)
        cls.board1 = Board.objects.create(
            crosses_player=cls.user1, noughts_player=cls.user2
        )
        cls.board2 = Board.objects.create(
            crosses_player=cls.user2, noughts_player=cls.user3
        )
        cls.board3 = Board.objects.create(
            crosses_player=cls.user3, noughts_player=cls.user1
        )

    def test_boards_of_logged_user_are_displayed(self) -> None:
        self.client.login(username=self.user1.username, password=self.password)
        response = self.client.get(reverse("tictactoe:index"))
        self.assertQuerySetEqual(
            response.context["user_boards"], [self.board1, self.board3], ordered=False
        )

    def test_non_logged_users_see_no_boards(self) -> None:
        response = self.client.get(reverse("tictactoe:index"))
        self.assertQuerySetEqual(response.context["user_boards"], [], ordered=False)
