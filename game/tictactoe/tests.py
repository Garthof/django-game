import enum

from typing import cast

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse

from .game import Game, GameState
from .models import Board, FieldState


class StatusCode(enum.Enum):
    FORBIDDEN = 403


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


class TicTacToeViewTest(TestCase):
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
        cls.board4 = Board.objects.create(crosses_player=cls.user2, noughts_player=None)
        cls.board5 = Board.objects.create(crosses_player=cls.user3, noughts_player=None)


class UserBoardsTest(TicTacToeViewTest):
    def test_non_logged_users_see_no_boards(self) -> None:
        response = self.client.get(reverse("tictactoe:user_boards"))
        self.assertQuerySetEqual(response.context["board_list"], [], ordered=False)

    def test_boards_of_logged_user_are_displayed(self) -> None:
        self.client.login(username=self.user1.username, password=self.password)
        response = self.client.get(reverse("tictactoe:user_boards"))
        self.assertQuerySetEqual(
            response.context["board_list"],
            [self.board1, self.board3],
            ordered=False,
        )


class OpenBoardsTest(TicTacToeViewTest):
    def test_non_logged_users_see_no_boards(self) -> None:
        response = self.client.get(reverse("tictactoe:user_boards"))
        self.assertQuerySetEqual(response.context["board_list"], [], ordered=False)

    def test_logged_users_see_open_boards_from_other_users(self) -> None:
        self.client.login(username=self.user1.username, password=self.password)
        response = self.client.get(reverse("tictactoe:open_boards"))
        self.assertQuerySetEqual(
            response.context["board_list"],
            [self.board4, self.board5],
            ordered=False,
        )


class BoardViewTest(TicTacToeViewTest):
    def test_request_for_non_existing_board_returns_404(self) -> None:
        response = self.client.get(reverse("tictactoe:board", args=(0,)))
        self.assertEqual(response.status_code, 404)

    def test_request_for_existing_board_returns_correct_info(self) -> None:
        response = self.client.get(reverse("tictactoe:board", args=(self.board1.id,)))
        self.assertEqual(response.context["board"], self.board1)
        self.assertTrue(len(response.context["field_infos"]) > 0)


class JoinBoardTest(TicTacToeViewTest):
    def test_non_logged_users_cannot_join_board(self) -> None:
        response = self.client.post(
            reverse("tictactoe:join_board", args=(self.board4.id,))
        )
        self.assertEqual(response.status_code, StatusCode.FORBIDDEN.value)

    def test_logged_user_can_join_board(self) -> None:
        self.client.login(username=self.user1.username, password=self.password)
        self.client.post(reverse("tictactoe:join_board", args=(self.board4.id,)))

        modified_board = Board.objects.get(pk=self.board4.id)
        self.assertEqual(modified_board.noughts_player, self.user1)

    def test_logged_user_cannot_join_full_boards(self) -> None:
        self.client.login(username=self.user1.username, password=self.password)
        response = self.client.post(
            reverse("tictactoe:join_board", args=(self.board2.id,))
        )
        self.assertEqual(response.status_code, StatusCode.FORBIDDEN.value)


class SetFieldStateViewTest(TicTacToeViewTest):
    board_id = 1

    def test_non_logged_users_cannot_modify_board(self):
        response = self.client.post(
            reverse("tictactoe:set_field_state", args=(self.board_id, 0, 0))
        )
        self.assertEqual(response.status_code, StatusCode.FORBIDDEN.value)

    def test_logged_user_can_modify_their_board(self):
        board = Board.objects.get(pk=self.board_id)

        def modify_board(user: User, row: int, col: int, new_field_state: FieldState):
            self.client.login(username=user.username, password=self.password)

            self.client.post(
                reverse("tictactoe:set_field_state", args=(self.board_id, row, col))
            )

            modified_board = Board.objects.get(pk=self.board_id)
            self.assertEqual(modified_board.get_field_state(row, col), new_field_state)

            self.client.logout()

        user = board.crosses_player
        assert user is not None
        modify_board(user, 0, 0, FieldState.X)

        user = board.noughts_player
        assert user is not None
        modify_board(user, 2, 2, FieldState.O)

    def test_logged_user_cannot_modify_other_boards(self):
        board = Board.objects.get(pk=self.board_id)
        self.client.login(username=self.user3.username, password=self.password)
        response = self.client.post(
            reverse("tictactoe:set_field_state", args=(self.board_id, 0, 0))
        )
        self.assertEqual(response.status_code, StatusCode.FORBIDDEN.value)
        self.assertEqual(board, Board.objects.get(pk=self.board_id))


class CreateBoardViewTest(TicTacToeViewTest):
    def test_non_logged_users_cannot_create_board(self) -> None:
        response = self.client.post(reverse("tictactoe:create_board"))
        self.assertEqual(response.status_code, StatusCode.FORBIDDEN.value)

    def test_logged_user_can_create_board(self) -> None:
        initial_boards_count = Board.objects.count()
        self.client.login(username=self.user1.username, password=self.password)

        response = self.client.post(reverse("tictactoe:create_board"))
        self.assertEqual(response.status_code, 302)  # Status code is REDIRECT
        current_boards_count = Board.objects.count()
        self.assertEqual(current_boards_count, initial_boards_count + 1)

        response = self.client.get(cast(HttpResponseRedirect, response).url)
        self.assertEqual(response.context["board"].crosses_player, self.user1)


class GameTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.board = Board()
        cls.game = Game(cls.board)

    def test_get_state(self):
        self.board.state = "         "
        self.assertEquals(self.game.state, GameState.ON_GOING)

        self.board.state = "XXX      "
        self.assertEquals(self.game.state, GameState.CROSSES_WON)

        self.board.state = "  O  O  O"
        self.assertEquals(self.game.state, GameState.NOUGHTS_WON)

        self.board.state = "X   X   X"
        self.assertEquals(self.game.state, GameState.CROSSES_WON)

        self.board.state = "  O O O  "
        self.assertEquals(self.game.state, GameState.NOUGHTS_WON)

        self.board.state = "XOXXOXOXO"
        self.assertEquals(self.game.state, GameState.TIE)

    def test_occupy_field_with_cross(self) -> None:
        # Occupying with an empty state raises an exception
        self.assertRaises(ValueError, self.game.occupy_field, 0, 0, FieldState.EMPTY)

        # First movement with X works
        self.game.occupy_field(0, 0, FieldState.X)
        self.assertEqual(self.board.state, "X        ")

        # Two movements of X in a row raise an exception
        self.assertRaises(Exception, self.game.occupy_field, 1, 1, FieldState.X)

        # Hitting an occupied field raises an exception
        self.assertRaises(Exception, self.game.occupy_field, 0, 0, FieldState.O)

        # First valid movement with O works
        self.game.occupy_field(2, 2, FieldState.O)
        self.assertEqual(self.board.state, "X       O")

        # Two movements of O in a row raise an exception
        self.assertRaises(Exception, self.game.occupy_field, 1, 1, FieldState.O)

        # X can now move
        self.game.occupy_field(1, 1, FieldState.X)
        self.assertEqual(self.board.state, "X   X   O")

        # In a finished game, it is not possible to occupy more fields
        self.board.state = "XXX      "
        self.assertRaises(Exception, self.game.occupy_field, 1, 1, FieldState.X)
