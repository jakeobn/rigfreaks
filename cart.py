import os
import json
import stripe
import uuid
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from werkzeug.utils import secure_filename
from models import User, Build, Order, Cart, OrderStatus
from utils import load_component_data, calculate_total_price, check_compatibility
from forms import CheckoutForm, ShippingForm

# Initialize Stripe with the API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Get domain from environment variables
DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0])

# Create blueprint
cart_bp = Blueprint('cart', __name__)


def generate_order_number():
    """Generate a random order number."""
    return 'ORD-' + str(uuid.uuid4())[:8].upper()


def get_or_create_cart(session_id=None):
    """Get the current cart for the user or create a new one."""
    if current_user.is_authenticated:
        # Check if user has an existing cart
        cart = Cart.query.filter_by(user_id=current_user.id).first()
    else:
        # For non-logged-in users, use session ID to track cart
        if not session_id:
            session_id = session.get('cart_session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['cart_session_id'] = session_id
        
        cart = Cart.query.filter_by(session_id=session_id).first()
    
    # If no cart exists, create a new one
    if not cart:
        cart = Cart(
            user_id=current_user.id if current_user.is_authenticated else None,
            session_id=None if current_user.is_authenticated else session_id
        )
        db.session.add(cart)
        db.session.commit()
    
    return cart


@cart_bp.route('/cart')
def view_cart():
    """Display the shopping cart."""
    cart = get_or_create_cart()
    build_details = None
    
    if cart and cart.build_id:
        # If there's a saved build in the cart
        build = Build.query.get(cart.build_id)
        if build:
            build_details = {
                'name': build.name,
                'description': build.description,
                'components': {}
            }
    
    elif cart and cart.build_config:
        # If there's a custom build in the cart
        build_config = cart.get_build_config()
        
        # Load component details
        if build_config:
            components = load_component_data()
            config_details = {}
            
            for category, component_id in build_config.items():
                category_components = components.get(category, [])
                component = next((c for c in category_components if c['id'] == component_id), None)
                if component:
                    config_details[category] = component
            
            build_details = {
                'name': 'Custom PC Build',
                'description': 'Your custom configured PC',
                'components': config_details
            }
    
    return render_template('cart/cart.html', cart=cart, build_details=build_details)


@cart_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add a build to the cart."""
    if 'pc_config' not in session or not session['pc_config']:
        flash("Please build a PC configuration first", "warning")
        return redirect(url_for('builder'))
    
    # Get or create cart
    cart = get_or_create_cart()
    
    # If cart already has items, clear them first
    if cart.build_id or cart.build_config:
        flash("Your cart has been updated with the new build", "info")
    
    # Calculate total price
    config = session.get('pc_config', {})
    total_price = calculate_total_price(config)
    
    # Update cart with current build config
    cart.build_id = None  # Reset any saved build reference
    cart.set_build_config(config)
    cart.total_price = total_price
    cart.quantity = 1
    
    db.session.commit()
    
    flash("Your custom PC has been added to cart!", "success")
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    """Remove item from cart."""
    cart = get_or_create_cart()
    
    if cart:
        cart.build_id = None
        cart.build_config = None
        cart.quantity = 0
        cart.total_price = 0
        db.session.commit()
    
    flash("Item removed from cart", "info")
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/update', methods=['POST'])
def update_cart():
    """Update cart items."""
    cart = get_or_create_cart()
    
    if cart:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        if quantity > 10:
            quantity = 10
        
        cart.quantity = quantity
        db.session.commit()
        
        flash("Cart updated", "info")
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout process."""
    cart = get_or_create_cart()
    
    # If cart is empty, redirect to cart page
    if not cart or not cart.build_config or cart.total_price <= 0:
        flash("Your cart is empty", "warning")
        return redirect(url_for('cart.view_cart'))
    
    # Get build details for display
    build_config = cart.get_build_config()
    build_details = {
        'name': 'Custom PC Build',
        'description': 'Your custom configured PC',
        'components': {}
    }
    
    if build_config:
        components = load_component_data()
        for category, component_id in build_config.items():
            category_components = components.get(category, [])
            component = next((c for c in category_components if c['id'] == component_id), None)
            if component:
                build_details['components'][category] = component
    
    form = CheckoutForm()
    
    if form.validate_on_submit():
        # Create a new order
        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            order_number=generate_order_number(),
            status=OrderStatus.PENDING.value,
            total_amount=cart.total_price * cart.quantity,
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address_line1=form.address_line1.data,
            address_line2=form.address_line2.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            country=form.country.data
        )
        
        # Store build configuration with the order
        if cart.build_id:
            order.build_id = cart.build_id
        elif cart.build_config:
            order.set_build_config(cart.get_build_config())
        
        db.session.add(order)
        db.session.commit()
        
        # Store order ID in session for the next step
        session['current_order_id'] = order.id
        
        return redirect(url_for('cart.payment'))
    
    return render_template('cart/checkout.html', form=form, cart=cart, build_details=build_details)


@cart_bp.route('/payment')
def payment():
    """Payment processing."""
    # Get the current order from session
    order_id = session.get('current_order_id')
    if not order_id:
        flash("Invalid checkout process. Please try again.", "danger")
        return redirect(url_for('cart.view_cart'))
    
    order = Order.query.get(order_id)
    if not order:
        flash("Order not found. Please try again.", "danger")
        return redirect(url_for('cart.view_cart'))
    
    # Create a Stripe payment intent
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Amount in cents
            currency='usd',
            metadata={
                'order_id': order.id,
                'order_number': order.order_number
            }
        )
        
        # Store the payment intent ID in the order
        order.payment_id = payment_intent.id
        db.session.commit()
        
        # Get the Stripe publishable key for the frontend
        stripe_key = 'pk_test_TYooMQauvdEDq54NiTphI7jx'  # This would normally be your test public key
        
        return render_template(
            'cart/payment.html',
            order=order,
            client_secret=payment_intent.client_secret,
            payment_intent_id=payment_intent.id,
            stripe_key=stripe_key
        )
    
    except Exception as e:
        flash(f"Error setting up payment: {str(e)}", "danger")
        return redirect(url_for('cart.checkout'))


@cart_bp.route('/payment/success')
def payment_success():
    """Payment success handler."""
    payment_intent_id = request.args.get('payment_intent')
    if not payment_intent_id:
        flash("Invalid payment process. Please try again.", "danger")
        return redirect(url_for('cart.view_cart'))
    
    # Find the order with this payment intent
    order = Order.query.filter_by(payment_id=payment_intent_id).first()
    if not order:
        flash("Order not found. Please contact support.", "danger")
        return redirect(url_for('index'))
    
    # Update order status
    order.status = OrderStatus.PAID.value
    db.session.commit()
    
    # Clear the cart and session data
    cart = get_or_create_cart()
    if cart:
        cart.build_id = None
        cart.build_config = None
        cart.quantity = 0
        cart.total_price = 0
        db.session.commit()
    
    if 'current_order_id' in session:
        del session['current_order_id']
    
    if 'pc_config' in session:
        session['pc_config'] = {}
    
    return render_template('cart/payment_success.html', order=order)


@cart_bp.route('/payment/cancel')
def payment_cancel():
    """Payment canceled handler."""
    flash("Payment was canceled. Your order has not been placed.", "warning")
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        
        if order_id:
            try:
                order = Order.query.get(int(order_id))
                if order:
                    order.status = OrderStatus.PAID.value
                    db.session.commit()
            except Exception as e:
                print(f"Error updating order: {str(e)}")
    
    return jsonify({'status': 'success'})