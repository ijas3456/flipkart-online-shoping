from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pickle
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with open('flipkart_model.pkl', 'rb') as f:
    model = pickle.load(f)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    brand = db.Column(db.String(50))
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/predict', methods=['POST'])
def predict():
    feature1 = float(request.form['feature1'])
    feature2 = float(request.form['feature2'])
    prediction = model.predict([[feature1, feature2]])
    return render_template('index.html', prediction=prediction[0], products=Product.query.all())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', [])
    products = Product.query.filter(Product.id.in_(cart_items)).all()
    return render_template('cart.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    cart = session.get('cart', [])
    if product_id not in cart:
        cart.append(product_id)
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    if product_id in cart:
        cart.remove(product_id)
        session['cart'] = cart
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)