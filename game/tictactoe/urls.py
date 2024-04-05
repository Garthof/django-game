from django.urls import URLPattern, path

from . import views

app_name = "tictactoe"

urlpatterns: list[URLPattern] = [
    path("", views.index, name="index"),
    path("boards/<int:board_id>/", views.board, name="board"),
    path("boards/detail/<int:board_id>/", views.board_detail, name="board_detail"),
    path(
        "boards/set_field_state/<int:board_id>/<int:row>/<int:col>",
        views.set_field_state,
        name="set_field_state",
    ),
]
