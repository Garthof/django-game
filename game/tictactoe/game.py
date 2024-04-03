from .models import Board, FieldState


def occupy_field(board: Board, row: int, col: int, new_field_state: FieldState) -> None:
    if new_field_state == FieldState.EMPTY:
        raise ValueError(f"Invalid field state {new_field_state}")

    empties_count = board.state.count(FieldState.EMPTY.value)
    if empties_count == len(board.state):
        raise Exception("No free space available")

    crosses_count = board.state.count(FieldState.X.value)
    noughts_count = board.state.count(FieldState.O.value)
    if (crosses_count > noughts_count and new_field_state == FieldState.O) or (
        crosses_count == noughts_count and new_field_state == FieldState.X
    ):
        board.set_field_state(row, col, new_field_state)
    else:
        raise Exception("Invalid movement")
