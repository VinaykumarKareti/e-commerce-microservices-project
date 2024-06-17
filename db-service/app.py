# product_service/app.py
from flask import Flask, request, render_template, jsonify
import firebase_admin
from firebase_admin import credentials, firestore


app = Flask(__name__)
cred = credentials.Certificate('service-account.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
# Route to fetch product details by product_id
@app.route('/getproduct/<product_id>')
def get_product(product_id):
    try:
        # Query Firestore to find the document with the matching product_id
        products_ref = db.collection('products')
        query = products_ref.where('product_id', '==', product_id).limit(1).get()

        if query:
            product = query[0].to_dict()
            return jsonify(product), 200
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

