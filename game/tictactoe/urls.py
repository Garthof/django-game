from django.urls import URLPattern, path
from django.views.generic import TemplateView

from . import views

app_name = "tictactoe"

urlpatterns: list[URLPattern] = [
    path("", TemplateView.as_view(template_name="tictactoe/index.html")),
    path("boards/<int:id>/", views.board, name="board"),
    path(
        "boards/set_field_state/<int:board_id>/<int:row>/<int:col>",
        views.set_field_state,
        name="set_field_state",
    ),
]
