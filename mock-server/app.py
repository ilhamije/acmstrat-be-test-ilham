import json
import logging
from flask import Flask, jsonify, request, abort

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mock-server")

app = Flask(__name__)

# Load customers from JSON file
def load_customers():
    try:
        with open('data/customers.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load customers data: {str(e)}")
        return []

@app.route('/api/customers', methods=['GET'])
def get_customers():
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    
    logger.info(f"Fetching customers - Page: {page}, Limit: {limit}")
    
    customers = load_customers()
    
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
    logger.info(f"Fetching customer: {customer_id}")
    customers = load_customers()
    customer = next((c for c in customers if c['customer_id'] == customer_id), None)
    
    if customer is None:
        logger.warning(f"Customer not found: {customer_id}")
        return jsonify({'error': 'Customer not found'}), 404
        
    return jsonify(customer)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
