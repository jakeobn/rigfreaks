from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import json
from enum import Enum
from flask_login import UserMixin

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    builds = db.relationship('Build', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_price = db.Column(db.Float, default=0.0)
    
    # Component IDs (foreign keys to components in the JSON data)
    cpu_id = db.Column(db.String(20), nullable=True)
    motherboard_id = db.Column(db.String(20), nullable=True)
    ram_id = db.Column(db.String(20), nullable=True)
    gpu_id = db.Column(db.String(20), nullable=True)
    storage_id = db.Column(db.String(20), nullable=True)
    power_supply_id = db.Column(db.String(20), nullable=True)
    case_id = db.Column(db.String(20), nullable=True)
    cooling_id = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<Build {self.name}>'

class PreBuiltConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., gaming, productivity, budget
    price = db.Column(db.Float, default=0.0)
    special_features = db.Column(db.Text, nullable=True)  # Stored as JSON
    
    def get_special_features(self):
        """Get special features as a list"""
        if self.special_features:
            return json.loads(self.special_features)
        return []
    
    # Component IDs (foreign keys to components in the JSON data)
    cpu_id = db.Column(db.String(20), nullable=True)
    motherboard_id = db.Column(db.String(20), nullable=True)
    ram_id = db.Column(db.String(20), nullable=True)
    gpu_id = db.Column(db.String(20), nullable=True)
    storage_id = db.Column(db.String(20), nullable=True)
    power_supply_id = db.Column(db.String(20), nullable=True)
    case_id = db.Column(db.String(20), nullable=True)
    cooling_id = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<PreBuiltConfig {self.name}>'

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Status tracking
    is_read = db.Column(db.Boolean, default=False)
    is_replied = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ContactMessage {self.id} - {self.email}>'

class OrderStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'
    REFUNDED = 'refunded'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('orders', lazy='dynamic'))
    
    # Order details
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default=OrderStatus.PENDING.value)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Customer information
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # Shipping information
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    
    # Payment information
    payment_method = db.Column(db.String(50), nullable=True)
    payment_id = db.Column(db.String(100), nullable=True)  # For Stripe payment_intent ID
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Build associated with this order
    build_id = db.Column(db.Integer, db.ForeignKey('build.id'), nullable=True)
    build = db.relationship('Build', backref=db.backref('orders', lazy='dynamic'))
    
    # Build configuration JSON
    build_config = db.Column(db.Text, nullable=True)  # Stored as JSON
    
    def set_build_config(self, config_dict):
        self.build_config = json.dumps(config_dict)
    
    def get_build_config(self):
        if self.build_config:
            return json.loads(self.build_config)
        return {}
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('cart', uselist=False))
    
    # Session ID for non-authenticated users
    session_id = db.Column(db.String(100), nullable=True)
    
    # Build IDs in the cart
    build_id = db.Column(db.Integer, db.ForeignKey('build.id'), nullable=True)
    build = db.relationship('Build', backref=db.backref('in_cart', uselist=False))
    
    # Build configuration for custom builds
    build_config = db.Column(db.Text, nullable=True)  # Stored as JSON
    
    # Cart item details
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_build_config(self, config_dict):
        self.build_config = json.dumps(config_dict)
    
    def get_build_config(self):
        if self.build_config:
            return json.loads(self.build_config)
        return {}
    
    def __repr__(self):
        return f'<Cart {self.id}>'