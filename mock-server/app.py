from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Load customer data
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/customers', methods=['GET'])
def get_customers():
    data = load_data()
    
    # Pagination
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    if page < 1 or limit < 1:
        return jsonify({"error": "Page and limit must be greater than 0"}), 400
        
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_data = data[start_idx:end_idx]
    
    return jsonify({
        "data": paginated_data,
        "total": len(data),
        "page": page,
        "limit": limit
    }), 200

@app.route('/api/customers/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    data = load_data()
    
    customer = next((c for c in data if c['customer_id'] == customer_id), None)
    
    if customer:
        return jsonify(customer), 200
    else:
        return jsonify({"error": "Customer not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
