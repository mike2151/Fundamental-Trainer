from django.db import models
import uuid
from random import randint
from django.db.models.aggregates import Count


def make_uuid():
   return str(uuid.uuid4()).replace("-", "_")

def make_pk():
    num_digits = 16
    range_start = 10**(num_digits-1)
    range_end = (10**num_digits)-1
    return randint(range_start, range_end)

class Challenge(models.Model):
    def upload_path_handler(instance, filename):
        return "{id}/{file}".format(id=instance.pk, file=filename)

    # website data
    is_premium = models.BooleanField(default=False)

    # challenge data
    stock_name = models.CharField(max_length=512)
    stock_ticker = models.CharField(max_length=12)
    stock_industry = models.CharField(max_length=256)
    stock_sector = models.CharField(max_length=256)
    time_label_full = models.CharField(max_length=16)
    time_label_url = models.CharField(max_length=16)
    stock_description = models.TextField()
    window_date = models.DateTimeField()
    display_id = models.BigIntegerField(default=make_pk, unique=True, db_index=True)
    result = models.BooleanField()
    result_amount_percent = models.CharField(max_length=16)
    historic_data = models.TextField()

    # financial files
    statement_8k = models.FileField(blank=True, upload_to=upload_path_handler)
    statement_10k = models.FileField(blank=True, upload_to=upload_path_handler)
    statement_10q = models.FileField(blank=True, upload_to=upload_path_handler)
    statement_13f_hr = models.FileField(blank=True, upload_to=upload_path_handler)
    statement_13_g = models.FileField(blank=True, upload_to=upload_path_handler)
    statement_sd = models.FileField(blank=True, upload_to=upload_path_handler)

    def __str__(self):
        return self.stock_ticker + ": " + str(self.window_date)
