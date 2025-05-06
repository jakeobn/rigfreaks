# Architecture Overview - RigFreaks PC Builder Application

## 1. Overview

RigFreaks is a web application for building and purchasing custom PC configurations. It provides a platform for users to:

- Build custom PC configurations with compatible components
- Browse pre-built PC configurations
- Save and share PC builds
- Purchase configured PC builds
- Contact customer support
- Access documentation and information about PC building

The application follows a monolithic architecture built on Flask with a PostgreSQL database, focusing on providing a responsive user experience with server-side rendering. It incorporates several key modules for handling user authentication, PC configuration building, shopping cart functionality, and admin features.

## 2. System Architecture

### 2.1 High-Level Architecture

The application follows a classic three-tier architecture:

- **Presentation Layer**: Flask templates with Jinja2 templating engine
- **Application Layer**: Flask application with blueprints for modular organization
- **Data Layer**: PostgreSQL database with SQLAlchemy ORM

```
┌─────────────────┐
│   Client        │
│  (Web Browser)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask App     │──┐
│  (Web Server)   │  │
└────────┬────────┘  │
         │           │
         ▼           │
┌─────────────────┐  │
│   Data Models   │  │
│   (SQLAlchemy)  │  │
└────────┬────────┘  │
         │           │
         ▼           │
┌─────────────────┐  │
│   PostgreSQL    │  │
│   Database      │  │
└─────────────────┘  │
         ▲           │
         │           │
┌────────┴────────┐  │
│ External APIs   │◄─┘
│ (Stripe, etc.)  │
└─────────────────┘
```

### 2.2 Component Organization

The application uses Flask's blueprint feature to organize code into logical modules:

- **auth_bp**: User authentication and account management
- **builds_bp**: PC configuration building and management
- **admin_bp**: Admin panel and administrative functions
- **cart_bp**: Shopping cart and checkout process

## 3. Key Components

### 3.1 Frontend Architecture

The frontend is built using server-side rendering with the following technologies:

- **Templating**: Jinja2 templates (contained in `/templates` directory)
- **CSS Framework**: Bootstrap with custom CSS overrides
- **JavaScript**: Client-side enhancements for interactive features
- **Icons**: Font Awesome for iconography

Key frontend design decisions:

- Dark theme UI optimized for displaying PC components
- Responsive design for both desktop and mobile users
- Progressive enhancement for core functionality to work without JavaScript
- AOS (Animate On Scroll) library for smooth animations and visual feedback

### 3.2 Backend Architecture

The backend is built on Flask with a modular structure:

- **app.py**: Main application entry point and configuration
- **models.py**: Database models using SQLAlchemy ORM
- **utils.py**: Utility functions for component compatibility checking and pricing
- **blueprints**: Modular code organization (auth.py, builds.py, cart.py, admin.py)

Key backend design decisions:

- Blueprints for code organization and separation of concerns
- SQLAlchemy ORM for database interaction
- Session-based state management for PC configuration building
- Custom decorators for authentication and authorization

### 3.3 Database Schema

The application uses PostgreSQL with SQLAlchemy ORM. Key models include:

- **User**: User accounts and authentication information
- **Build**: Custom PC configurations created by users
- **PreBuiltConfig**: Pre-configured PC builds offered by the shop
- **Order**: Customer orders with associated shipping and payment information
- **Cart**: Shopping cart implementation for temporary storage of builds before purchase
- **ContactMessage**: Customer support inquiries and messages

Database connection is optimized with the following settings:

- Connection pooling with recycling (pool_recycle: 300 seconds)
- Connection verification with pre-ping
- Pool size limiting (10 with 15 overflow)
- Timeouts to prevent hanging connections

### 3.4 Authentication and Authorization

Authentication is implemented using:

- **Flask-Login**: For session management and user authentication
- **Werkzeug security**: For password hashing and verification
- **Custom decorators**: For role-based access control (e.g., admin_required)

Key authentication design decisions:

- Session-based authentication with secure cookies
- Password hashing for secure storage
- Role-based access control for admin functionality
- Login_required decorator for protected routes

### 3.5 PC Builder Component

The PC Builder component is a core feature that includes:

- **Component compatibility checking**: Ensures selected components work together
- **Component data management**: JSON-based component catalog
- **Pricing calculation**: Dynamic pricing based on component selection
- **Configuration saving**: Allows users to save and share configurations

Key design features:

- Component data loaded from JSON files (static/data/components.json)
- Compatibility rules loaded from JSON files (static/data/compatibility_rules.json)
- Caching mechanism for component data to improve performance
- Step-by-step builder interface for guiding users through the configuration process

## 4. Data Flow

### 4.1 PC Building Flow

1. User selects PC components through the builder interface
2. Application validates component compatibility in real-time
3. Pricing is calculated dynamically based on component selection
4. Configuration is stored in session during the building process
5. User can save the configuration to their account or proceed to purchase

### 4.2 Shopping Cart Flow

1. User adds a configuration to their cart
2. Cart is associated with user account (if logged in) or session (if anonymous)
3. User proceeds to checkout process
4. Shipping information and payment details are collected
5. Stripe integration processes payment
6. Order confirmation is generated and sent to user

### 4.3 Admin Flow

1. Admin logs in with appropriate credentials
2. Admin has access to specialized views for user management and message handling
3. Admin can view and respond to contact messages
4. Admin-specific features are protected by custom decorators

## 5. External Dependencies

### 5.1 Third-Party Services

- **Stripe**: Payment processing integration
- **Gunicorn**: WSGI HTTP server for production deployment
- **Trafilatura**: Used for web scraping in analysis functions

### 5.2 External Libraries

- **Flask**: Web framework for the application
- **SQLAlchemy**: Object-relational mapper for database interaction
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and validation
- **Werkzeug**: Utilities for web applications including security features
- **Bootstrap**: Frontend CSS framework
- **Font Awesome**: Icon library

## 6. Deployment Strategy

### 6.1 Deployment Configuration

The application is configured for deployment on a Replit environment with auto-scaling capabilities:

- **WSGI Server**: Gunicorn for handling HTTP requests
- **Database**: PostgreSQL 16
- **Python Runtime**: Python 3.11
- **Port Configuration**: Port 5000 internally mapped to port 80 externally

### 6.2 Scaling Strategy

- **Autoscaling**: The deployment target is set to "autoscale"
- **Connection pooling**: Database connections are pooled for better resource utilization
- **ProxyFix middleware**: Configured to handle proper HTTP headers for proxied requests

### 6.3 Environment Configuration

- **Environment Variables**: Configuration through environment variables (e.g., DATABASE_URL, SESSION_SECRET)
- **Development Mode**: Debug mode enabled in development but should be disabled in production

## 7. Future Considerations

- **API Development**: Potential for adding a RESTful API for headless interaction
- **Performance Optimization**: Caching strategies for component data and benchmark results
- **Mobile App Integration**: Possible companion app for mobile access
- **Advanced Analytics**: Integration with analytics platforms for user behavior tracking

## 8. Security Considerations

- **CSRF Protection**: Implemented via Flask-WTF
- **Password Security**: Passwords are hashed using Werkzeug security
- **Session Security**: Secret key configuration for secure session cookies
- **Input Validation**: Form validation to prevent injection attacks
- **Admin Access Control**: Role-based access control for administrative functions