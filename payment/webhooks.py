import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error("Invalid payload: %s", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error("Invalid signature: %s", e)
        return HttpResponse(status=400)

    # Log the event type to debug
    logger.info(f"Received Stripe event: {event.type}")

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
                # Log the order
                logger.info(f"Order found: {order.id}, updating paid status.")

            except Order.DoesNotExist:
                logger.error(f"Order with id {session.client_reference_id} does not exist.")
                return HttpResponse(status=404)
            
            # store Stripe payment ID
            order.stripe_id = session.payment_intent
            order.paid = True
            order.save()

    return HttpResponse(status=200)
