from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Float, default=0.0)

    # Products
    products = db.relationship(
        'Product',
        backref='seller',
        lazy=True
    )

    # Transport Listings
    transports = db.relationship(
        'Transport',
        backref='transporter',
        lazy=True
    )

    # Orders as Buyer
    orders = db.relationship(
        'Order',
        foreign_keys='Order.buyer_id',
        backref='buyer',
        lazy=True
    )

    # Orders as Transporter
    transport_orders = db.relationship(
        'Order',
        foreign_keys='Order.transporter_id',
        backref='assigned_transporter',
        lazy=True
    )

    # Messages
    sent_messages = db.relationship(
        'Message',
        foreign_keys='Message.sender_id',
        backref='sender',
        lazy=True
    )

    received_messages = db.relationship(
        'Message',
        foreign_keys='Message.receiver_id',
        backref='receiver',
        lazy=True
    )

    # Ratings
    ratings_given = db.relationship(
        'Rating',
        foreign_keys='Rating.rater_id',
        backref='rater',
        lazy=True
    )

    ratings_received = db.relationship(
        'Rating',
        foreign_keys='Rating.ratee_id',
        backref='ratee',
        lazy=True
    )


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    image_filename = db.Column(db.String(255))
    location = db.Column(db.String(120))
    description = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    favorites = db.relationship(
        'Favorite',
        backref='product',
        lazy=True,
        cascade='all, delete-orphan'
    )

    orders = db.relationship(
        'Order',
        backref='product',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id'),
        nullable=False
    )


class Transport(db.Model):
    __tablename__ = 'transports'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    vehicle = db.Column(db.String(120))
    capacity = db.Column(db.String(80))
    current_location = db.Column(db.String(120))
    destination = db.Column(db.String(120))
    available_date = db.Column(db.String(20))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id'),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default='Pending'
    )

    transporter_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)

    rater_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    ratee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    stars = db.Column(
        db.Integer,
        nullable=False
    )

    review = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )