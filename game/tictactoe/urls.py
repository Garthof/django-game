from django.urls import URLPattern, path

from . import views

app_name = "tictactoe"

urlpatterns: list[URLPattern] = [
    path("boards/<int:id>/", views.board, name="board"),
    path(
        "boards/set_field_state/<int:board_id>/<int:row>/<int:col>",
        views.set_field_state,
        name="set_field_state",
    ),
]
