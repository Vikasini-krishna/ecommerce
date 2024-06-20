from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from random import choices
import string
import bcrypt  # Make sure flask_bcrypt is installed

# Import SECRET_KEY from config.py
from config import SECRET_KEY

# Create Flask app instance
app = Flask(__name__)
app.secret_key = SECRET_KEY

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce']
products_collection = db['products']
subscription_collection = db['sub']
payment_collection = db['payment']
users_collection = db['login']

# Function to generate unique 4-character alphanumeric ID
def generate_unique_id():
    while True:
        unique_id = ''.join(choices(string.ascii_uppercase + string.digits, k=4))
        if not products_collection.find_one({"_id": unique_id}):
            return unique_id

# Sample data insertion (run this once)
def insert_sample_data():
    sample_products = [
        {"_id": generate_unique_id(), "name": "Product 1", "price": 29.99, "description": "Description for product 1",
         "sizes": ["Small", "Medium", "Large"], "colors": ["Red", "Blue", "Green"],
         "image": "https://images.pexels.com/photos/904117/pexels-photo-904117.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"},
        {"_id": generate_unique_id(), "name": "Product 2", "price": 39.99, "description": "Description for product 2",
         "sizes": ["Small", "Large"], "colors": ["Black", "White"],
         "image": "https://example.com/path/to/image2.jpg"},
        {"_id": generate_unique_id(), "name": "Product 3", "price": 19.99, "description": "Description for product 3",
         "sizes": ["Medium", "Large"], "colors": ["Yellow", "Purple"],
         "image": "https://example.com/path/to/image3.jpg"},
        {"_id": generate_unique_id(), "name": "Product 4", "price": 49.99, "description": "Description for product 4",
         "sizes": ["Small", "Medium"], "colors": ["Pink", "Orange"],
         "image": "https://example.com/path/to/image4.jpg"},
        {"_id": generate_unique_id(), "name": "Product 5", "price": 59.99, "description": "Description for product 5",
         "sizes": ["Large"], "colors": ["Blue", "White"],
         "image": "https://example.com/path/to/image5.jpg"},
        {"_id": generate_unique_id(), "name": "Product 6", "price": 79.99, "description": "Description for product 6",
         "sizes": ["Small", "Large"], "colors": ["Green", "Black"],
         "image": "https://example.com/path/to/image6.jpg"},
        {"_id": generate_unique_id(), "name": "Product 7", "price": 39.99, "description": "Description for product 7",
         "sizes": ["Medium", "Large"], "colors": ["Red", "Yellow"],
         "image": "https://example.com/path/to/image7.jpg"},
        {"_id": generate_unique_id(), "name": "Product 8", "price": 69.99, "description": "Description for product 8",
         "sizes": ["Small", "Medium", "Large"], "colors": ["Purple", "Gray"],
         "image": "https://example.com/path/to/image8.jpg"},
        {"_id": generate_unique_id(), "name": "Product 9", "price": 89.99, "description": "Description for product 9",
         "sizes": ["Medium"], "colors": ["Brown", "Beige"],
         "image": "https://example.com/path/to/image9.jpg"},
        {"_id": generate_unique_id(), "name": "Product 10", "price": 99.99, "description": "Description for product 10",
         "sizes": ["Large"], "colors": ["Orange", "Silver"],
         "image": "https://example.com/path/to/image10.jpg"},
    ]
    products_collection.insert_many(sample_products)


# Uncomment the following line to insert sample data
insert_sample_data()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']
        
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        users_collection.insert_one({'username': username, 'password': hashed_password, 'email': email})

        return redirect(url_for('index'))  
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        user = users_collection.find_one({'email': email})

        if user and bcrypt.checkpw(password, user['password']):
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('index'))

        error = 'Invalid email or password. Please try again.'
        return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/products')
def products():
    products = list(products_collection.find())
    return render_template('products.html', products=products)

@app.route('/product/<string:product_id>')
def product_details(product_id):
    product = products_collection.find_one({"_id": product_id})
    return render_template('product_details.html', product=product)

@app.route('/subscribe', methods=['POST'])
def subscribe_email():
    if request.method == 'POST':
        email = request.form['email']
        if subscription_collection.find_one({'email': email}):
            return "You are already subscribed."
        else:
            subscription_collection.insert_one({'email': email})
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        card_number = request.form['card-number']
        card_holder = request.form['card-holder']
        expiration_date = request.form['expiration-date']
        save_card = request.form.get('save-info')  

        # Assuming user is logged in and email is stored in session
        email = session.get('email')

        if save_card:
            # If 'save-card' checkbox is checked, insert payment data into collection
            payment_data = {
                "card_number": card_number,
                "card_holder": card_holder,
                "expiration_date": expiration_date,
                "email": email
            }
            payment_collection.insert_one(payment_data)

        return redirect(url_for('home'))  # Redirect to home page after successful payment

    return render_template('payment.html')

if __name__ == '__main__':
    app.run(debug=True)
