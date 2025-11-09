import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from decimal import Decimal

from .models import Product, Bid

class BiddingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # URL: /ws/bids/<product_id>/
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        self.group_name = f'product_{self.product_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send current highest bid on connect
        highest = await self.get_highest_bid()
        await self.send_json({
            'type': 'highest_bid',
            'amount': str(highest),
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'place_bid':
            amount = data.get('amount')
            bidder = data.get('bidder', 'anonymous')
            try:
                amount = Decimal(str(amount))
            except Exception:
                await self.send_json({'type': 'error', 'message': 'Invalid amount'})
                return

            # validate and create
            accepted, current = await self.place_bid(bidder, amount)
            if not accepted:
                await self.send_json({'type': 'rejected', 'message': f'Bid too low (current: {current})'})
                return

            # Broadcast new highest to group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'broadcast_highest',
                    'amount': str(amount),
                    'bidder': bidder,
                }
            )

    async def broadcast_highest(self, event):
        await self.send_json({
            'type': 'highest_bid',
            'amount': event['amount'],
            'bidder': event.get('bidder')
        })

    @database_sync_to_async
    def get_highest_bid(self):
        try:
            product = Product.objects.get(pk=self.product_id)
            hb = product.bids.order_by('-amount').first()
            return hb.amount if hb else product.starting_price
        except Product.DoesNotExist:
            return 0

    @database_sync_to_async
    def place_bid(self, bidder_name, amount: Decimal):
        products = Product.objects.first()
        if not products:
            products = Product.objects.create(name='test product', description='this is atest product description', starting_price=0)
        try:
            product = Product.objects.filter(pk=self.product_id).first()
        except Product.DoesNotExist:
            return False, 'product missing'

        if not product:
            return False, 'product missing'

        current_high = product.bids.order_by('-amount').first()
        current_amount = current_high.amount if current_high else product.starting_price

        # Simple rule: must be strictly greater than current highest
        if amount <= current_amount:
            return False, str(current_amount)

        bid = Bid.objects.create(product=product, bidder_name=bidder_name, amount=amount)
        return True, str(bid.amount)