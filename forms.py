from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, HiddenField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one or login.')

class SaveBuildForm(FlaskForm):
    name = StringField('Build Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    is_public = BooleanField('Make this build public')
    submit = SubmitField('Save Build')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=3, max=200)])
    category = SelectField('Category', choices=[
        ('support', 'Technical Support'),
        ('sales', 'Sales Inquiry'),
        ('feedback', 'Feedback'),
        ('other', 'Other')
    ])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Send Message')

class CheckoutForm(FlaskForm):
    # Customer Information
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(min=10, max=20)])
    
    # Shipping Information
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(min=5, max=100)])
    address_line2 = StringField('Address Line 2 (Optional)', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=50)])
    state = StringField('State/Province', validators=[DataRequired(), Length(min=2, max=50)])
    postal_code = StringField('ZIP/Postal Code', validators=[DataRequired(), Length(min=5, max=20)])
    country = SelectField('Country', choices=[
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('UK', 'United Kingdom'),
        ('AU', 'Australia'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('JP', 'Japan'),
        ('OTHER', 'Other')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Continue to Payment')

class ShippingForm(FlaskForm):
    shipping_method = SelectField('Shipping Method', choices=[
        ('standard', 'Standard Shipping (5-7 business days) - Free'),
        ('express', 'Express Shipping (2-3 business days) - $25'),
        ('overnight', 'Overnight Shipping (1 business day) - $50')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Continue to Payment')

class PaymentForm(FlaskForm):
    payment_method = SelectField('Payment Method', choices=[
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal')
    ], validators=[DataRequired()])
    
    # These fields are just for display - the actual payment processing will be done with Stripe
    card_name = StringField('Name on Card', validators=[DataRequired(), Length(min=3, max=100)])
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    card_expiry = StringField('Expiration (MM/YY)', validators=[DataRequired(), Length(min=5, max=5)])
    card_cvc = StringField('CVC', validators=[DataRequired(), Length(min=3, max=4)])
    
    submit = SubmitField('Place Order')