# dashboard_service/app.py
import os
from flask import Flask, request, render_template, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import Image
import base64

app = Flask(__name__)
cred = credentials.Certificate('service-account.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/dashboard', methods=['GET'])
def dashboard():
    user = request.args.get('user')
    # return jsonify({'message': f'Welcome to your dashboard, {user}'})
    try:
        # Retrieve all documents from the 'products' collection
        products_ref = db.collection('products')
        products = products_ref.get()

        # Prepare products data to pass to template
        products_list = []
        for product in products:
            products_list.append(product.to_dict())

        return jsonify({'products': products_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

