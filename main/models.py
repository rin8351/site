from django.db import models

class VisitCounter(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"VisitCounter(count={self.count})"
