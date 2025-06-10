#!/usr/bin/env python3
"""
Comprehensive Test Cases for Mock Business System
Tests various transaction processing scenarios for agent training
"""

import requests
import json
import time
from datetime import datetime

class BusinessSystemTestCases:
    """Test cases for the mock CRM, ERP, and Email systems"""
    
    def __init__(self):
        self.crm_base_url = "http://localhost:5001/api"
        self.erp_base_url = "http://localhost:5002/api"
        self.email_base_url = "http://localhost:5000/api"
        
    def check_services_health(self):
        """Verify all services are running"""
        services = {
            "CRM": f"{self.crm_base_url}/health",
            "ERP": f"{self.erp_base_url}/health", 
            "Email": f"{self.email_base_url}/health"
        }
        
        results = {}
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                results[service] = response.status_code == 200
                if results[service]:
                    print(f"✅ {service} service is healthy")
                else:
                    print(f"❌ {service} service returned status {response.status_code}")
            except Exception as e:
                results[service] = False
                print(f"❌ {service} service not available: {e}")
        
        return all(results.values())

# Test Data Scenarios
TEST_TRANSACTIONS = {
    "perfect_match": {
        "transaction_id": "TXN-PERFECT-001",
        "account_number": "ACC-789123456",
        "amount": 12500.00,
        "type": "credit",
        "description": "Payment received - Software licensing",
        "timestamp": "2025-06-10T09:15:00Z",
        "reference": "INV-2025-001",
        "bank_reference": "WIRE_TXN_001",
        "expected_outcome": "auto_process",
        "description_text": "Exact match - payment equals invoice amount"
    },
    
    "partial_payment": {
        "transaction_id": "TXN-PARTIAL-002", 
        "account_number": "ACC-456789123",
        "amount": 5000.00,
        "type": "credit",
        "description": "Partial payment - Consulting services",
        "timestamp": "2025-06-10T14:30:00Z",
        "reference": "INV-2025-002",
        "bank_reference": "ACH_PARTIAL_001",
        "expected_outcome": "review_and_process",
        "description_text": "Partial payment - less than invoice amount"
    },
    
    "unknown_customer": {
        "transaction_id": "TXN-UNKNOWN-003",
        "account_number": "ACC-999888777",
        "amount": 15000.00,
        "type": "credit", 
        "description": "Unknown payment source",
        "timestamp": "2025-06-10T16:45:00Z",
        "reference": "UNKNOWN_REF",
        "bank_reference": "MYSTERY_PAYMENT",
        "expected_outcome": "manual_review",
        "description_text": "Customer not found in CRM system"
    },
    
    "high_value_payment": {
        "transaction_id": "TXN-HIGHVAL-004",
        "account_number": "ACC-123456789",
        "amount": 75000.00,
        "type": "credit",
        "description": "Large payment - requires review", 
        "timestamp": "2025-06-10T17:20:00Z",
        "reference": "BULK-PAYMENT-Q2",
        "bank_reference": "HIGH_VALUE_001",
        "expected_outcome": "manual_review",
        "description_text": "High value payment from suspended customer"
    },
    
    "overpayment": {
        "transaction_id": "TXN-OVERPAY-005",
        "account_number": "ACC-789123456", 
        "amount": 25000.00,
        "type": "credit",
        "description": "Overpayment scenario",
        "timestamp": "2025-06-10T18:00:00Z",
        "reference": "OVERPAY_TEST",
        "bank_reference": "EXCESS_PAYMENT",
        "expected_outcome": "review_and_process",
        "description_text": "Payment exceeds outstanding invoice amount"
    },
    
    "suspended_customer": {
        "transaction_id": "TXN-SUSPENDED-006",
        "account_number": "ACC-123456789",
        "amount": 10000.00,
        "type": "credit",
        "description": "Payment from suspended account",
        "timestamp": "2025-06-10T19:15:00Z", 
        "reference": "SUSPENDED_PAY",
        "bank_reference": "SUSP_PAYMENT",
        "expected_outcome": "hold",
        "description_text": "Payment from customer with suspended status"
    },
    
    "zero_amount": {
        "transaction_id": "TXN-ZERO-010",
        "account_number": "ACC-789123456",
        "amount": 0.00,
        "type": "credit",
        "description": "Zero amount transaction",
        "timestamp": "2025-06-10T23:15:00Z",
        "reference": "ZERO_TEST",
        "bank_reference": "ZERO_AMT",
        "expected_outcome": "error",
        "description_text": "Invalid zero amount transaction"
    }
}

class TransactionTestRunner:
    """Runs comprehensive tests on transaction processing scenarios"""
    
    def __init__(self):
        self.test_system = BusinessSystemTestCases()
        self.results = []
        
    def run_all_tests(self):
        """Execute all test scenarios"""
        print("🚀 Starting Comprehensive Transaction Processing Tests")
        print("=" * 60)
        
        # Check system health first
        if not self.test_system.check_services_health():
            print("❌ Some services are not available. Please start all services first.")
            print("\nTo start services:")
            print("Terminal 1: python mock_crm.py")
            print("Terminal 2: python mock_erp.py") 
            print("Terminal 3: python mock_email.py")
            return False
            
        print("✅ All services are healthy. Running test scenarios...\n")
        
        # Run each test scenario
        for test_name, transaction in TEST_TRANSACTIONS.items():
            print(f"🧪 Testing: {test_name}")
            print(f"   Scenario: {transaction['description_text']}")
            
            result = self.run_single_test(test_name, transaction)
            self.results.append(result)
            
            self.print_test_result(result)
            print("-" * 40)
            time.sleep(1)  # Brief pause between tests
            
        self.print_summary()
        return True
    
    def run_single_test(self, test_name, transaction):
        """Run a single test scenario"""
        result = {
            "test_name": test_name,
            "transaction": transaction,
            "steps": [],
            "success": False,
            "actual_outcome": None,
            "expected_outcome": transaction["expected_outcome"],
            "errors": [],
            "execution_time": 0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Check customer exists
            customer_step = self.check_customer_exists(transaction["account_number"])
            result["steps"].append(customer_step)
            
            # Step 2: Get customer invoices 
            invoices_step = self.get_customer_invoices(transaction["account_number"])
            result["steps"].append(invoices_step)
            
            # Step 3: Validate transaction
            validation_step = self.validate_transaction(transaction)
            result["steps"].append(validation_step)
            
            # Step 4: Determine expected action
            decision_step = self.make_decision(transaction, customer_step, invoices_step, validation_step)
            result["steps"].append(decision_step)
            result["actual_outcome"] = decision_step.get("action", "unknown")
            
            # Step 5: Send appropriate notifications
            notification_step = self.send_notifications(transaction, decision_step)
            result["steps"].append(notification_step)
            
            # Check if outcome matches expectation
            result["success"] = result["actual_outcome"] == result["expected_outcome"]
            
        except Exception as e:
            result["errors"].append(f"Test execution error: {str(e)}")
            
        result["execution_time"] = time.time() - start_time
        return result
    
    def check_customer_exists(self, account_number):
        """Test customer lookup in CRM"""
        step = {
            "step": "customer_lookup",
            "success": False,
            "data": None,
            "error": None
        }
        
        try:
            url = f"{self.test_system.crm_base_url}/customers/by-account/{account_number}"
            response = requests.get(url, timeout=5)
            
            step["success"] = response.status_code == 200
            if step["success"]:
                step["data"] = response.json()
            else:
                step["error"] = f"Customer not found (Status: {response.status_code})"
                
        except Exception as e:
            step["error"] = f"CRM API Error: {str(e)}"
            
        return step
    
    def get_customer_invoices(self, account_number):
        """Test invoice lookup in ERP"""
        step = {
            "step": "invoice_lookup",
            "success": False,
            "data": None,
            "error": None
        }
        
        try:
            url = f"{self.test_system.erp_base_url}/invoices/by-account/{account_number}"
            response = requests.get(url, timeout=5)
            
            step["success"] = response.status_code == 200
            if step["success"]:
                step["data"] = response.json()
            else:
                step["error"] = f"Invoices not found (Status: {response.status_code})"
                
        except Exception as e:
            step["error"] = f"ERP API Error: {str(e)}"
            
        return step
    
    def validate_transaction(self, transaction):
        """Test transaction validation in ERP"""
        step = {
            "step": "transaction_validation",
            "success": False,
            "data": None,
            "error": None
        }
        
        try:
            url = f"{self.test_system.erp_base_url}/financial/validate-transaction"
            payload = {
                "account_number": transaction["account_number"],
                "amount": transaction["amount"],
                "type": "payment" if transaction["type"] == "credit" else "charge",
                "transaction_id": transaction["transaction_id"]
            }
            response = requests.post(url, json=payload, timeout=5)
            
            step["success"] = response.status_code == 200
            if step["success"]:
                step["data"] = response.json()
            else:
                step["error"] = f"Validation failed (Status: {response.status_code})"
                
        except Exception as e:
            step["error"] = f"Validation API Error: {str(e)}"
            
        return step
    
    def make_decision(self, transaction, customer_step, invoices_step, validation_step):
        """Test decision-making logic"""
        step = {
            "step": "decision_making",
            "success": True,
            "action": "unknown",
            "confidence": 0.0,
            "reasons": [],
            "next_steps": []
        }
        
        # Customer not found
        if not customer_step["success"]:
            step["action"] = "manual_review"
            step["confidence"] = 0.0
            step["reasons"].append("Customer not found in CRM")
            step["next_steps"].append("Research customer or return payment")
            return step
        
        customer = customer_step.get("data", {})
        
        # Customer suspended
        if customer.get("status") == "suspended":
            step["action"] = "hold"
            step["confidence"] = 0.9
            step["reasons"].append("Customer account is suspended")
            step["next_steps"].append("Contact customer service team")
            return step
        
        # Zero amount
        if transaction["amount"] <= 0:
            step["action"] = "error"
            step["confidence"] = 1.0
            step["reasons"].append("Invalid transaction amount")
            step["next_steps"].append("Reject transaction")
            return step
        
        # High value payment
        if transaction["amount"] > 50000:
            step["action"] = "manual_review"
            step["confidence"] = 0.3
            step["reasons"].append("High value payment requires manual approval")
            step["next_steps"].append("Manager approval required")
            return step
        
        # Check validation results
        if validation_step["success"]:
            validation = validation_step.get("data", {})
            if validation.get("validation_status") == "approved":
                step["action"] = "auto_process"
                step["confidence"] = 0.95
                step["reasons"].append("All validations passed")
                step["next_steps"].append("Process payment automatically")
            elif validation.get("validation_status") == "warning":
                step["action"] = "review_and_process"
                step["confidence"] = 0.7
                step["reasons"].extend(validation.get("notes", []))
                step["next_steps"].append("Review payment amount vs outstanding invoices")
            else:
                step["action"] = "manual_review"
                step["confidence"] = 0.3
                step["reasons"].extend(validation.get("notes", []))
                step["next_steps"].append("Manual review required")
        else:
            step["action"] = "manual_review"
            step["confidence"] = 0.2
            step["reasons"].append("Unable to validate transaction")
            step["next_steps"].append("Manual validation required")
        
        return step
    
    def send_notifications(self, transaction, decision_step):
        """Test email notification system"""
        step = {
            "step": "notification",
            "success": False,
            "data": None,
            "error": None
        }
        
        try:
            # Determine appropriate email template
            template_map = {
                "manual_review": "unknown_customer",
                "hold": "suspended_customer_payment", 
                "review_and_process": "payment_mismatch",
                "auto_process": None,  # No notification needed for auto-processed
                "error": "payment_mismatch"
            }
            
            template = template_map.get(decision_step["action"])
            
            if template:
                url = f"{self.test_system.email_base_url}/send-template-email"
                payload = {
                    "template": template,
                    "data": {
                        "transaction_id": transaction["transaction_id"],
                        "account_number": transaction["account_number"],
                        "amount": str(transaction["amount"]),
                        "transaction_date": transaction["timestamp"],
                        "reference": transaction["reference"],
                        "customer_name": "Test Customer",
                        "customer_email": "test@example.com",
                        "customer_status": "active",
                        "issue_description": "; ".join(decision_step["reasons"]),
                        "action_required": "; ".join(decision_step["next_steps"]),
                        "outstanding_invoices": "See ERP system for details",
                        "description": transaction["description"]
                    }
                }
                response = requests.post(url, json=payload, timeout=5)
                step["success"] = response.status_code == 200
                if step["success"]:
                    step["data"] = response.json()
                else:
                    step["error"] = f"Email failed (Status: {response.status_code})"
            else:
                step["success"] = True
                step["data"] = {"message": "No notification required"}
                
        except Exception as e:
            step["error"] = f"Email API Error: {str(e)}"
            
        return step
    
    def print_test_result(self, result):
        """Print formatted test result"""
        status_icon = "✅" if result["success"] else "❌"
        print(f"   {status_icon} Expected: {result['expected_outcome']} | Actual: {result['actual_outcome']}")
        print(f"   ⏱️  Execution time: {result['execution_time']:.2f}s")
        
        if result["errors"]:
            for error in result["errors"]:
                print(f"   ⚠️  Error: {error}")
        
        # Show step results
        for step in result["steps"]:
            step_icon = "✅" if step["success"] else "❌"
            print(f"   {step_icon} {step['step']}")
            if step.get("error"):
                print(f"      ⚠️  {step['error']}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test_name']}: Expected {result['expected_outcome']}, got {result['actual_outcome']}")
        
        print(f"\n📈 Performance:")
        avg_time = sum(r["execution_time"] for r in self.results) / total_tests
        print(f"   Average execution time: {avg_time:.2f}s")

def run_interactive_test():
    """Interactive test runner with menu"""
    runner = TransactionTestRunner()
    
    while True:
        print("\n" + "="*50)
        print("🧪 TRANSACTION PROCESSING TEST SUITE")
        print("="*50)
        print("1. Run all test scenarios")
        print("2. Run specific test scenario")
        print("3. List available test scenarios")
        print("4. Check system health")
        print("5. View sample transaction data")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            runner.run_all_tests()
            
        elif choice == "2":
            print("\nAvailable test scenarios:")
            for i, (name, data) in enumerate(TEST_TRANSACTIONS.items(), 1):
                print(f"{i}. {name} - {data['description_text']}")
            
            try:
                test_num = int(input("\nSelect test number: ")) - 1
                test_names = list(TEST_TRANSACTIONS.keys())
                if 0 <= test_num < len(test_names):
                    test_name = test_names[test_num]
                    transaction = TEST_TRANSACTIONS[test_name]
                    print(f"\n🧪 Running: {test_name}")
                    result = runner.run_single_test(test_name, transaction)
                    runner.print_test_result(result)
                else:
                    print("❌ Invalid test number")
            except ValueError:
                print("❌ Please enter a valid number")
                
        elif choice == "3":
            print("\n📋 Available Test Scenarios:")
            for name, data in TEST_TRANSACTIONS.items():
                print(f"• {name}: {data['description_text']}")
                print(f"  Expected outcome: {data['expected_outcome']}")
                print()
                
        elif choice == "4":
            print("\n🏥 Checking system health...")
            if runner.test_system.check_services_health():
                print("✅ All services are healthy")
            else:
                print("❌ Some services are not available")
                
        elif choice == "5":
            print("\n💾 Sample Transaction Data:")
            print(json.dumps(list(TEST_TRANSACTIONS.values())[0], indent=2))
            
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option. Please select 1-6.")

if __name__ == "__main__":
    print("🚀 Mock Business System Test Cases")
    print("This script tests various transaction processing scenarios")
    print("\nMake sure all services are running:")
    print("  - CRM System: python mock_crm.py (port 5001)")
    print("  - ERP System: python mock_erp.py (port 5002)")  
    print("  - Email System: python mock_email.py (port 5000)")
    
    run_interactive_test() 