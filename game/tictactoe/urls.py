from django.urls import path

from . import views

app_name = "tictactoe"

urlpatterns = [path("boards/<int:id>/", views.board, name="board")]
