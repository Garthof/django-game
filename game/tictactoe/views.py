from django.http import Http404, HttpRequest, HttpResponse
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


def board(request: HttpRequest, id: int) -> HttpResponse:
    try:
        board = Board.objects.get(pk=id)
    except Board.DoesNotExist:
        raise Http404(f"Board {id} does not exist")

    field_infos = [[FieldInfo(board, row, col) for col in range(3)] for row in range(3)]
    context = {"board": board, "field_infos": field_infos}
    return render(request, "tictactoe/board.html", context)


def set_field_state(
    request: HttpRequest, board_id: int, row: int, col: int
) -> HttpResponse:
    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        raise Http404(f"Board {id} does not exist")

    new_field_state = FieldState.X
    board.set_field_state(row, col, new_field_state)
    board.save()

    return HttpResponse(new_field_state.value)
