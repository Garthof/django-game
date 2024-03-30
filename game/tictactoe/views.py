from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Board


def board(request: HttpRequest, id: int) -> HttpResponse:
    try:
        board = Board.objects.get(pk=id)
    except Board.DoesNotExist:
        raise Http404(f"Board {id} does not exist")

    context = {"board": board}
    return render(request, "tictactoe/board.html", context)
