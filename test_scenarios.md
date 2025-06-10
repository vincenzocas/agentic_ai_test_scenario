# Test Scenarios for Mock Business System

This document outlines comprehensive test scenarios for training agents to handle various transaction processing situations in the mock CRM, ERP, and Email systems.

## Test Environment Setup

### Prerequisites
```bash
# Install dependencies
pip install flask requests

# Start services in separate terminals:
python mock_crm.py     # Port 5001
python mock_erp.py     # Port 5002  
python mock_email.py   # Port 5000
```

### Health Check
Before running tests, verify all services are healthy:
- CRM: http://localhost:5001/api/health
- ERP: http://localhost:5002/api/health
- Email: http://localhost:5000/api/health

## Test Scenarios

### 1. Perfect Match Payment ✅
**Scenario**: Customer pays exact invoice amount
- **Transaction**: $12,500 payment for invoice INV-2025-001
- **Account**: ACC-789123456 (Acme Corporation - Active)
- **Expected Outcome**: `auto_process`
- **Learning Objective**: Basic happy path processing

**Test Steps**:
1. Lookup customer in CRM ✅
2. Find matching invoice in ERP ✅  
3. Validate payment amount matches invoice ✅
4. Auto-process payment ✅
5. Update invoice status to "paid" ✅

### 2. Partial Payment 📝
**Scenario**: Customer pays less than full invoice amount
- **Transaction**: $5,000 payment for $8,750 invoice INV-2025-002
- **Account**: ACC-456789123 (Tech Solutions Ltd - Active)
- **Expected Outcome**: `review_and_process`
- **Learning Objective**: Handling partial payments

**Test Steps**:
1. Lookup customer in CRM ✅
2. Find matching invoice in ERP ✅
3. Detect partial payment (amount < invoice) ⚠️
4. Flag for review but allow processing ⚠️
5. Update invoice status to "partially_paid" ✅
6. Send notification to accounting team 📧

### 3. Unknown Customer ❌
**Scenario**: Payment from customer not in CRM system  
- **Transaction**: $15,000 from unknown account ACC-999888777
- **Account**: Not found in CRM
- **Expected Outcome**: `manual_review`
- **Learning Objective**: Handling unrecognized customers

**Test Steps**:
1. Attempt customer lookup in CRM ❌
2. Customer not found error ❌
3. Flag for manual investigation ⚠️
4. Hold payment pending review ⏸️
5. Send alert to customer service 📧

### 4. High Value Payment 💰
**Scenario**: Large payment requiring special approval
- **Transaction**: $75,000 from ACC-123456789 (Global Manufacturing Inc)
- **Account**: Suspended customer
- **Expected Outcome**: `manual_review`
- **Learning Objective**: High-value transaction handling

**Test Steps**:
1. Lookup customer in CRM ✅
2. Detect high-value amount (>$50K) ⚠️
3. Check customer status: SUSPENDED ❌
4. Require manual approval ⚠️
5. Send high-value alert to management 📧

### 5. Overpayment 💸
**Scenario**: Customer pays more than owed amount
- **Transaction**: $25,000 payment when only $12,500 owed
- **Account**: ACC-789123456 (Acme Corporation - Active)
- **Expected Outcome**: `review_and_process`
- **Learning Objective**: Overpayment handling

**Test Steps**:
1. Lookup customer in CRM ✅
2. Find outstanding invoices ✅
3. Calculate overpayment amount ($12,500) ⚠️
4. Flag for review (refund/credit options) ⚠️
5. Send overpayment alert 📧

### 6. Suspended Customer Payment ⏸️
**Scenario**: Payment from customer with suspended account
- **Transaction**: $10,000 from suspended customer
- **Account**: ACC-123456789 (Global Manufacturing Inc - Suspended)
- **Expected Outcome**: `hold`
- **Learning Objective**: Account status validation

**Test Steps**:
1. Lookup customer in CRM ✅
2. Check customer status: SUSPENDED ❌
3. Hold payment pending account review ⏸️
4. Do not process automatically ❌
5. Send suspended customer alert 📧

### 7. Duplicate Payment 🔄
**Scenario**: Potential duplicate payment for same invoice
- **Transaction**: Second $8,750 payment for INV-2025-002
- **Account**: ACC-456789123 (Tech Solutions Ltd - Active)
- **Expected Outcome**: `manual_review`
- **Learning Objective**: Duplicate detection

**Test Steps**:
1. Lookup customer in CRM ✅
2. Find matching invoice ✅
3. Check payment history ⚠️
4. Detect potential duplicate ⚠️
5. Flag for manual verification ⚠️

### 8. Incorrect Amount 💱
**Scenario**: Payment amount doesn't match any invoice exactly
- **Transaction**: $11,500 payment (invoice is $12,500)
- **Account**: ACC-789123456 (Acme Corporation - Active)
- **Expected Outcome**: `review_and_process`
- **Learning Objective**: Amount mismatch handling

**Test Steps**:
1. Lookup customer in CRM ✅
2. Find invoices but no exact match ⚠️
3. Flag amount discrepancy ⚠️
4. Allow processing with review ⚠️
5. Send payment mismatch alert 📧

### 9. Multiple Invoices Payment 📊
**Scenario**: Single payment covering multiple invoices
- **Transaction**: $20,000 payment from customer with multiple outstanding invoices
- **Account**: ACC-456789123 (Tech Solutions Ltd - Active)
- **Expected Outcome**: `review_and_process`
- **Learning Objective**: Complex payment allocation

**Test Steps**:
1. Lookup customer in CRM ✅
2. Find multiple outstanding invoices ✅
3. Determine optimal allocation strategy ⚠️
4. Flag for manual allocation review ⚠️
5. Send multi-invoice notification 📧

### 10. Zero Amount Transaction ❌
**Scenario**: Invalid transaction with zero amount
- **Transaction**: $0.00 transaction
- **Account**: ACC-789123456 (Acme Corporation - Active)
- **Expected Outcome**: `error`
- **Learning Objective**: Input validation

**Test Steps**:
1. Validate transaction amount ❌
2. Reject zero amount transaction ❌
3. Return error response ❌
4. Log invalid transaction attempt 📝

## Advanced Test Scenarios

### 11. Currency Mismatch 💱
**Scenario**: Payment in different currency
- Test foreign currency handling
- Currency conversion validation
- Multi-currency account management

### 12. Batch Payment Processing 📦
**Scenario**: Multiple payments in single batch
- Bulk transaction processing
- Error handling for partial batch failures
- Performance testing with large datasets

### 13. Network Failure Simulation 🌐
**Scenario**: Service unavailability during processing
- CRM system timeout
- ERP system connection failure  
- Email service outage
- Graceful degradation and retry logic

### 14. Fraud Detection 🔍
**Scenario**: Suspicious transaction patterns
- Unusual payment times
- Rapid successive payments
- Geographic anomalies
- Velocity checks

### 15. Integration Testing 🔗
**Scenario**: End-to-end workflow testing
- Complete transaction lifecycle
- Cross-system data consistency
- Audit trail verification
- Performance benchmarking

## Test Data Sets

### Customer Profiles
```json
{
  "active_customer": "ACC-789123456",
  "suspended_customer": "ACC-123456789", 
  "high_credit_customer": "ACC-456789123",
  "unknown_customer": "ACC-999888777"
}
```

### Invoice Scenarios
```json
{
  "pending_invoice": "INV-2025-001",
  "overdue_invoice": "INV-2025-002",
  "large_invoice": "INV-2025-003"
}
```

### Amount Thresholds
- Small payment: < $1,000
- Normal payment: $1,000 - $10,000
- Large payment: $10,000 - $50,000
- High-value payment: > $50,000

## Expected Learning Outcomes

After completing these test scenarios, agents should be able to:

1. **API Integration**: Successfully call CRM, ERP, and Email APIs
2. **Data Correlation**: Match transactions to customers and invoices
3. **Business Rules**: Apply payment processing rules correctly
4. **Error Handling**: Gracefully handle missing data and API failures
5. **Decision Making**: Choose appropriate actions based on business logic
6. **Notification Management**: Send relevant alerts to appropriate teams
7. **Edge Case Handling**: Deal with unusual or problematic transactions
8. **Performance Optimization**: Process transactions efficiently
9. **Audit Compliance**: Maintain proper transaction records
10. **User Experience**: Provide clear feedback and status updates

## Running the Tests

### Automated Test Suite
```bash
python test_cases.py
```

### Manual Testing
```bash
# Test individual scenarios using curl
curl -X POST http://localhost:5001/api/customers/cust_001/update-balance \
  -H "Content-Type: application/json" \
  -d '{"amount": 12500.00, "type": "payment", "reference": "INV-2025-001"}'
```

### Performance Testing
```bash
# Run load tests with multiple concurrent transactions
python performance_tests.py --concurrent=10 --duration=60
```

## Success Criteria

### Functional Requirements
- ✅ All happy path scenarios process correctly
- ✅ Edge cases are handled appropriately  
- ✅ Error conditions generate proper alerts
- ✅ Business rules are enforced consistently

### Performance Requirements
- ⏱️ Transaction processing < 2 seconds
- 🔄 Handle 100+ concurrent transactions
- 📊 99.9% API availability
- 💾 Maintain data consistency across systems

### Quality Requirements
- 🧪 95%+ test coverage
- 📝 Complete audit trails
- 🔒 Secure data handling
- 📧 Timely notifications for exceptions

## Troubleshooting Guide

### Common Issues
1. **Service Connection Errors**: Check if all services are running
2. **Data Mismatches**: Verify test data is properly loaded
3. **Timeout Issues**: Increase request timeout values
4. **Port Conflicts**: Ensure ports 5000-5002 are available

### Debug Commands
```bash
# Check service status
curl http://localhost:5001/api/health
curl http://localhost:5002/api/health  
curl http://localhost:5000/api/health

# View customer data
curl http://localhost:5001/api/customers

# Check invoices
curl http://localhost:5002/api/invoices

# Review sent emails
curl http://localhost:5000/api/emails
``` 