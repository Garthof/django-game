import enum

from .models import Board, FieldState


class GameState(enum.Enum):
    ON_GOING = enum.auto()
    CROSSES_WON = enum.auto()
    NOUGHTS_WON = enum.auto()
    TIE = enum.auto()


class Game:
    board: Board

    def __init__(self, board: Board) -> None:
        self.board = board

    @property
    def state(self) -> GameState:
        if self.__is_match_three(FieldState.X):
            return GameState.CROSSES_WON
        elif self.__is_match_three(FieldState.O):
            return GameState.NOUGHTS_WON
        elif self.board.state.count(FieldState.EMPTY.value) == 0:
            return GameState.TIE
        else:
            return GameState.ON_GOING

    def occupy_field(self, row: int, col: int, new_field_state: FieldState) -> None:
        if new_field_state == FieldState.EMPTY:
            raise ValueError(f"Invalid field state {new_field_state}")

        field_state = self.board.get_field_state(row, col)
        if field_state != FieldState.EMPTY:
            raise Exception("Occupied space cannot be changed")

        if self.state != GameState.ON_GOING:
            raise Exception("Game is over")

        crosses_count = self.board.state.count(FieldState.X.value)
        noughts_count = self.board.state.count(FieldState.O.value)
        if (crosses_count > noughts_count and new_field_state == FieldState.O) or (
            crosses_count == noughts_count and new_field_state == FieldState.X
        ):
            self.board.set_field_state(row, col, new_field_state)
        else:
            raise Exception("Invalid movement")

    def __is_match_three(self, field_state: FieldState) -> bool:
        field_states = [
            [self.board.get_field_state(row, col) for col in range(3)]
            for row in range(3)
        ]

        # Check rows
        for col in range(3):
            if (
                field_state
                == field_states[col][0]
                == field_states[col][1]
                == field_states[col][2]
            ):
                return True

        # Check cols
        for col in range(3):
            if (
                field_state
                == field_states[0][col]
                == field_states[1][col]
                == field_states[2][col]
            ):
                return True

        # Check diagonals
        if (
            field_state
            == field_states[0][0]
            == field_states[1][1]
            == field_states[2][2]
        ):
            return True

        if (
            field_state
            == field_states[0][2]
            == field_states[1][1]
            == field_states[2][0]
        ):
            return True

        return False
