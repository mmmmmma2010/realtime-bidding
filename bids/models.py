from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starting_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def highest_bid(self):
        hb = self.bids.order_by('-amount').first()
        return hb.amount if hb else self.starting_price

class Bid(models.Model):
    product = models.ForeignKey(Product, related_name='bids', on_delete=models.CASCADE)
    bidder_name = models.CharField(max_length=150, default='anonymous')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount', 'created_at']

    def __str__(self):
        return f"{self.bidder_name}: {self.amount} on {self.product.name}"