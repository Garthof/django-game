from typing import Any

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse

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
            "tictactoe:set_field_state", args=[self.board.id, self.row, self.col]
        )


def index(request: HttpRequest) -> HttpResponse:
    user_boards = None

    if request.user.is_authenticated:
        user_boards = Board.objects.filter(
            crosses_player=request.user
        ) | Board.objects.filter(noughts_player=request.user)

    context: dict[str, Any] = {"user_boards": user_boards}
    return render(request, "tictactoe/index.html", context)


def board(request: HttpRequest, id: int) -> HttpResponse:
    try:
        board = Board.objects.get(pk=id)
    except Board.DoesNotExist:
        raise Http404(f"Board {id} does not exist")

    field_infos = [[FieldInfo(board, row, col) for col in range(3)] for row in range(3)]
    context: dict[str, Any] = {"board": board, "field_infos": field_infos}
    return render(request, "tictactoe/board.html", context)


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

    board.set_field_state(row, col, new_field_state)
    board.save()

    return HttpResponse(new_field_state.value)
