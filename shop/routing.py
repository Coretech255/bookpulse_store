from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/interactions/<int:product_id>/', consumers.InteractionConsumer.as_asgi()),
]
