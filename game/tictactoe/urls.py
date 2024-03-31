from django.urls import path

from . import views

app_name = "tictactoe"

urlpatterns = [
    path("boards/<int:id>/", views.board, name="board"),
    path(
        "boards/set_field_state/<int:board_id>/<int:row>/<int:col>",
        views.set_field_state,
        name="set_field_state",
    ),
]
