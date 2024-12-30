from django.db import models


class Habit(models.Model):
    name = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    times_completed = models.IntegerField(default=0)

    owner = models.ForeignKey(
        "auth.User", related_name="habits", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class UserScore(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    accomplished_habits = models.ManyToManyField(Habit)

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.score}"
