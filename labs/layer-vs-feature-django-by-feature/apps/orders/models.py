from django.db import models


class Order(models.Model):
    customer = models.ForeignKey("users.Customer", on_delete=models.PROTECT)
    total_pence = models.PositiveIntegerField()
