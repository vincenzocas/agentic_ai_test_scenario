from flask import Flask, jsonify, request
from datetime import datetime
import uuid

app = Flask(__name__)

# Mock CRM database
customers = {
    "cust_001": {
        "id": "cust_001",
        "name": "Acme Corporation",
        "email": "contact@acme.com",
        "phone": "+1-555-0123",
        "account_number": "ACC-789123456",
        "status": "active",
        "credit_limit": 50000.00,
        "current_balance": 12500.00,
        "created_date": "2024-01-15",
        "last_payment_date": None,
        "last_payment_amount": 0.00
    },
    "cust_002": {
        "id": "cust_002",
        "name": "Tech Solutions Ltd",
        "email": "billing@techsolutions.com",
        "phone": "+1-555-0456",
        "account_number": "ACC-456789123",
        "status": "active",
        "credit_limit": 25000.00,
        "current_balance": 8750.00,
        "created_date": "2024-02-20",
        "last_payment_date": None,
        "last_payment_amount": 0.00
    },
    "cust_003": {
        "id": "cust_003",
        "name": "Global Manufacturing Inc",
        "email": "accounts@globalmanuf.com",
        "phone": "+1-555-0789",
        "account_number": "ACC-123456789",
        "status": "suspended",
        "credit_limit": 75000.00,
        "current_balance": 45000.00,
        "created_date": "2023-11-10",
        "last_payment_date": None,
        "last_payment_amount": 0.00
    }
}

transactions = []

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "CRM System", "timestamp": datetime.now().isoformat()})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get all customers or search by query parameters"""
    search_term = request.args.get('search', '').lower()
    status_filter = request.args.get('status', '').lower()
    
    filtered_customers = list(customers.values())
    
    if search_term:
        filtered_customers = [
            c for c in filtered_customers 
            if search_term in c['name'].lower() or search_term in c['email'].lower()
        ]
    
    if status_filter:
        filtered_customers = [c for c in filtered_customers if c['status'] == status_filter]
    
    return jsonify({
        "customers": filtered_customers,
        "total": len(filtered_customers),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer by ID"""
    customer = customers.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    return jsonify(customer)

@app.route('/api/customers/by-account/<account_number>', methods=['GET'])
def get_customer_by_account(account_number):
    """Get customer by account number"""
    for customer in customers.values():
        if customer['account_number'] == account_number:
            return jsonify(customer)
    
    return jsonify({"error": "Customer not found"}), 404

@app.route('/api/customers/<customer_id>/credit-check', methods=['GET'])
def credit_check(customer_id):
    """Check if customer has sufficient credit for a transaction"""
    customer = customers.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    amount = float(request.args.get('amount', 0))
    available_credit = customer['credit_limit'] - customer['current_balance']
    
    return jsonify({
        "customer_id": customer_id,
        "credit_limit": customer['credit_limit'],
        "current_balance": customer['current_balance'],
        "available_credit": available_credit,
        "requested_amount": amount,
        "approved": amount <= available_credit and customer['status'] == 'active',
        "status": customer['status']
    })

@app.route('/api/customers/<customer_id>/update-balance', methods=['POST'])
def update_balance(customer_id):
    """Update customer balance with payment processing"""
    customer = customers.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    data = request.get_json()
    amount = data.get('amount', 0)
    transaction_type = data.get('type', 'payment')  # payment, charge, adjustment
    reference = data.get('reference', '')
    bank_transaction_id = data.get('bank_transaction_id', '')
    
    old_balance = customers[customer_id]['current_balance']
    
    if transaction_type == 'payment':
        customers[customer_id]['current_balance'] -= amount
        customers[customer_id]['last_payment_date'] = datetime.now().isoformat()
        customers[customer_id]['last_payment_amount'] = amount
    elif transaction_type == 'charge':
        customers[customer_id]['current_balance'] += amount
    elif transaction_type == 'adjustment':
        customers[customer_id]['current_balance'] += amount  # Can be negative for credits
    
    # Ensure balance doesn't go negative beyond credit limit
    if customers[customer_id]['current_balance'] < 0:
        available_credit = customers[customer_id]['credit_limit']
        if abs(customers[customer_id]['current_balance']) > available_credit:
            return jsonify({
                "error": "Payment would exceed credit limit",
                "available_credit": available_credit,
                "attempted_balance": customers[customer_id]['current_balance']
            }), 400
    
    # Record transaction with more details
    transaction = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "amount": amount,
        "type": transaction_type,
        "reference": reference,
        "bank_transaction_id": bank_transaction_id,
        "timestamp": datetime.now().isoformat(),
        "old_balance": old_balance,
        "new_balance": customers[customer_id]['current_balance'],
        "processed_by": "system"
    }
    transactions.append(transaction)
    
    return jsonify({
        "transaction": transaction,
        "customer": customers[customer_id],
        "balance_change": amount if transaction_type == 'charge' else -amount
    })

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions"""
    customer_id = request.args.get('customer_id')
    if customer_id:
        filtered_transactions = [t for t in transactions if t['customer_id'] == customer_id]
        return jsonify({"transactions": filtered_transactions})
    
    return jsonify({"transactions": transactions})

if __name__ == '__main__':
    print("Starting CRM System on port 5001...")
    print("Available endpoints:")
    print("- GET /api/health - Health check")
    print("- GET /api/customers - Get all customers (supports ?search= and ?status= filters)")
    print("- GET /api/customers/<id> - Get customer by ID")
    print("- GET /api/customers/by-account/<account_number> - Get customer by account number")
    print("- GET /api/customers/<id>/credit-check?amount=X - Check credit availability")
    print("- POST /api/customers/<id>/update-balance - Update customer balance")
    print("- GET /api/transactions - Get all transactions (supports ?customer_id= filter)")
    app.run(debug=True, port=5001)