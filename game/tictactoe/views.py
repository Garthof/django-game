from typing import Any

from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse

from .game import Game, GameState
from .models import Board, FieldState


class FieldInfo:
    board: Board
    row: int
    col: int
    state: FieldState

    def __init__(self, board: Board, row: int, col: int) -> None:
        self.board = board
        self.row = row
        self.col = col
        self.state = board.get_field_state(row, col)

    def url_set_field_state(self) -> str:
        return reverse(
            "tictactoe:set_field_state", args=(self.board.id, self.row, self.col)
        )


def index(request: HttpRequest) -> HttpResponse:
    user_boards = None

    if request.user.is_authenticated:
        user_boards = Board.objects.filter(
            crosses_player=request.user
        ) | Board.objects.filter(noughts_player=request.user)

    context: dict[str, Any] = {"user_boards": user_boards}
    return render(request, "tictactoe/index.html", context)


def board(request: HttpRequest, board_id: int) -> HttpResponse:
    return render(request, "tictactoe/board.html", generate_board_context(board_id))


def board_detail(request: HttpRequest, board_id: int) -> HttpResponse:
    return render(
        request, "tictactoe/board_detail.html", generate_board_context(board_id)
    )


def set_field_state(
    request: HttpRequest, board_id: int, row: int, col: int
) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to perform this action")

    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        raise Http404(f"Board {id} does not exist")

    if request.user == board.crosses_player:
        new_field_state = FieldState.X
    elif request.user == board.noughts_player:
        new_field_state = FieldState.O
    else:
        return HttpResponseForbidden("You must join the board to perform this action")

    game = Game(board)
    try:
        game.occupy_field(row, col, new_field_state)
        board.save()
    except Exception as e:
        return HttpResponseForbidden(str(e))

    return board_detail(request, board_id)


def create_board(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to perform this action")

    new_board = Board.objects.create(crosses_player=request.user)

    redirect_url = reverse("tictactoe:board", args=(new_board.id,))
    if request.headers.get("HX-Request"):
        response = HttpResponse()
        response.headers["HX-Redirect"] = redirect_url  # type: ignore
    else:
        response = HttpResponseRedirect(redirect_url)

    return response


def generate_board_context(board_id: int) -> dict[str, Any]:
    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        raise Http404(f"Board {board_id} does not exist")

    player_victory_text = (
        lambda player, symbol: f"Game is over. Player {player} ({symbol}) won"
    )
    game = Game(board)
    match game.state:
        case GameState.CROSSES_WON | GameState.NOUGHTS_WON:
            victory_text = player_victory_text(board.crosses_player, game.state.value)
        case GameState.TIE:
            victory_text = "Game has ended with a tie"
        case _:
            victory_text = None

    field_infos = [[FieldInfo(board, row, col) for col in range(3)] for row in range(3)]

    return {
        "victory_text": victory_text,
        "board": board,
        "field_infos": field_infos,
    }
