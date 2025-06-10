# Mock Business System

A comprehensive mock business system consisting of three interconnected Flask-based services that simulate real-world enterprise applications for testing and development purposes.

## Overview

This system provides mock implementations of:
- **Email Notification System** - Automated email alerts and notifications
- **CRM (Customer Relationship Management) System** - Customer data and transaction management
- **ERP (Enterprise Resource Planning) System** - Invoice, payment, and purchase order management

## Architecture

The system consists of three independent Flask services that can communicate with each other:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Email Service  │    │   CRM Service   │    │   ERP Service   │
│   (Port 5000)   │    │   (Port 5001)   │    │   (Port 5002)   │
│                 │    │                 │    │                 │
│ • Email alerts  │    │ • Customer data │    │ • Invoices      │
│ • Notifications │    │ • Account mgmt  │    │ • Payments      │
│ • Templates     │    │ • Transactions  │    │ • Purchase orders│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Services

### 1. Email Notification System (`mock_email.py`)

Handles automated email notifications with predefined templates for various business scenarios.

**Key Features:**
- Pre-built email templates for payment alerts, overdue notices, high-value transactions
- Email queuing and status tracking
- Notification rules engine
- Template-based email generation

**API Endpoints:**
- `GET /api/health` - Health check
- `POST /api/send-email` - Send custom email
- `POST /api/send-template-email` - Send templated email
- `GET /api/emails` - Retrieve sent emails
- `GET /api/templates` - Get available templates
- `GET /api/statistics` - Email statistics

### 2. CRM System (`mock_crm.py`)

Manages customer information, account balances, and customer transactions.

**Key Features:**
- Customer database with account management
- Credit limit monitoring
- Balance tracking and payment processing
- Customer status management (active, suspended)
- Transaction history

**API Endpoints:**
- `GET /api/health` - Health check
- `GET /api/customers` - Get all customers (with search/filter)
- `GET /api/customers/<id>` - Get customer by ID
- `GET /api/customers/by-account/<account>` - Get customer by account number
- `GET /api/customers/<id>/credit-check` - Check credit availability
- `POST /api/customers/<id>/update-balance` - Update customer balance
- `GET /api/transactions` - Get transaction history

### 3. ERP System (`mock_erp.py`)

Handles invoicing, payment processing, and purchase order management.

**Key Features:**
- Invoice management (pending, paid, overdue)
- Payment processing with full allocation tracking
- Purchase order management
- Cash flow analysis
- Financial transaction validation

**API Endpoints:**
- `GET /api/health` - Health check
- `GET /api/invoices` - Get invoices (with filters)
- `GET /api/invoices/<id>` - Get specific invoice
- `GET /api/invoices/by-account/<account>` - Get invoices by customer account
- `POST /api/invoices/<id>/payment` - Process payment for invoice
- `GET /api/purchase-orders` - Get purchase orders
- `GET /api/cash-flow/analysis` - Cash flow analysis
- `GET /api/payments` - Get payment history

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd agentic_ai_test_scenario
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Individual Services

**Start Email Service (Port 5000):**
```bash
python mock_email.py
```

**Start CRM Service (Port 5001):**
```bash
python mock_crm.py
```

**Start ERP Service (Port 5002):**
```bash
python mock_erp.py
```

### Running All Services Simultaneously

In separate terminal windows, run each service with the commands above.

## Sample Data

The system comes pre-loaded with sample data:

**Customers:**
- Acme Corporation (Active, $50K credit limit)
- Tech Solutions Ltd (Active, $25K credit limit)  
- Global Manufacturing Inc (Suspended, $75K credit limit)

**Invoices:**
- Software licensing ($12,500 - pending)
- Consulting services ($8,750 - overdue)
- Hardware procurement ($45,000 - pending)

## API Usage Examples

### Check Customer Credit
```bash
curl "http://localhost:5001/api/customers/cust_001/credit-check?amount=5000"
```

### Process Invoice Payment
```bash
curl -X POST http://localhost:5002/api/invoices/INV-2025-001/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 12500.00, "method": "bank_transfer", "reference": "Payment ref 123"}'
```

### Send Payment Alert Email
```bash
curl -X POST http://localhost:5000/api/send-template-email \
  -H "Content-Type: application/json" \
  -d '{
    "template": "payment_mismatch",
    "data": {
      "transaction_id": "TXN-123",
      "customer_name": "Acme Corp",
      "amount": "5000.00"
    }
  }'
```

## Development & Testing

This mock system is designed for:
- **API Testing** - Test integrations without real business systems
- **Development** - Develop against realistic business data structures
- **Prototyping** - Rapid prototyping of business workflows
- **Training** - Learning business system integration patterns

## Dependencies

- **Flask** - Web framework for REST APIs
- **Flask-CORS** - Cross-origin resource sharing support
- **Requests** - HTTP client library

## License

This is a mock system for development and testing purposes. 