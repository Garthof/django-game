from django.db import models


class Player(models.Model):
    handle = models.CharField(max_length=16, unique=True)

    def __str__(self) -> str:
        return self.handle


class Board(models.Model):
    noughtsPlayer = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, related_name="noughts_players"
    )
    crossesPlayer = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, related_name="crosses_players"
    )
    status = models.CharField(max_length=9)

    def __str__(self) -> str:
        return (
            f"X = {self.crossesPlayer} O = {self.noughtsPlayer} status = {self.status}"
        )
