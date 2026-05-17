from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///liminshop.db'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_seller = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    name = request.args.get('name')
    
    query = Product.query
    
    if category:
        query = query.filter_by(category=category)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    
    products = query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'category': p.category,
        'description': p.description,
        'seller_id': p.seller_id
    } for p in products])

@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    data = request.json
    buyer_id = data.get('buyer_id')
    seller_id = data.get('seller_id')
    product_id = data.get('product_id')
    
    chat = Chat.query.filter_by(
        buyer_id=buyer_id,
        seller_id=seller_id,
        product_id=product_id,
        is_deleted=False
    ).first()
    
    if not chat:
        chat = Chat(buyer_id=buyer_id, seller_id=seller_id, product_id=product_id)
        db.session.add(chat)
        db.session.commit()
    
    return jsonify({'chat_id': chat.id})

@app.route('/api/chat/<int:chat_id>/messages', methods=['GET'])
def get_messages(chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).all()
    return jsonify([{
        'id': m.id,
        'sender_id': m.sender_id,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    } for m in messages])

@app.route('/api/chat/<int:chat_id>/message', methods=['POST'])
def send_message(chat_id):
    data = request.json
    sender_id = data.get('sender_id')
    content = data.get('content')
    
    message = Message(chat_id=chat_id, sender_id=sender_id, content=content)
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'id': message.id, 'created_at': message.created_at.isoformat()})

@app.route('/api/chat/<int:chat_id>/delete', methods=['POST'])
def delete_chat(chat_id):
    chat = Chat.query.get(chat_id)
    if chat:
        chat.is_deleted = True
        db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
