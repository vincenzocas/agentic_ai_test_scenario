from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

# Mock ERP database
invoices = {
    "INV-2025-001": {
        "id": "INV-2025-001",
        "customer_account": "ACC-789123456",
        "amount": 12500.00,
        "status": "pending",
        "due_date": "2025-07-15",
        "issue_date": "2025-06-01",
        "description": "Software licensing - Q2 2025",
        "payment_terms": "NET30",
        "paid_amount": 0.00,
        "last_payment_date": None,
        "last_payment_amount": 0.00,
        "line_items": [
            {"product": "Enterprise License", "quantity": 5, "unit_price": 2500.00}
        ]
    },
    "INV-2025-002": {
        "id": "INV-2025-002",
        "customer_account": "ACC-456789123",
        "amount": 8750.00,
        "status": "overdue",
        "due_date": "2025-05-30",
        "issue_date": "2025-05-01",
        "description": "Consulting services - May 2025",
        "payment_terms": "NET30",
        "paid_amount": 0.00,
        "last_payment_date": None,
        "last_payment_amount": 0.00,
        "line_items": [
            {"product": "Consulting Hours", "quantity": 35, "unit_price": 250.00}
        ]
    },
    "INV-2025-003": {
        "id": "INV-2025-003",
        "customer_account": "ACC-123456789",
        "amount": 45000.00,
        "status": "pending",
        "due_date": "2025-06-30",
        "issue_date": "2025-06-01",
        "description": "Hardware procurement",
        "payment_terms": "NET30",
        "paid_amount": 0.00,
        "last_payment_date": None,
        "last_payment_amount": 0.00,
        "line_items": [
            {"product": "Server Equipment", "quantity": 3, "unit_price": 15000.00}
        ]
    }
}

purchase_orders = {
    "PO-2025-101": {
        "id": "PO-2025-101",
        "supplier": "Tech Components Inc",
        "amount": 25000.00,
        "status": "approved",
        "expected_delivery": "2025-06-20",
        "order_date": "2025-06-01",
        "description": "Network infrastructure components",
        "line_items": [
            {"product": "Network Switches", "quantity": 10, "unit_price": 2500.00}
        ]
    },
    "PO-2025-102": {
        "id": "PO-2025-102",
        "supplier": "Office Supplies Ltd",
        "amount": 1500.00,
        "status": "pending",
        "expected_delivery": "2025-06-15",
        "order_date": "2025-06-05",
        "description": "Office supplies Q2",
        "line_items": [
            {"product": "Office Supplies", "quantity": 1, "unit_price": 1500.00}
        ]
    }
}

payments = []

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "ERP System", "timestamp": datetime.now().isoformat()})

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    """Get all invoices or filter by parameters"""
    status_filter = request.args.get('status', '').lower()
    customer_account = request.args.get('customer_account', '')
    
    filtered_invoices = list(invoices.values())
    
    if status_filter:
        filtered_invoices = [i for i in filtered_invoices if i['status'] == status_filter]
    
    if customer_account:
        filtered_invoices = [i for i in filtered_invoices if i['customer_account'] == customer_account]
    
    return jsonify({
        "invoices": filtered_invoices,
        "total": len(filtered_invoices),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/invoices/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Get invoice by ID"""
    invoice = invoices.get(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404
    
    return jsonify(invoice)

@app.route('/api/invoices/by-account/<account_number>', methods=['GET'])
def get_invoices_by_account(account_number):
    """Get invoices by customer account number"""
    account_invoices = [i for i in invoices.values() if i['customer_account'] == account_number]
    
    return jsonify({
        "invoices": account_invoices,
        "total": len(account_invoices),
        "account_number": account_number
    })

@app.route('/api/invoices/<invoice_id>/payment', methods=['POST'])
def process_payment(invoice_id):
    """Process payment for an invoice with full payment allocation"""
    invoice = invoices.get(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404
    
    data = request.get_json()
    payment_amount = data.get('amount', 0)
    payment_method = data.get('method', 'bank_transfer')
    reference = data.get('reference', '')
    bank_transaction_id = data.get('bank_transaction_id', '')
    
    # Get current outstanding amount
    paid_amount = sum(p['amount'] for p in payments if p['invoice_id'] == invoice_id)
    outstanding_amount = invoice['amount'] - paid_amount
    
    if payment_amount > outstanding_amount:
        return jsonify({
            "error": "Payment amount exceeds outstanding balance",
            "outstanding_amount": outstanding_amount,
            "payment_amount": payment_amount,
            "overpayment": payment_amount - outstanding_amount
        }), 400
    
    # Create payment record with enhanced tracking
    payment = {
        "id": str(uuid.uuid4()),
        "invoice_id": invoice_id,
        "customer_account": invoice['customer_account'],
        "amount": payment_amount,
        "method": payment_method,
        "reference": reference,
        "bank_transaction_id": bank_transaction_id,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "processed_by": "system",
        "outstanding_before": outstanding_amount,
        "outstanding_after": outstanding_amount - payment_amount
    }
    payments.append(payment)
    
    # Update invoice status based on payment
    new_outstanding = outstanding_amount - payment_amount
    if new_outstanding <= 0.01:  # Account for floating point precision
        invoices[invoice_id]['status'] = 'paid'
        invoices[invoice_id]['paid_date'] = datetime.now().isoformat()
        invoices[invoice_id]['paid_amount'] = invoice['amount']
    else:
        invoices[invoice_id]['status'] = 'partially_paid'
        invoices[invoice_id]['paid_amount'] = invoice['amount'] - new_outstanding
    
    # Update last payment info
    invoices[invoice_id]['last_payment_date'] = datetime.now().isoformat()
    invoices[invoice_id]['last_payment_amount'] = payment_amount
    
    return jsonify({
        "payment": payment,
        "invoice": invoices[invoice_id],
        "message": f"Payment of ${payment_amount} processed successfully",
        "remaining_balance": new_outstanding
    })

@app.route('/api/purchase-orders', methods=['GET'])
def get_purchase_orders():
    """Get all purchase orders"""
    status_filter = request.args.get('status', '').lower()
    
    filtered_pos = list(purchase_orders.values())
    
    if status_filter:
        filtered_pos = [po for po in filtered_pos if po['status'] == status_filter]
    
    return jsonify({
        "purchase_orders": filtered_pos,
        "total": len(filtered_pos),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/purchase-orders/<po_id>', methods=['GET'])
def get_purchase_order(po_id):
    """Get purchase order by ID"""
    po = purchase_orders.get(po_id)
    if not po:
        return jsonify({"error": "Purchase order not found"}), 404
    
    return jsonify(po)

@app.route('/api/cash-flow/analysis', methods=['GET'])
def cash_flow_analysis():
    """Get cash flow analysis"""
    # Calculate totals
    pending_receivables = sum(i['amount'] for i in invoices.values() if i['status'] in ['pending', 'overdue'])
    total_payables = sum(po['amount'] for po in purchase_orders.values() if po['status'] == 'approved')
    
    overdue_invoices = [i for i in invoices.values() if i['status'] == 'overdue']
    overdue_amount = sum(i['amount'] for i in overdue_invoices)
    
    return jsonify({
        "summary": {
            "pending_receivables": pending_receivables,
            "total_payables": total_payables,
            "net_cash_flow": pending_receivables - total_payables,
            "overdue_amount": overdue_amount,
            "overdue_count": len(overdue_invoices)
        },
        "overdue_invoices": overdue_invoices,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/payments', methods=['GET'])
def get_payments():
    """Get all payments"""
    invoice_id = request.args.get('invoice_id')
    if invoice_id:
        filtered_payments = [p for p in payments if p['invoice_id'] == invoice_id]
        return jsonify({"payments": filtered_payments})
    
    return jsonify({"payments": payments})

@app.route('/api/financial/validate-transaction', methods=['POST'])
def validate_transaction():
    """Validate if a transaction can be processed based on outstanding invoices"""
    data = request.get_json()
    account_number = data.get('account_number')
    transaction_amount = data.get('amount', 0)
    transaction_type = data.get('type', 'payment')  # payment, charge, refund
    
    if not account_number:
        return jsonify({"error": "Account number required"}), 400
    
    # Get customer invoices
    customer_invoices = [i for i in invoices.values() if i['customer_account'] == account_number]
    outstanding_amount = sum(i['amount'] for i in customer_invoices if i['status'] in ['pending', 'overdue'])
    
    validation_result = {
        "account_number": account_number,
        "transaction_amount": transaction_amount,
        "transaction_type": transaction_type,
        "outstanding_invoices": outstanding_amount,
        "invoice_count": len(customer_invoices),
        "validation_status": "approved",
        "notes": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Add validation logic
    if transaction_type == "payment" and transaction_amount > outstanding_amount:
        validation_result["validation_status"] = "warning"
        validation_result["notes"].append("Payment amount exceeds outstanding invoices")
    
    overdue_invoices = [i for i in customer_invoices if i['status'] == 'overdue']
    if overdue_invoices:
        validation_result["validation_status"] = "attention_required"
        validation_result["notes"].append(f"Customer has {len(overdue_invoices)} overdue invoices")
    
    if outstanding_amount > 50000:
        validation_result["validation_status"] = "high_value"
        validation_result["notes"].append("High value customer - manual review recommended")
    
    return jsonify(validation_result)

if __name__ == '__main__':
    print("Starting ERP System on port 5002...")
    print("Available endpoints:")
    print("- GET /api/health - Health check")
    print("- GET /api/invoices - Get all invoices (supports ?status= and ?customer_account= filters)")
    print("- GET /api/invoices/<id> - Get invoice by ID")
    print("- GET /api/invoices/by-account/<account_number> - Get invoices by account")
    print("- POST /api/invoices/<id>/payment - Process payment for invoice")
    print("- GET /api/purchase-orders - Get purchase orders (supports ?status= filter)")
    print("- GET /api/purchase-orders/<id> - Get purchase order by ID")
    print("- GET /api/cash-flow/analysis - Get cash flow analysis")
    print("- GET /api/payments - Get all payments (supports ?invoice_id= filter)")
    print("- POST /api/financial/validate-transaction - Validate transaction against invoices")
    app.run(debug=True, port=5002)