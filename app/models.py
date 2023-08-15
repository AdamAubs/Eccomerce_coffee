from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


user_product_association = db.Table('user_product_association',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
        )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    student_id = db.Column(db.Integer)
    email= db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    products = db.relationship('Product', secondary=user_product_association, backref=db.backref('users', lazy='dynamic'))
    cart_items = db.relationship('Cart', backref='user', lazy='dynamic')
    orders= db.relationship('Order', backref='user', lazy=True, primaryjoin='User.id == Order.user_id')
    orders_as_student = db.relationship('Order', backref='student', lazy=True,  primaryjoin='User.student_id == Order.student_id')
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=wavatar&s={size}'
    
    def add_to_cart(self, product, quantity=1):
        cart_item = self.cart_items.filter_by(product_id=product.id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user=self, product=product, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
    
    def remove_from_cart(self, product, quantity=1):
        cart_item = self.cart_items.filter_by(product_id=product.id).first()
        if cart_item:
            cart_item.quantity -= quantity
            if cart_item.quantity <= 0:
                db.session.delete(cart_item)
            
        db.session.commit()
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    image_url = db.Column(db.String(255))
    cart_items = db.relationship('Cart', backref='product', lazy='dynamic')
    language = db.Column(db.String(5))
    orders = db.relationship('Order', backref='product', lazy=True)
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('user.student_id'))
    status = db.Column(db.String(20))
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
