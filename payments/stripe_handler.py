import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentHandler:
    """Handle Stripe payment operations"""

    @staticmethod
    def create_payment_intent(order, user):
        """Create a Stripe Payment Intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'user_id': user.id,
                    'user_email': user.email,
                }
            )
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def confirm_payment(payment_intent_id):
        """Confirm a Stripe Payment Intent"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'status': intent.status,
                'payment_intent': intent
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_refund(payment_intent_id, amount=None):
        """Create a refund for a payment"""
        try:
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=amount  # Optional: partial refund
            )
            return {
                'success': True,
                'refund': refund
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
