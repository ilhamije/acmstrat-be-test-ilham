import json
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Load customers from JSON file
def load_customers():
    with open('data/customers.json', 'r') as f:
        return json.load(f)

@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = load_customers()
    
    # Pagination
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    
    start = (page - 1) * limit
    end = start + limit
    
    paginated_customers = customers[start:end]
    
    return jsonify({
        'data': paginated_customers,
        'total': len(customers),
        'page': page,
        'limit': limit,
        'total_pages': (len(customers) + limit - 1) // limit
    })

@app.route('/api/customers/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customers = load_customers()
    # Search by customer_id (String)
    customer = next((c for c in customers if c['customer_id'] == customer_id), None)
    
    if customer is None:
        return jsonify({'error': 'Customer not found'}), 404
        
    return jsonify(customer)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
