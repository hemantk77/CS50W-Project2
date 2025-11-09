from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    is_active = models.BooleanField(default=True)
    image = models.URLField(blank=True, null=True)