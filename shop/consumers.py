from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from .models import Product, Interaction, Rating
from .recommendation import load_data, train_algorithm, get_top_n_recommendations
from channels.exceptions import StopConsumer

class InteractionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join room
        self.room_group_name = f'user_{self.scope["user"].id}_interactions'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        raise StopConsumer()

    async def receive(self, text_data):
            text_data_json = json.loads(text_data)
            isbn = text_data_json['isbn']
            action = text_data_json['action']
            user = self.scope['user']

            if user.is_authenticated:
                # Process interaction
                product = await sync_to_async(Product.objects.get)(isbn=isbn)

                interaction, created = await sync_to_async(Interaction.objects.get_or_create)(
                    user=user, product=product
                )
                rating_value = 0.0

                print(f"Received action: {action}, ISBN: {isbn}, User ID: {user.id}")
                if action == 'like':
                    interaction.liked = True
                    rating_value = interaction.calculate_interaction_value()
                elif action == 'add_to_cart':
                    interaction.added_to_cart = True
                    rating_value = interaction.calculate_interaction_value()
                elif action == 'click':
                    #print(f"Time spent: {text_data_json.get('time_spent')}")
                    interaction.clicks += 1
                    rating_value = interaction.calculate_interaction_value()

                await sync_to_async(interaction.save)()

                # Update or create the rating
                rating, created = await sync_to_async(Rating.objects.get_or_create)(
                    user=user, product=product
                )
                await sync_to_async(rating.update_rating)(rating_value)

                # Send the updated rating to the client
                await self.send(text_data=json.dumps({
                    'status': 'success',
                    'rating': rating.rating
                }))

            else:
                await self.send(text_data=json.dumps({'status': 'error', 'message': 'User not authenticated'}))

