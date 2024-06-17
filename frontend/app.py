from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
from PIL import Image
import base64
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

cred = credentials.Certificate('service-account.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

def resize_image(image):
    max_size = (1024, 1024)  # Maximum dimensions for the image
    img = Image.open(image)
    img.thumbnail(max_size, Image.ANTIALIAS)
    return img

auth_service_url = 'http://auth-service:5000'
dashboard_service_url = 'http://dashboard-service:5001'
product_service_url = 'http://db-service:5002'
cart_service_url = 'http://cart-service:5003'
order_service_url= 'http://order-service:5004'

# auth_service_url = 'http://localhost:5000'
# dashboard_service_url = 'http://localhost:5001'
# product_service_url = 'http://localhost:5002'
# cart_service_url = 'http://localhost:5003'
# order_service_url= 'http://localhost:5004'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f'{auth_service_url}/login', json={'username': username,'password': password})
        if response.status_code == 200:
            session['user'] = username
            return redirect(url_for('dashboard'))
        return response.json()['message']
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        response = requests.post(f'{auth_service_url}/signup', json={'username': username, 'email':email, 'password': password})
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = session['user']
        response = requests.get(f'{dashboard_service_url}/dashboard', params={'user': user})
        if response.status_code == 200:
            products = response.json().get('products', [])
            return render_template('dashboard.html', products=products)
        else:
            return jsonify({'error': 'Failed to fetch products from dashboard service'}), 500
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    requests.post(f'{auth_service_url}/logout')
    return redirect(url_for('login'))

@app.route('/product/<product_id>')
def product_detail(product_id):
    if 'user' in session:
        user = session['user']
        try:
            response = requests.get(f'{product_service_url}/getproduct/{product_id}', params={'user': user})
            if response.status_code == 200:
                product = response.json()
                return render_template('product_detail.html', product=product)
            elif response.status_code == 404:
                return jsonify({'error': 'Product not found'}), 404
            else:
                return jsonify({'error': 'Failed to fetch product details'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return redirect(url_for('login'))

@app.route('/addtocart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user' in session:
        user = session['user']
        try:
            response = requests.post(f'{cart_service_url}/add_to_cart/{product_id}', json={'user': user}, cookies=request.cookies)
            if response.status_code == 200:
                return redirect(url_for('cart'))
            else:
                error_message = response.json().get('error', 'Unknown error')
                return render_template('error.html', error=error_message)
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return render_template('error.html', error='Internal server error. Please try again later.')
    else:
        return redirect(url_for('login'))

@app.route('/cart')
def cart():
    if 'user' in session:
        user = session['user']
        try:
            response = requests.get(f'{cart_service_url}/get_cart', cookies=request.cookies)
            if response.status_code == 200:
                cart_items = response.json()['cart_items']
                products = []
                for product_id in cart_items:
                    product_response = requests.get(f'{product_service_url}/getproduct/{product_id}')
                    if product_response.status_code == 200:
                        products.append(product_response.json())
                    else:
                        print(f'Error fetching details for product {product_id}: {product_response.status_code}')
                return render_template('cart.html', products=products)
            else:
                return render_template('cart.html', error=response.json()['error'])
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return render_template('cart.html', error='Failed to fetch cart items. Please try again later.')
    else:
        return redirect(url_for('login'))
    
@app.route('/addtoorder/<product_id>', methods=['POST'])
def add_to_order(product_id):
    if 'user' in session:
        user = session['user']
        try:
            print(f"User {user} adding product {product_id} to order")
            response = requests.post(f'{order_service_url}/add_to_order/{product_id}', json={'user': user}, cookies=request.cookies)
            if response.status_code == 200:
                return redirect(url_for('order'))
            else:
                error_message = response.json().get('error', 'Unknown error')
                return render_template('error.html', error=error_message)
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return render_template('error.html', error='Internal server error. Please try again later.')
    else:
        return redirect(url_for('login'))
    
@app.route('/order')
def order():
    if 'user' in session:
        user = session['user']
        try:
            print(f"Fetching order for user {user}")
            response = requests.get(f'{order_service_url}/get_order', cookies=request.cookies)
            if response.status_code == 200:
                order_items = response.json()['order_items']
                products = []
                for product_id in order_items:
                    product_response = requests.get(f'{product_service_url}/getproduct/{product_id}')
                    if product_response.status_code == 200:
                        products.append(product_response.json())
                    else:
                        print(f'Error fetching details for product {product_id}: {product_response.status_code}')
                return render_template('order.html', products=products)
            else:
                return render_template('order.html', error=response.json()['error'])
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return render_template('order.html', error='Failed to fetch cart items. Please try again later.')
    else:
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user' in session:
        try:
            response = requests.get(f'{auth_service_url}/status', cookies=request.cookies)
            if response.status_code == 200:
                user_data = response.json()
                username = user_data['user']
                email = user_data['email']
                password = user_data['password']  # Include password

                return render_template('profile.html', username=username, email=email, password=password)
            else:
                return render_template('error.html', error='Failed to fetch user details')
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return render_template('error.html', error='Internal server error. Please try again later.')
    else:
        return redirect(url_for('login'))

@app.route('/upload_product')
def upload_product():
    return render_template('upload_product.html')


@app.route('/upload', methods=['POST'])
def upload():
    # Fetch data from request
    product_id = request.form.get('product_id')
    product_name = request.form.get('product_name')
    price = float(request.form.get('price'))
    category = request.form.get('category')
    product_type = request.form.get('product_type')
    image = request.files['image']

    # Resize image if larger than 1MB
    if image:
        if len(image.read()) > 1024 * 1024:
            image = resize_image(image)
    
    # Convert image to base64
    image_base64 = None
    if image:
        image.seek(0)  # Reset file pointer
        image_base64 = base64.b64encode(image.read()).decode('utf-8')

    # Create product object
    product_data = {
        'product_id': product_id,
        'product_name': product_name,
        'price': price,
        'category': category,
        'product_type': product_type,
        'image': image_base64 if image_base64 else ''
    }

    try:
        # Add a new document with a generated ID into the 'products' collection
        db.collection('products').add(product_data)
        return redirect(url_for('dashboard'))
        # return jsonify({'message': 'Product uploaded successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

