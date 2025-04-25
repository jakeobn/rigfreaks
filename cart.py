import os
import json
import stripe
import uuid
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
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
    # Import current_user here to avoid circular imports
    from flask_login import current_user

    # Get user_id safely, checking if current_user is available and authenticated
    user_id = None
    is_authenticated = False
    try:
        is_authenticated = current_user.is_authenticated
        if is_authenticated:
            user_id = current_user.id
    except:
        # If there's any issue with current_user, fall back to session
        pass
    
    if is_authenticated:
        # Check if user has an existing cart
        cart = Cart.query.filter_by(user_id=user_id).first()
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
            user_id=user_id,
            session_id=None if is_authenticated else session_id
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
    
    # Define the required component categories
    required_categories = ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']
    
    # Check if all required components are selected
    config = session.get('pc_config', {})
    missing_components = [category for category in required_categories if category not in config]
    
    if missing_components:
        missing_list = ", ".join([category.replace('_', ' ').capitalize() for category in missing_components])
        flash(f"Cannot add to cart: Missing required components: {missing_list}", "warning")
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
        # Get user_id safely
        user_id = None
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                user_id = current_user.id
        except:
            pass
            
        # Create a new order
        order = Order(
            user_id=user_id,
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
    """Payment processing using Stripe hosted checkout."""
    # Get the current order from session
    order_id = session.get('current_order_id')
    if not order_id:
        flash("Invalid checkout process. Please try again.", "danger")
        return redirect(url_for('cart.view_cart'))
    
    order = Order.query.get(order_id)
    if not order:
        flash("Order not found. Please try again.", "danger")
        return redirect(url_for('cart.view_cart'))
    
    # Create a description of the order
    components_info = order.get_build_config()
    line_items = []
    
    # If there's a build configuration, create line items for the components
    if components_info:
        # Load components data
        components_data = load_component_data()
        
        # Add each component as a line item
        for category, component_id in components_info.items():
            if not component_id:
                continue
                
            # Find the component details
            for comp in components_data.get(category, []):
                if comp['id'] == component_id:
                    line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f"{category.replace('_', ' ').title()}: {comp['name']}",
                                'description': comp.get('description', ''),
                            },
                            'unit_amount': int(float(comp['price']) * 100),  # Convert to cents
                        },
                        'quantity': 1,
                    })
                    break
    else:
        # If no components, use the total amount as a single line item
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f"Custom PC Build - {order.order_number}",
                    'description': "Complete custom PC build",
                },
                'unit_amount': int(order.total_amount * 100),  # Convert to cents
            },
            'quantity': 1,
        })
    
    # Create a Stripe checkout session
    try:
        # Ensure we're using HTTPS URL
        success_url = f"https://{DOMAIN}{url_for('cart.payment_success')}?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"https://{DOMAIN}{url_for('cart.payment_cancel')}"
        
        if not success_url.startswith('https://'):
            success_url = f"https://{success_url}"
        if not cancel_url.startswith('https://'):
            cancel_url = f"https://{cancel_url}"
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=order.email,
            client_reference_id=str(order.id),
            metadata={
                'order_id': order.id,
                'order_number': order.order_number
            },
            shipping_address_collection={
                'allowed_countries': ['US', 'CA', 'GB', 'AU'],
            },
            shipping_options=[
                {
                    'shipping_rate_data': {
                        'type': 'fixed_amount',
                        'fixed_amount': {
                            'amount': 0,
                            'currency': 'usd',
                        },
                        'display_name': 'Standard Shipping',
                        'delivery_estimate': {
                            'minimum': {
                                'unit': 'business_day',
                                'value': 5,
                            },
                            'maximum': {
                                'unit': 'business_day',
                                'value': 7,
                            },
                        }
                    }
                },
                {
                    'shipping_rate_data': {
                        'type': 'fixed_amount',
                        'fixed_amount': {
                            'amount': 2500,
                            'currency': 'usd',
                        },
                        'display_name': 'Express Shipping',
                        'delivery_estimate': {
                            'minimum': {
                                'unit': 'business_day',
                                'value': 2,
                            },
                            'maximum': {
                                'unit': 'business_day',
                                'value': 3,
                            },
                        }
                    }
                },
            ],
        )
        
        # Store the checkout session ID in the order
        order.payment_id = checkout_session.id
        db.session.commit()
        
        # Redirect to Stripe checkout
        return redirect(checkout_session.url)
    
    except Exception as e:
        flash(f"Error setting up payment: {str(e)}", "danger")
        return redirect(url_for('cart.checkout'))


@cart_bp.route('/payment/success')
def payment_success():
    """Payment success handler for Stripe Checkout."""
    session_id = request.args.get('session_id')
    if not session_id:
        flash("Invalid payment process. Please try again.", "danger")
        return redirect(url_for('cart.view_cart'))
    
    try:
        # Retrieve the checkout session to verify payment
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Find the order with this session id
        order = Order.query.filter_by(payment_id=session_id).first()
        if not order:
            # If order is not found by session ID, try looking up by client reference ID
            if checkout_session.client_reference_id:
                order = Order.query.get(int(checkout_session.client_reference_id))
        
        if not order:
            flash("Order not found. Please contact support.", "danger")
            return redirect(url_for('index'))
        
        # Update order status
        order.status = OrderStatus.PAID.value
        
        # If we have shipping details from Stripe, update order
        if hasattr(checkout_session, 'shipping') and checkout_session.shipping:
            shipping = checkout_session.shipping
            if shipping.address:
                order.address_line1 = shipping.address.line1
                if hasattr(shipping.address, 'line2'):
                    order.address_line2 = shipping.address.line2
                order.city = shipping.address.city
                order.state = shipping.address.state
                order.postal_code = shipping.address.postal_code
                order.country = shipping.address.country
            
            if shipping.name:
                order.full_name = shipping.name
        
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
    
    except Exception as e:
        flash(f"Error processing payment confirmation: {str(e)}", "danger")
        return redirect(url_for('cart.view_cart'))


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
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # If we don't have a webhook secret configured, just parse the JSON payload directly
    if not webhook_secret:
        try:
            event = json.loads(payload)
        except ValueError as e:
            # Invalid payload
            return jsonify({'error': 'Invalid payload'}), 400
    else:
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            # Invalid payload
            return jsonify({'error': 'Invalid payload'}), 400
        except Exception as e:
            # Invalid signature or other error
            return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle different event types
    event_type = event['type']
    
    # Handle checkout.session.completed event
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extract order information from session
        client_ref = session.get('client_reference_id')
        session_id = session.get('id')
        
        if client_ref:
            try:
                # Find the order either by client reference or session ID
                order = Order.query.get(int(client_ref))
                
                if not order and session_id:
                    order = Order.query.filter_by(payment_id=session_id).first()
                    
                if order:
                    # Update order status
                    order.status = OrderStatus.PAID.value
                    
                    # If payment method details are available, record them
                    if 'payment_intent' in session:
                        order.payment_id = session['payment_intent']
                    
                    # Update shipping information if available
                    if 'shipping' in session and session['shipping']:
                        shipping = session['shipping']
                        if 'address' in shipping:
                            addr = shipping['address']
                            order.address_line1 = addr.get('line1', '')
                            order.address_line2 = addr.get('line2', '')
                            order.city = addr.get('city', '')
                            order.state = addr.get('state', '')
                            order.postal_code = addr.get('postal_code', '')
                            order.country = addr.get('country', '')
                            
                        if 'name' in shipping:
                            order.full_name = shipping['name']
                    
                    db.session.commit()
                    
                    # Log order completion
                    print(f"Order {order.order_number} was paid successfully via webhook")
            except Exception as e:
                print(f"Error processing checkout session webhook: {str(e)}")
    
    # Also handle the payment_intent.succeeded event for backward compatibility
    elif event_type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent.get('metadata', {}).get('order_id')
        
        if order_id:
            try:
                order = Order.query.get(int(order_id))
                if order:
                    order.status = OrderStatus.PAID.value
                    db.session.commit()
                    print(f"Order {order.order_number} was updated via payment_intent webhook")
            except Exception as e:
                print(f"Error updating order in payment_intent webhook: {str(e)}")
    
    return jsonify({'status': 'success'})