from flask import Flask, jsonify, request
from datetime import datetime
import uuid
import json

app = Flask(__name__)

# Mock email storage
sent_emails = []
email_templates = {
    "payment_mismatch": {
        "subject": "Payment Processing Alert - Transaction Mismatch",
        "template": """
Dear Finance Team,

A payment transaction requires your attention:

Transaction Details:
- Transaction ID: {transaction_id}
- Account Number: {account_number}
- Amount: ${amount}
- Date: {transaction_date}
- Reference: {reference}

Issue: {issue_description}

Customer Information:
- Customer: {customer_name}
- Email: {customer_email}
- Account Status: {customer_status}

Outstanding Invoices:
{outstanding_invoices}

Action Required: {action_required}

Please review and take appropriate action.

Best regards,
Automated Payment Processing System
        """
    },
    "overpayment_alert": {
        "subject": "Overpayment Alert - Customer {customer_name}",
        "template": """
Dear Customer Service Team,

We have received an overpayment that requires processing:

Payment Details:
- Customer: {customer_name}
- Account: {account_number}
- Payment Amount: ${payment_amount}
- Outstanding Balance: ${outstanding_amount}
- Overpayment: ${overpayment_amount}

This overpayment needs to be processed according to company policy.
Options: Refund, Credit to account, or Apply to future invoices.

Customer Contact: {customer_email}

Please contact the customer to confirm their preference.

Best regards,
Payment Processing System
        """
    },
    "unknown_customer": {
        "subject": "Unknown Customer Payment - Investigation Required",
        "template": """
Dear Finance Team,

We received a payment from an unknown customer account:

Payment Details:
- Transaction ID: {transaction_id}
- Account Number: {account_number}
- Amount: ${amount}
- Date: {transaction_date}
- Description: {description}

No matching customer found in CRM system.

Action Required:
1. Research customer identity
2. Determine if this is a new customer
3. Process payment appropriately or return if necessary

Holding payment pending investigation.

Best regards,
Payment Processing System
        """
    },
    "high_value_alert": {
        "subject": "High Value Transaction Alert - ${amount}",
        "template": """
Dear Management Team,

A high-value transaction has been processed:

Transaction Details:
- Customer: {customer_name}
- Account: {account_number}
- Amount: ${amount}
- Type: {transaction_type}
- Date: {transaction_date}

Customer Status: {customer_status}
Previous Balance: ${previous_balance}
New Balance: ${new_balance}

This transaction exceeds the ${threshold} threshold and has been flagged for review.

Please verify this transaction is legitimate.

Best regards,
Payment Monitoring System
        """
    },
    "suspended_customer_payment": {
        "subject": "Payment from Suspended Customer - {customer_name}",
        "template": """
Dear Customer Service Team,

We received a payment from a suspended customer account:

Customer: {customer_name}
Account: {account_number}
Amount: ${amount}
Suspension Reason: Account review required

The payment has been held pending account review.

Action Required:
1. Review customer account status
2. Determine if suspension should be lifted
3. Process or return payment accordingly

Customer Contact: {customer_email}

Best regards,
Payment Processing System
        """
    }
}

notification_rules = []

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Email Notification System", "timestamp": datetime.now().isoformat()})

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Send an email notification"""
    data = request.get_json()
    
    email_data = {
        "id": str(uuid.uuid4()),
        "to": data.get('to', 'finance@company.com'),
        "cc": data.get('cc', []),
        "subject": data.get('subject', 'Payment Processing Notification'),
        "body": data.get('body', ''),
        "priority": data.get('priority', 'normal'),  # low, normal, high, urgent
        "category": data.get('category', 'general'),  # payment_mismatch, overpayment, etc.
        "timestamp": datetime.now().isoformat(),
        "status": "sent",
        "read": False,
        "metadata": data.get('metadata', {})
    }
    
    sent_emails.append(email_data)
    
    return jsonify({
        "message": "Email sent successfully",
        "email_id": email_data["id"],
        "timestamp": email_data["timestamp"]
    })

@app.route('/api/send-template-email', methods=['POST'])
def send_template_email():
    """Send an email using a predefined template"""
    data = request.get_json()
    template_name = data.get('template', '')
    template_data = data.get('data', {})
    
    if template_name not in email_templates:
        return jsonify({"error": f"Template '{template_name}' not found"}), 400
    
    template = email_templates[template_name]
    
    # Format the template with provided data
    try:
        formatted_subject = template['subject'].format(**template_data)
        formatted_body = template['template'].format(**template_data)
    except KeyError as e:
        return jsonify({"error": f"Missing template data: {str(e)}"}), 400
    
    email_data = {
        "id": str(uuid.uuid4()),
        "to": data.get('to', 'finance@company.com'),
        "cc": data.get('cc', []),
        "subject": formatted_subject,
        "body": formatted_body,
        "priority": data.get('priority', 'normal'),
        "category": template_name,
        "template_used": template_name,
        "timestamp": datetime.now().isoformat(),
        "status": "sent",
        "read": False,
        "metadata": template_data
    }
    
    sent_emails.append(email_data)
    
    return jsonify({
        "message": "Template email sent successfully",
        "email_id": email_data["id"],
        "template": template_name,
        "timestamp": email_data["timestamp"]
    })

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Get all sent emails with optional filtering"""
    category = request.args.get('category', '')
    priority = request.args.get('priority', '')
    unread_only = request.args.get('unread', '').lower() == 'true'
    
    filtered_emails = sent_emails.copy()
    
    if category:
        filtered_emails = [e for e in filtered_emails if e.get('category', '') == category]
    
    if priority:
        filtered_emails = [e for e in filtered_emails if e.get('priority', '') == priority]
    
    if unread_only:
        filtered_emails = [e for e in filtered_emails if not e.get('read', False)]
    
    # Sort by timestamp, most recent first
    filtered_emails.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({
        "emails": filtered_emails,
        "total": len(filtered_emails),
        "unread_count": len([e for e in sent_emails if not e.get('read', False)])
    })

@app.route('/api/emails/<email_id>', methods=['GET'])
def get_email(email_id):
    """Get specific email by ID"""
    email = next((e for e in sent_emails if e['id'] == email_id), None)
    if not email:
        return jsonify({"error": "Email not found"}), 404
    
    return jsonify(email)

@app.route('/api/emails/<email_id>/mark-read', methods=['POST'])
def mark_email_read(email_id):
    """Mark an email as read"""
    email = next((e for e in sent_emails if e['id'] == email_id), None)
    if not email:
        return jsonify({"error": "Email not found"}), 404
    
    email['read'] = True
    email['read_timestamp'] = datetime.now().isoformat()
    
    return jsonify({"message": "Email marked as read", "email_id": email_id})

@app.route('/api/notification-rules', methods=['GET'])
def get_notification_rules():
    """Get all notification rules"""
    return jsonify({"rules": notification_rules})

@app.route('/api/notification-rules', methods=['POST'])
def create_notification_rule():
    """Create a new notification rule"""
    data = request.get_json()
    
    rule = {
        "id": str(uuid.uuid4()),
        "name": data.get('name', ''),
        "condition": data.get('condition', {}),  # e.g., {"amount_threshold": 10000, "customer_status": "suspended"}
        "template": data.get('template', 'payment_mismatch'),
        "recipients": data.get('recipients', ['finance@company.com']),
        "priority": data.get('priority', 'normal'),
        "active": data.get('active', True),
        "created_date": datetime.now().isoformat()
    }
    
    notification_rules.append(rule)
    
    return jsonify({
        "message": "Notification rule created",
        "rule_id": rule["id"]
    })

@app.route('/api/evaluate-notification', methods=['POST'])
def evaluate_notification():
    """Evaluate if a transaction should trigger notifications"""
    data = request.get_json()
    
    transaction = data.get('transaction', {})
    customer = data.get('customer', {})
    validation_result = data.get('validation_result', {})
    
    notifications_to_send = []
    
    # Check various conditions
    amount = transaction.get('amount', 0)
    customer_status = customer.get('status', 'unknown')
    account_number = transaction.get('account_number', '')
    
    # High value transaction
    if amount > 50000:
        notifications_to_send.append({
            "template": "high_value_alert",
            "priority": "high",
            "reason": f"Transaction amount ${amount} exceeds threshold"
        })
    
    # Suspended customer
    if customer_status == 'suspended':
        notifications_to_send.append({
            "template": "suspended_customer_payment",
            "priority": "high",
            "reason": "Payment from suspended customer account"
        })
    
    # Unknown customer
    if not customer:
        notifications_to_send.append({
            "template": "unknown_customer",
            "priority": "urgent",
            "reason": "Payment from unknown customer account"
        })
    
    # Validation issues
    if validation_result and validation_result.get('validation_status') in ['warning', 'attention_required']:
        notifications_to_send.append({
            "template": "payment_mismatch",
            "priority": "normal",
            "reason": "Payment validation issues detected"
        })
    
    # Overpayment detection
    if validation_result and 'overpayment' in validation_result.get('notes', []):
        notifications_to_send.append({
            "template": "overpayment_alert",
            "priority": "normal",
            "reason": "Customer overpayment detected"
        })
    
    return jsonify({
        "should_notify": len(notifications_to_send) > 0,
        "notifications": notifications_to_send,
        "evaluation_timestamp": datetime.now().isoformat()
    })

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all available email templates"""
    template_info = {}
    for name, template in email_templates.items():
        template_info[name] = {
            "subject": template['subject'],
            "description": f"Template for {name.replace('_', ' ')} notifications"
        }
    
    return jsonify({"templates": template_info})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get email statistics"""
    total_emails = len(sent_emails)
    unread_emails = len([e for e in sent_emails if not e.get('read', False)])
    
    # Count by category
    category_counts = {}
    priority_counts = {}
    
    for email in sent_emails:
        category = email.get('category', 'general')
        priority = email.get('priority', 'normal')
        
        category_counts[category] = category_counts.get(category, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    return jsonify({
        "total_emails": total_emails,
        "unread_emails": unread_emails,
        "categories": category_counts,
        "priorities": priority_counts,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Email Notification System on port 5003...")
    print("Available endpoints:")
    print("- GET /api/health - Health check")
    print("- POST /api/send-email - Send custom email")
    print("- POST /api/send-template-email - Send email using template")
    print("- GET /api/emails - Get all emails (supports filtering)")
    print("- GET /api/emails/<id> - Get specific email")
    print("- POST /api/emails/<id>/mark-read - Mark email as read")
    print("- POST /api/evaluate-notification - Evaluate if notification needed")
    print("- GET /api/templates - Get available templates")
    print("- GET /api/statistics - Get email statistics")
    print("- GET /api/notification-rules - Get notification rules")
    print("- POST /api/notification-rules - Create notification rule")
    app.run(debug=True, port=5003)