import os
import random
import string
from flask import Blueprint, session, render_template, redirect, url_for, request, flash, jsonify, abort, current_app
from flask_login import current_user, login_required
import stripe
from werkzeug.utils import secure_filename

from models import db, Cart, Order, OrderStatus, Build
from utils import load_component_data, calculate_total_price
from forms import CheckoutForm, ShippingForm, PaymentForm

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Create Blueprint
cart_bp = Blueprint('cart', __name__)

def generate_order_number():
    """Generate a random order number."""
    prefix = 'PCB'
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}-{random_part}"

def get_or_create_cart(session_id=None):
    """Get the current cart for the user or create a new one."""
    if current_user.is_authenticated:
        # Check if user has a cart
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            # Create a new cart for the user
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        return cart
    else:
        # For anonymous users, use session_id
        if not session_id:
            # Generate a new session ID if none exists
            session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
            session['cart_session_id'] = session_id
        
        # Try to find existing cart for this session
        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart:
            # Create a new cart for this session
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
        return cart

@cart_bp.route('/cart')
def view_cart():
    """Display the shopping cart."""
    # Get session ID from cookie if user is not logged in
    session_id = session.get('cart_session_id') if not current_user.is_authenticated else None
    
    # Get or create cart
    cart = get_or_create_cart(session_id)
    
    # Load component data
    components = load_component_data()
    
    # Extract build details from cart
    build_details = None
    if cart.build_id:
        # Get build from database
        build = Build.query.get(cart.build_id)
        if build:
            build_details = {
                'id': build.id,
                'name': build.name,
                'description': build.description,
                'total_price': build.total_price,
                'components': {}
            }
            # Add component details
            for category in ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']:
                component_id = getattr(build, f"{category}_id")
                if component_id and components.get(category):
                    for component in components[category]:
                        if component['id'] == component_id:
                            build_details['components'][category] = component
                            break
    elif cart.build_config:
        # Get build config from JSON
        config = cart.get_build_config()
        build_details = {
            'name': 'Custom Build',
            'description': 'Your custom PC build',
            'total_price': cart.total_price,
            'components': {}
        }
        # Add component details
        for category, component_id in config.items():
            if component_id and components.get(category):
                for component in components[category]:
                    if component['id'] == component_id:
                        build_details['components'][category] = component
                        break
    
    return render_template('cart/cart.html', cart=cart, build_details=build_details)

@cart_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add a build to the cart."""
    # Get session ID from cookie if user is not logged in
    session_id = session.get('cart_session_id') if not current_user.is_authenticated else None
    
    # Get or create cart
    cart = get_or_create_cart(session_id)
    
    # Clear existing cart items (we only support one build per cart for now)
    if cart.build_id:
        cart.build_id = None
    
    # Check if we're adding a saved build or current configuration
    build_id = request.form.get('build_id')
    
    if build_id:
        # Adding a saved build
        build = Build.query.get(build_id)
        if build:
            cart.build_id = build.id
            cart.total_price = build.total_price
            cart.quantity = 1
    else:
        # Adding current configuration from session
        if 'current_config' in session:
            config = session['current_config']
            # Load component data to calculate total price
            components = load_component_data()
            total_price = calculate_total_price(config, components)
            
            # Save to cart
            cart.set_build_config(config)
            cart.total_price = total_price
            cart.quantity = 1
        else:
            flash("No build configuration found to add to cart.", "error")
            return redirect(url_for('builder'))
    
    # Save cart changes
    db.session.commit()
    
    flash("Build added to your cart!", "success")
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    """Remove item from cart."""
    # Get session ID from cookie if user is not logged in
    session_id = session.get('cart_session_id') if not current_user.is_authenticated else None
    
    # Get cart
    cart = get_or_create_cart(session_id)
    
    # Clear cart
    cart.build_id = None
    cart.build_config = None
    cart.total_price = 0
    cart.quantity = 0
    
    # Save changes
    db.session.commit()
    
    flash("Cart has been cleared.", "success")
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/cart/update', methods=['POST'])
def update_cart():
    """Update cart items."""
    # Get session ID from cookie if user is not logged in
    session_id = session.get('cart_session_id') if not current_user.is_authenticated else None
    
    # Get cart
    cart = get_or_create_cart(session_id)
    
    # Update quantity
    quantity = request.form.get('quantity', type=int)
    if quantity and quantity > 0:
        cart.quantity = quantity
        db.session.commit()
        flash("Cart updated successfully.", "success")
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout process."""
    # Get session ID from cookie if user is not logged in
    session_id = session.get('cart_session_id') if not current_user.is_authenticated else None
    
    # Get cart
    cart = get_or_create_cart(session_id)
    
    # Check if cart is empty
    if cart.total_price <= 0:
        flash("Your cart is empty. Please add a build before checking out.", "error")
        return redirect(url_for('cart.view_cart'))
    
    # Load component data
    components = load_component_data()
    
    # Extract build details from cart
    build_details = None
    if cart.build_id:
        # Get build from database
        build = Build.query.get(cart.build_id)
        if build:
            build_details = {
                'id': build.id,
                'name': build.name,
                'description': build.description,
                'total_price': build.total_price,
                'components': {}
            }
            # Add component details
            for category in ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']:
                component_id = getattr(build, f"{category}_id")
                if component_id and components.get(category):
                    for component in components[category]:
                        if component['id'] == component_id:
                            build_details['components'][category] = component
                            break
    elif cart.build_config:
        # Get build config from JSON
        config = cart.get_build_config()
        build_details = {
            'name': 'Custom Build',
            'description': 'Your custom PC build',
            'total_price': cart.total_price,
            'components': {}
        }
        # Add component details
        for category, component_id in config.items():
            if component_id and components.get(category):
                for component in components[category]:
                    if component['id'] == component_id:
                        build_details['components'][category] = component
                        break
    
    # Initialize form
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
        
        # Copy build details to order
        if cart.build_id:
            order.build_id = cart.build_id
        elif cart.build_config:
            order.set_build_config(cart.get_build_config())
        
        # Save order to database
        db.session.add(order)
        db.session.commit()
        
        # Store order ID in session for payment step
        session['order_id'] = order.id
        
        # Redirect to payment page
        return redirect(url_for('cart.payment'))
    
    # Pre-fill user information if logged in
    if current_user.is_authenticated and not form.is_submitted():
        form.full_name.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('cart/checkout.html', form=form, cart=cart, build_details=build_details)

@cart_bp.route('/payment', methods=['GET', 'POST'])
def payment():
    """Payment processing."""
    # Check if we have an order in progress
    order_id = session.get('order_id')
    if not order_id:
        flash("Please complete checkout before proceeding to payment.", "error")
        return redirect(url_for('cart.checkout'))
    
    # Get the order
    order = Order.query.get(order_id)
    if not order:
        flash("Order not found. Please try again.", "error")
        return redirect(url_for('cart.checkout'))
    
    # Create a payment intent with Stripe
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Stripe requires amount in cents
            currency='usd',
            metadata={
                'order_number': order.order_number,
                'customer_email': order.email
            }
        )
        
        # Store the client secret for the frontend
        client_secret = intent.client_secret
        
        return render_template(
            'cart/payment.html',
            order=order,
            client_secret=client_secret,
            stripe_key=os.environ.get('STRIPE_PUBLISHABLE_KEY', ''),
            payment_intent_id=intent.id
        )
    except Exception as e:
        flash(f"An error occurred while setting up payment: {str(e)}", "error")
        return redirect(url_for('cart.checkout'))

@cart_bp.route('/payment/success')
def payment_success():
    """Payment success handler."""
    # Get order from session
    order_id = session.get('order_id')
    if not order_id:
        return redirect(url_for('index'))
    
    # Get order details
    order = Order.query.get(order_id)
    if not order:
        return redirect(url_for('index'))
    
    # Update order status
    order.status = OrderStatus.PAID.value
    
    # Get payment intent ID from query string
    payment_intent_id = request.args.get('payment_intent')
    if payment_intent_id:
        order.payment_id = payment_intent_id
        order.payment_method = 'stripe'
    
    # Save changes
    db.session.commit()
    
    # Clear cart and session data
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            cart.build_id = None
            cart.build_config = None
            cart.total_price = 0
            cart.quantity = 0
            db.session.commit()
    
    # Clear session
    if 'cart_session_id' in session:
        del session['cart_session_id']
    if 'order_id' in session:
        del session['order_id']
    
    return render_template('cart/payment_success.html', order=order)

@cart_bp.route('/payment/cancel')
def payment_cancel():
    """Payment canceled handler."""
    # Get order from session
    order_id = session.get('order_id')
    if order_id:
        # Get order details
        order = Order.query.get(order_id)
        if order:
            # Update order status
            order.status = OrderStatus.CANCELED.value
            db.session.commit()
    
    flash("Your payment was canceled. Please try again when you're ready.", "warning")
    return redirect(url_for('cart.checkout'))

@cart_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': str(e)}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        # Find order by payment ID
        order = Order.query.filter_by(payment_id=payment_intent.id).first()
        if order:
            order.status = OrderStatus.PAID.value
            db.session.commit()
    
    return jsonify({'status': 'success'}), 200