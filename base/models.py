from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class Telegram(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    key = models.CharField(max_length=200)
    authorised_flag = models.BooleanField()
    chat_id = models.IntegerField(null=True)


    



class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    stock = models.CharField(max_length=200)
    pos = models.IntegerField()
    neg = models.IntegerField()
    pos_share = models.IntegerField()
    tot_news = models.IntegerField()
    #recs
    rec_hold = models.IntegerField()
    rec_buy = models.IntegerField()
    rec_sell = models.IntegerField()
    #preds
    anomalies = models.IntegerField() #0 or 1
    pred_5_days = models.FloatField()
    pred_20_days = models.FloatField()
    pred_arima_trend = models.IntegerField()


    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return str(self.name)
    
    





# Create your models here.
