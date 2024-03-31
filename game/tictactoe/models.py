import enum

from django.contrib.auth.models import User
from django.db import models


class FieldState(enum.Enum):
    X = "X"
    O = "O"
    EMPTY = " "


class Board(models.Model):
    noughts_player = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="noughts_players"
    )
    crosses_player = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="crosses_players"
    )
    state = models.CharField(max_length=9, default=" " * 9)

    def __str__(self) -> str:
        return (
            f"X = {self.crosses_player} O = {self.noughts_player} status = {self.state}"
        )

    def get_field_state(self, row: int, col: int) -> FieldState:
        if 0 <= row < 3 and 0 <= col < 3:
            return FieldState(self.state[row * 3 + col])
        else:
            raise ValueError(f"Invalid row or col {row, col}")

    def set_field_state(self, row: int, col: int, field_state: FieldState) -> None:
        if 0 <= row < 3 and 0 <= col < 3:
            list_state = list(self.state)
            list_state[row * 3 + col] = field_state.value
            self.state = "".join(list_state)
        else:
            raise ValueError(f"Invalid row or col {row, col}")
