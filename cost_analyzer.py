from llm_handler import LLMHandler
from utils import load_json, save_json, validate_cost_report, format_currency
import json

class CostAnalyzer:
    def __init__(self):
        self.llm = LLMHandler()
    
    def analyze_costs(self, profile, billing):
        total_cost = sum(record.get('cost_inr', 0) for record in billing)
        budget = profile.get('budget_inr_per_month', 0)
        variance = total_cost - budget
        
        # Group by service
        service_costs = {}
        for record in billing:
            service = record.get('service', 'Unknown')
            cost = record.get('cost_inr', 0)
            service_costs[service] = service_costs.get(service, 0) + cost
        
        # Find high-cost services
        sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
        high_cost_services = dict(sorted_services[:3])
        
        return {
            "total_monthly_cost": round(total_cost, 2),
            "budget": budget,
            "budget_variance": round(variance, 2),
            "service_costs": {k: round(v, 2) for k, v in service_costs.items()},
            "high_cost_services": {k: round(v, 2) for k, v in high_cost_services.items()},
            "is_over_budget": total_cost > budget
        }
    
    def create_recommendations_prompt(self, profile, billing, analysis):
        
        service_costs_str = '\n'.join([f"  - {service}: ₹{cost:,.2f}" for service, cost in analysis['service_costs'].items()])
        
        prompt = f"""You are a cloud cost optimization expert. Generate actionable cost optimization recommendations.

Project: {profile.get('name', 'Unknown')}
Budget: ₹{analysis['budget']:,} per month
Current Cost: ₹{analysis['total_monthly_cost']:,} per month
Budget Variance: ₹{analysis['budget_variance']:,} ({"OVER" if analysis['is_over_budget'] else "UNDER"} budget)

Service Costs:
{service_costs_str}

Tech Stack: {json.dumps(profile.get('tech_stack', {}), indent=2)}

Your task: Generate 6-10 actionable cost optimization recommendations.

CRITICAL RULES:
1. Respond with ONLY a valid JSON array of recommendations
2. No explanations, no markdown, no code blocks
3. Include recommendations for: AWS, Azure, GCP alternatives, open-source options, reserved instances, right-sizing, free tiers
4. Each recommendation must have these exact fields:
   - title: Short descriptive title (string)
   - service: Service being optimized (string)
   - current_cost: Current cost in INR (number)
   - potential_savings: Estimated savings in INR (number)
   - recommendation_type: One of: "alternative_provider", "open_source", "free_tier", "right_sizing", "reserved_instances", "optimization", "cost_effective_storage"
   - description: Detailed explanation (string)
   - implementation_effort: "low", "medium", or "high"
   - risk_level: "low", "medium", or "high"
   - steps: Array of implementation steps (array of strings)
   - cloud_providers: Array of applicable providers like ["AWS", "Azure", "GCP"] or ["Open Source"] (array of strings)

Example recommendation:
{{
  "title": "Switch to Reserved Instances for EC2",
  "service": "EC2",
  "current_cost": 5000,
  "potential_savings": 1500,
  "recommendation_type": "reserved_instances",
  "description": "Reserved instances offer significant savings for predictable workloads",
  "implementation_effort": "low",
  "risk_level": "low",
  "steps": [
    "Analyze EC2 usage patterns",
    "Purchase 1-year reserved instances",
    "Monitor savings"
  ],
  "cloud_providers": ["AWS", "Azure", "GCP"]
}}

Generate 6-10 diverse recommendations now. Respond with ONLY the JSON array:"""
        
        return prompt
    
    def generate_recommendations(self, profile, billing, analysis):
        """
        Generate cost optimization recommendations
        
        Args:
            profile: Project profile dict
            billing: Billing records list
            analysis: Cost analysis dict
            
        Returns:
            list: Recommendations or None
        """
        print("Generating cost optimization recommendations using LLM...")
        
        prompt = self.create_recommendations_prompt(profile, billing, analysis)
        recommendations = self.llm.call_llm_for_json(prompt, expected_type="array")
        
        if not recommendations:
            print(" Failed to generate recommendations")
            return None
        
        print(f" Generated {len(recommendations)} recommendations")
        return recommendations
    
    def create_report(self, profile, billing):
        analysis = self.analyze_costs(profile, billing)
        
        recommendations = self.generate_recommendations(profile, billing, analysis)
        if not recommendations:
            return None
        
        total_savings = sum(rec.get('potential_savings', 0) for rec in recommendations)
        current_cost = analysis['total_monthly_cost']
        savings_percentage = (total_savings / current_cost * 100) if current_cost > 0 else 0
        
        high_impact = sum(1 for rec in recommendations 
                         if rec.get('potential_savings', 0) > rec.get('current_cost', 0) * 0.2)
        
        report = {
            "project_name": profile.get('name', 'Unknown'),
            "analysis": analysis,
            "recommendations": recommendations,
            "summary": {
                "total_potential_savings": round(total_savings, 2),
                "savings_percentage": round(savings_percentage, 2),
                "recommendations_count": len(recommendations),
                "high_impact_recommendations": high_impact
            }
        }
        
        return report
    
    def run(self):
        profile = load_json("project_profile.json")
        if not profile:
            print("\n Could not load project_profile.json")
            return False

        billing = load_json("mock_billing.json")
        if not billing:
            print("\n Could not load mock_billing.json")
            return False
        
        print(f"\nAnalyzing costs for: {profile.get('name', 'Unknown')}")
        print("-" * 80)
        
        report = self.create_report(profile, billing)
        if not report:
            return False
        
        if not validate_cost_report(report):
            print(" Generated report is invalid")
            return False
        
        if save_json("cost_optimization_report.json", report):
            analysis = report['analysis']
            summary = report['summary']
            
            print(f"\n{'='*80}")
            print(f"  COST ANALYSIS SUMMARY")
            print(f"{'='*80}")
            print(f"  Total Cost: {format_currency(analysis['total_monthly_cost'])}")
            print(f"  Budget: {format_currency(analysis['budget'])}")
            print(f"  Variance: {format_currency(analysis['budget_variance'])} ", end='')
            print(f"({'OVER BUDGET' if analysis['is_over_budget'] else 'UNDER BUDGET'})")
            print(f"\n  Potential Savings: {format_currency(summary['total_potential_savings'])}")
            print(f"  Savings %: {summary['savings_percentage']:.1f}%")
            print(f"  Recommendations: {summary['recommendations_count']}")
            print(f"  High Impact: {summary['high_impact_recommendations']}")
            print(f"{'='*80}\n")
            
            return True
        
        return False

if __name__ == "__main__":
    analyzer = CostAnalyzer()
    analyzer.run()