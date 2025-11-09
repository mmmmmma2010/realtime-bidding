from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/bids/(?P<product_id>\d+)/$', consumer.BiddingConsumer.as_asgi()),
]