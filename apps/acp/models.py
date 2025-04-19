from django.db import models


class AccountHistory(models.Model):
    account = models.CharField(max_length=50)
    date = models.DateField()
    period_type = models.CharField(max_length=10)  # 'daily', 'weekly', 'monthly', 'yearly'
    total_assets = models.FloatField()
    market_value = models.FloatField()
    cash = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['account', 'date']),
            models.Index(fields=['account', 'period_type'])
        ]
# Create your models here.
