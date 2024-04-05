from typing import Any

from django.db.models import Q
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
    return render(request, "tictactoe/index.html")


def user_boards(request: HttpRequest) -> HttpResponse:
    board_list = None

    if request.user.is_authenticated:
        board_list = Board.objects.filter(
            crosses_player=request.user
        ) | Board.objects.filter(noughts_player=request.user)

    context: dict[str, Any] = {"board_list": board_list}
    return render(request, "tictactoe/board_list.html", context)


def open_boards(request: HttpRequest) -> HttpResponse:
    board_list = None

    if request.user.is_authenticated:
        board_list = Board.objects.filter(
            (Q(crosses_player=None) & ~Q(noughts_player=request.user))
            | (~Q(crosses_player=request.user) & Q(noughts_player=None))
        )

    context: dict[str, Any] = {"board_list": board_list}
    return render(request, "tictactoe/board_list.html", context)


def board(request: HttpRequest, board_id: int) -> HttpResponse:
    context = generate_board_detail_context(board_id)

    if request.user.is_authenticated:
        board = Board.objects.get(pk=board_id)
        if (
            board.crosses_player != request.user
            and board.noughts_player != request.user
        ):
            context |= {"user_can_join": True}

    return render(request, "tictactoe/board.html", context)


def board_detail(request: HttpRequest, board_id: int) -> HttpResponse:
    return render(
        request, "tictactoe/board_detail.html", generate_board_detail_context(board_id)
    )


def join_board(request: HttpRequest, board_id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to perform this action")

    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        raise Http404(f"Board {id} does not exist")

    if not board.crosses_player:
        board.crosses_player = request.user  # type: ignore
        board.save()
    elif not board.noughts_player:
        board.noughts_player = request.user  # type: ignore
        board.save()
    else:
        return HttpResponseForbidden("No free space available to join board")

    redirect_url = reverse("tictactoe:board", args=(board_id,))
    if request.headers.get("HX-Request"):
        # Redirects are triggered by HTMX if the response's status code is 200 and the
        # header contains the field "HX-Redirect" with the target URL
        response = HttpResponse()
        response.headers["HX-Redirect"] = redirect_url  # type: ignore
    else:
        response = HttpResponseRedirect(redirect_url)

    return response


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
        # Redirects are triggered by HTMX if the response's status code is 200 and the
        # header contains the field "HX-Redirect" with the target URL
        response = HttpResponse()
        response.headers["HX-Redirect"] = redirect_url  # type: ignore
    else:
        response = HttpResponseRedirect(redirect_url)

    return response


def generate_board_detail_context(board_id: int) -> dict[str, Any]:
    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        raise Http404(f"Board {board_id} does not exist")

    player_victory_text = (
        lambda player, symbol: f"Game is over. Player {player} ({symbol}) won!"
    )
    game = Game(board)
    match game.state:
        case GameState.CROSSES_WON:
            victory_text = player_victory_text(board.crosses_player, FieldState.X.value)
        case GameState.NOUGHTS_WON:
            victory_text = player_victory_text(board.noughts_player, FieldState.O.value)
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
