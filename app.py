from flask import Flask, request, jsonify, session, send_from_directory
from models import db, User, Product, Favorite, Transport, Order, Rating, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'  # Replace with a secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zabo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db.init_app(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return wrapped

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','gif'}

@app.route('/')
def index():
    # Serve the main HTML page
    return send_from_directory('static', 'zabo.html')

# User registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username'); password = data.get('password'); role = data.get('role')
    if not username or not password or not role:
        return jsonify({'error': 'Missing required fields'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if data.get('email') and User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already registered'}), 400
    hashed = generate_password_hash(password)  # uses PBKDF2 (Werkzeug)
    user = User(username=username, email=data.get('email'), password=hashed, role=role)
    db.session.add(user); db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# User login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    user = User.query.filter_by(username=data.get('username')).first()
    if user and check_password_hash(user.password, data.get('password')):
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# User logout
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

# Products endpoints
@app.route('/api/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'price': p.price,
            'quantity': p.quantity,
            'image': p.image_filename,
            'location': p.location,
            'description': p.description,
            'seller': p.seller.username,
            'created_at': p.created_at.isoformat()
        })
    return jsonify(result), 200

@app.route('/api/products', methods=['POST'])
@login_required
def create_product():
    name = request.form.get('name')
    price = request.form.get('price', type=float)
    quantity = request.form.get('quantity', type=int)
    if not name or price is None or quantity is None:
        return jsonify({'error': 'Missing required fields'}), 400
    filename = None
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    product = Product(
        name=name,
        category=request.form.get('category'),
        price=price,
        quantity=quantity,
        location=request.form.get('location'),
        description=request.form.get('description'),
        image_filename=filename,
        seller_id=session['user_id']
    )
    db.session.add(product); db.session.commit()
    return jsonify({'message': 'Product created', 'id': product.id}), 201

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'quantity': p.quantity,
        'image': p.image_filename,
        'location': p.location,
        'description': p.description,
        'seller': p.seller.username,
        'created_at': p.created_at.isoformat()
    }), 200

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    p = Product.query.get_or_404(product_id)
    # Only seller or admin can update
    if p.seller_id != session['user_id'] and session.get('role') != 'Admin':
        return jsonify({'error': 'Permission denied'}), 403
    data = request.json or {}
    for field in ['name','category','price','quantity','location','description']:
        if field in data:
            setattr(p, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Product updated'}), 200

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    if p.seller_id != session['user_id'] and session.get('role') != 'Admin':
        return jsonify({'error': 'Permission denied'}), 403
    db.session.delete(p); db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

# Favorites (saved listings)
@app.route('/api/favorites', methods=['GET'])
@login_required
def list_favorites():
    favs = Favorite.query.filter_by(user_id=session['user_id']).all()
    result = [{'product_id': f.product_id, 'product_name': f.product.name} for f in favs]
    return jsonify(result), 200

@app.route('/api/favorites', methods=['POST'])
@login_required
def add_favorite():
    data = request.json or {}
    pid = data.get('product_id')
    if not pid or not Product.query.get(pid):
        return jsonify({'error': 'Invalid product_id'}), 400
    fav = Favorite(user_id=session['user_id'], product_id=pid)
    db.session.add(fav); db.session.commit()
    return jsonify({'message': 'Added to favorites'}), 201

@app.route('/api/favorites', methods=['DELETE'])
@login_required
def remove_favorite():
    data = request.json or {}
    pid = data.get('product_id')
    fav = Favorite.query.filter_by(user_id=session['user_id'], product_id=pid).first()
    if not fav:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(fav); db.session.commit()
    return jsonify({'message': 'Removed from favorites'}), 200

# Transport listings
@app.route('/api/transports', methods=['GET'])
def list_transports():
    trans = Transport.query.all()
    result = []
    for t in trans:
        result.append({
            'id': t.id,
            'vehicle': t.vehicle,
            'capacity': t.capacity,
            'current_location': t.current_location,
            'destination': t.destination,
            'available_date': t.available_date,
            'user': t.transporter.username
        })
    return jsonify(result), 200

@app.route('/api/transports', methods=['POST'])
@login_required
def create_transport():
    data = request.json or {}
    vehicle = data.get('vehicle'); current = data.get('current_location'); destination = data.get('destination')
    if not vehicle or not current or not destination:
        return jsonify({'error': 'Missing fields'}), 400
    transport = Transport(
        user_id=session['user_id'],
        vehicle=vehicle,
        capacity=data.get('capacity'),
        current_location=current,
        destination=destination,
        available_date=data.get('available_date')
    )
    db.session.add(transport); db.session.commit()
    return jsonify({'message': 'Transport listing created', 'id': transport.id}), 201

# Orders
@app.route('/api/orders', methods=['GET'])
@login_required
def list_orders():
    orders = Order.query.filter(
        (Order.buyer_id == session['user_id']) |
        (Order.transporter_id == session['user_id'])
    ).all()
    result = []
    for o in orders:
        result.append({
            'id': o.id,
            'product': o.product.name,
            'buyer': o.buyer.username,
            'quantity': o.quantity,
            'status': o.status,
            'transporter': (User.query.get(o.transporter_id).username if o.transporter_id else None)
        })
    return jsonify(result), 200

@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    data = request.json or {}
    product_id = data.get('product_id'); qty = data.get('quantity')
    if not product_id or not qty:
        return jsonify({'error': 'Missing fields'}), 400
    product = Product.query.get(product_id)
    if not product or product.quantity < qty:
        return jsonify({'error': 'Invalid product or insufficient stock'}), 400
    order = Order(buyer_id=session['user_id'], product_id=product_id, quantity=qty, status='Pending')
    db.session.add(order)
    product.quantity -= qty  # reduce stock
    db.session.commit()
    return jsonify({'message': 'Order placed', 'order_id': order.id}), 201

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    o = Order.query.get_or_404(order_id)
    if o.buyer_id != session['user_id'] and o.transporter_id != session['user_id'] and session.get('role') != 'Admin':
        return jsonify({'error': 'Permission denied'}), 403
    return jsonify({
        'id': o.id,
        'product': o.product.name,
        'buyer': o.buyer.username,
        'quantity': o.quantity,
        'status': o.status,
        'transporter': (User.query.get(o.transporter_id).username if o.transporter_id else None),
        'created_at': o.created_at.isoformat()
    }), 200

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    o = Order.query.get_or_404(order_id)
    data = request.json or {}
    # Only admin, transporter, or the seller of the product can update
    if session.get('role') not in ['Admin','Transporter'] and o.product.seller_id != session['user_id']:
        return jsonify({'error': 'Permission denied'}), 403
    if 'status' in data:
        o.status = data['status']
    if 'transporter_id' in data:
        o.transporter_id = data['transporter_id']
    db.session.commit()
    return jsonify({'message': 'Order updated'}), 200

# Ratings
@app.route('/api/ratings', methods=['GET'])
def list_ratings():
    ratings = Rating.query.all()
    result = []
    for r in ratings:
        result.append({
            'id': r.id,
            'rater': r.rater.username,
            'ratee': r.ratee.username,
            'stars': r.stars,
            'review': r.review,
            'created_at': r.created_at.isoformat()
        })
    return jsonify(result), 200

@app.route('/api/ratings', methods=['POST'])
@login_required
def create_rating():
    data = request.json or {}
    ratee_id = data.get('ratee_id'); stars = data.get('stars')
    if not ratee_id or not stars:
        return jsonify({'error': 'Missing fields'}), 400
    rating = Rating(rater_id=session['user_id'], ratee_id=ratee_id,
                    stars=stars, review=data.get('review'))
    db.session.add(rating); db.session.commit()
    return jsonify({'message': 'Rating submitted'}), 201

# Messages
@app.route('/api/messages', methods=['GET'])
@login_required
def list_messages():
    messages = Message.query.filter(
        (Message.sender_id == session['user_id']) |
        (Message.receiver_id == session['user_id'])
    ).all()
    result = []
    for m in messages:
        result.append({
            'id': m.id,
            'sender': m.sender.username,
            'receiver': m.receiver.username,
            'content': m.content,
            'timestamp': m.timestamp.isoformat()
        })
    return jsonify(result), 200

@app.route('/api/messages', methods=['POST'])
@login_required
def send_message():
    data = request.json or {}
    receiver_id = data.get('receiver_id'); content = data.get('content')
    if not receiver_id or not content:
        return jsonify({'error': 'Missing fields'}), 400
    msg = Message(sender_id=session['user_id'], receiver_id=receiver_id, content=content)
    db.session.add(msg); db.session.commit()
    return jsonify({'message': 'Message sent'}), 201
@app.route('/api/current-user')
def current_user():
    if 'user_id' not in session:
        return jsonify({
            'logged_in': False
        })

    user = User.query.get(session['user_id'])

    return jsonify({
        'logged_in': True,
        'username': user.username,
        'role': user.role
    })

# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
@login_required
def admin_list_users():
    if session.get('role') != 'Admin':
        return jsonify({'error': 'Permission denied'}), 403
    users = User.query.all()
    result = [{'id': u.id, 'username': u.username, 'email': u.email, 'role': u.role} for u in users]
    return jsonify(result), 200

@app.route('/api/admin/products', methods=['GET'])
@login_required
def admin_list_products():
    if session.get('role') != 'Admin':
        return jsonify({'error': 'Permission denied'}), 403
    prods = Product.query.all()
    result = [{'id': p.id, 'name': p.name, 'seller': p.seller.username} for p in prods]
    return jsonify(result), 200

@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@login_required
def admin_delete_product(product_id):
    if session.get('role') != 'Admin':
        return jsonify({'error': 'Permission denied'}), 403
    p = Product.query.get_or_404(product_id)
    db.session.delete(p); db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

# Create all database tables automatically
with app.app_context():
    db.create_all()

# Optional CLI command
@app.cli.command('init-db')
def init_db():
    with app.app_context():
        db.create_all()
    print("Initialized database.")

if __name__ == '__main__':
    app.run(debug=True)