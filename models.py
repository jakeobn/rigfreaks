from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
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