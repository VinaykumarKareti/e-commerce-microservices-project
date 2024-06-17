

from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Ensure this matches with frontend secret key

# In-memory storage for cart details
cart_details = {}

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user' in session:
        user = session['user']
        if user not in cart_details:
            cart_details[user] = []
        cart_details[user].append(product_id)
        return jsonify({'message': 'Product added to cart successfully'}), 200
    else:
        return jsonify({'error': 'User not logged in'}), 403

@app.route('/get_cart', methods=['GET'])
def get_cart():
    if 'user' in session:
        user = session['user']
        if user in cart_details:
            return jsonify({'cart_items': cart_details[user]}), 200
        else:
            return jsonify({'cart_items': []}), 200
    else:
        return jsonify({'error': 'User not logged in'}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
