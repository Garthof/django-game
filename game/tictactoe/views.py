from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Board


def board(request: HttpRequest, id: int) -> HttpResponse:
    try:
        board = Board.objects.get(pk=id)
    except Board.DoesNotExist:
        raise Http404(f"Board {id} does not exist")

    field_states = [
        [board.get_field_state(row, col) for col in range(3)] for row in range(3)
    ]
    context = {"board": board, "field_states": field_states}
    return render(request, "tictactoe/board.html", context)
