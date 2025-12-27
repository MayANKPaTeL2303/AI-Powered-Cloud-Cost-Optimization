from llm_handler import LLMHandler
from utils import load_json, save_json, validate_billing_data

class BillingGenerator:
    def __init__(self):
        self.llm = LLMHandler()
        
    def create_billing_prompt(self, profile):
        tech_stack_str = ', '.join([f"{k}: {v}" for k,v in profile.get('tech_stack',{}).items()])
        budget = profile.get('budget_inr_per_month', 'Not specified')
        
        # Simplified prompt for faster generation
        prompt = f"""Generate 12 realistic cloud billing records as a JSON array.

Project: {profile.get('name', 'Unknown Project')}
Budget: ₹{budget}/month
Tech Stack: {tech_stack_str}

Generate exactly 12 billing records. Total cost should be around ₹{budget} (90-110% of budget).

Each record MUST have these fields:
- month: "2025-01"
- service: service name (EC2, RDS, S3, Lambda, CloudWatch, etc.)
- resource_id: unique ID (e.g., "i-web-01")
- region: "ap-south-1"
- usage_type: usage type description
- usage_quantity: number
- unit: "hours", "GB", "requests", etc.
- cost_inr: cost in rupees (number)
- desc: brief description

Example record:
{{
  "month": "2025-01",
  "service": "EC2",
  "resource_id": "i-web-01",
  "region": "ap-south-1",
  "usage_type": "t3.medium",
  "usage_quantity": 720,
  "unit": "hours",
  "cost_inr": 2500,
  "desc": "Web server"
}}

IMPORTANT: 
- Respond with ONLY the JSON array
- Start with [ and end with ]
- Include exactly 12 records
- No explanations or markdown
- Distribute costs across: Compute (40%), Database (25%), Storage (15%), Networking (10%), Other (10%)

Generate the JSON array now:"""
        
        return prompt 
    
    def generate_billing_response(self, profile):
        print("\nGenerating synthetic billing data...")
        print("This may take 30-60 seconds...")

        prompt = self.create_billing_prompt(profile)
        response = self.llm.call_llm_for_json(prompt, expected_type="array")

        if not response:
            print(" Failed to generate the billing data")
            return None
        
        # Allow 10-20 records (not just 12 minimum)
        if len(response) < 10:
            print(f" Generated only {len(response)} records, need at least 10")
            return None
        
        if not validate_billing_data(response):
            print(" Billing data validation failed")
            return None
        
        total_cost = sum(record.get('cost_inr', 0) for record in response)

        print(f" Generated {len(response)} billing records")
        print(f" Total cost: ₹{total_cost:,.2f}")

        return response
    
    def run(self):
        profile = load_json("project_profile.json")
        if not profile:
            print(" Could not load project_profile.json")
            return False
        
        print(f"\n{'='*60}")
        print(f"Generating billing for: {profile.get('name','Unknown')}")
        print(f"Budget: ₹{profile.get('budget_inr_per_month', 0):,}/month")
        print(f"{'='*60}")

        billing = self.generate_billing_response(profile)
        if not billing:
            return False
        
        if save_json("mock_billing.json", billing):
            services = {}
            for record in billing:
                service = record.get('service', 'Unknown')
                cost = record.get('cost_inr', 0)
                services[service] = services.get(service, 0) + cost

            print(f"\n{'='*60}")
            print("Cost breakdown by service:")
            print(f"{'='*60}")
            for service, cost in sorted(services.items(), key=lambda x: x[1], reverse=True):
                print(f"  {service:20s} ₹{cost:>10,.2f}")
            print(f"{'='*60}\n")
            return True 
        
        return False
    
if __name__ == "__main__":
    generator = BillingGenerator()
    generator.run()