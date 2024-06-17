from flask import Flask, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Ensure this matches with frontend secret key

# In-memory storage for order details
order_details = {}

@app.route('/add_to_order/<product_id>', methods=['POST'])
def add_to_order(product_id):
    if 'user' in session:
        user = session['user']
        print(f"User {user} adding product {product_id} to order")
        if user not in order_details:
            order_details[user] = []
        order_details[user].append(product_id)
        return jsonify({'message': 'Product added to order successfully'}), 200
    else:
        print("User not logged in")
        return jsonify({'error': 'User not logged in'}), 403

@app.route('/get_order', methods=['GET'])
def get_order():
    if 'user' in session:
        user = session['user']
        print(f"Fetching order for user {user}")
        if user in order_details:
            return jsonify({'order_items': order_details[user]}), 200
        else:
            return jsonify({'order_items': []}), 200
    else:
        print("User not logged in")
        return jsonify({'error': 'User not logged in'}), 403

@app.route('/remove_from_order/<product_id>', methods=['POST'])
def remove_from_order(product_id):
    if 'user' in session:
        user = session['user']
        if user in order_details and product_id in order_details[user]:
            order_details[user].remove(product_id)
        return redirect(url_for('order'))
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
