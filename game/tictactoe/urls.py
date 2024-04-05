from django.urls import URLPattern, path

from . import views

app_name = "tictactoe"

urlpatterns: list[URLPattern] = [
    path("", views.index, name="index"),
    path("boards/user_boards/", views.user_boards, name="user_boards"),
    path("boards/open_boards/", views.open_boards, name="open_boards"),
    path("boards/create/", views.create_board, name="create_board"),
    path("boards/<int:board_id>/", views.board, name="board"),
    path("boards/detail/<int:board_id>/", views.board_detail, name="board_detail"),
    path(
        "boards/set_field_state/<int:board_id>/<int:row>/<int:col>",
        views.set_field_state,
        name="set_field_state",
    ),
]
