from django.db import models


class Product(models.Model):
    json = models.JSONField('JSON-строка')

    def __str__(self) -> str:
        return str(self.id)
