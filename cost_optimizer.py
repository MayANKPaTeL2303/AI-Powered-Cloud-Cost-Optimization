import os
import traceback
import sys 
from profile_extractor import ProfileExtractor
from billing_generator import BillingGenerator
from cost_analyzer import CostAnalyzer
from utils import (
    save_text, load_json, print_seperator, print_header,
    format_currency, ensure_output_dir
)

class CostOptimizer:
    def __init__(self):
        self.profile_extractor = ProfileExtractor()
        self.billing_generator = BillingGenerator()
        self.cost_analyzer = CostAnalyzer()
        ensure_output_dir()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self):
        print_header("CLOUD COST OPTIMIZER - AI Powered Tool")
        print("1. Enter New Project Description")
        print("2. Run Complete Cost Analysis")
        print("3. View Recommendations")
        print("4. Export Report")
        print("5. Exit")
        print_seperator()

    def enter_project_description(self):
        # Option - 1: Enter the project description 
        self.clear_screen()
        print_header("ENTER PROJECT DESCRIPTION")

        print("Enter your project description below.")
        print("Include: project goals, budget, tech stack, requirements")
        print("Type 'END' on a new line when finished.\n")

        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            except EOFError:
                break

        description = '\n'.join(lines).strip()

        if not description:
            print("\n No description is provided")
            input("\n Press Enter to continue ...")
            return False
        
        if save_text("project_description.txt",description):
            print(f"\n Description saved ({len(description)} characters)")
            print("\nDescription preview:")
            print(description[:300] + ("..." if len(description) > 300 else ""))
            print("-" * 30)
        
        input("\nPress Enter to continue...")
        return True
    
    def run_complete_analysis(self):
        # Option 2: Run the complete pipeline
        self.clear_screen()
        print_header("RUNNING COMPLETE COST ANALYSIS")

        # Step 1: Extract Profile
        print("\n[Step 1/3] Extracting Project Profile...")
        print("-"*30)
        if not self.profile_extractor.run():
            print("Profile extraction failed")
            input("\nPress Enter to continue...")
            return False 
        
        print("Profile Extraction completed succesfully")
        input("\nPress Enter to continue to billing generation...")

        #Step 2: Synthetic billing generation
        print("\n[Step 2/3] Generating Synthetic billing...")
        print("-"*30)
        if not self.billing_generator.run():
            print("\n Billing generation failed")
            input("\n Press Enter to continue...")
            return False 
        
        print("\n Billing generation completed")
        input("\nPress Enter to continue to cost analysis...")

        # Step 3: Analyze the costs
        print("\n [Step 3/3] Generating the detailed cost analysis...")
        print("-"*30)
        if not self.cost_analyzer.run():
            print("\n Cost Analysis failed")
            input("\n Press Enter to continue...")
            return False
        
        print("\n Cost Analysis Completed")
        print("="*30)
        print("\n ALL STEPS COMPLETED SUCCESSFULLY! ")
        print("-------------------------")

        print("\n Press Enter to continue!")
        return True
    
    def view_recommendation(self):
        # Option 3: View recommendation summary
        self.clear_screen()
        print_header("COST OPTIMIZATION RECOMMENDATIONS")

        report = load_json("cost_optimization_report.json")
        if not report:
            print("No report found. ")
            input("\n Press Enter to continue...")
            return False
        
        analysis = report.get('analysis',{})
        summary = report.get('summary',{})
        recommendation = report.get('recommendations',{})
        
        print(f"Project: {report.get('project_name', 'Unknown')}")
        print(f"Total Cost: {format_currency(analysis.get('total_monthly_cost', 0))}")
        print(f"Budget: {format_currency(analysis.get('budget', 0))}")
        print(f"Variance: {format_currency(analysis.get('budget_variance', 0))} ", end='')
        print(f"({'OVER BUDGET' if analysis.get('is_over_budget', False) else 'UNDER BUDGET'})")
        print_seperator()

        print(f"Potential Savings: {format_currency(summary.get('total_potential_savings', 0))}")
        print(f"Savings Percentage: {summary.get('savings_percentage', 0):.1f}%")
        print(f"Total Recommendations: {len(recommendation)}")
        print_seperator()

        print("TOP RECOMMENDATIONS:\n")
        for i, rec in enumerate(recommendation[:5], 1):
            print(f"{i}. {rec.get('title', 'Unknown')}")
            print(f"   Service: {rec.get('service', 'Unknown')}")
            print(f"   Current Cost: {format_currency(rec.get('current_cost', 0))}")
            print(f"   Potential Savings: {format_currency(rec.get('potential_savings', 0))}")
            print(f"   Effort: {rec.get('implementation_effort', 'Unknown')} | Risk: {rec.get('risk_level', 'Unknown')}")
            print(f"   Providers: {', '.join(rec.get('cloud_providers', []))}")
            print()

        if len(recommendation) > 5:
            print(f"... and {len(recommendation) - 5} more recommendations")
            print("(See cost_optimization_report.json for full details)")
        
        input("\nPress Enter to continue...")

    def export_report(self):
        # Option 4: Export report in different formats
        self.clear_screen()
        print_header("EXPORT REPORT")
        
        # Load report
        report = load_json("cost_optimization_report.json")
        if not report:
            print(" No report found. ")
            input("\nPress Enter to continue...")
            return
        
        print("Available export formats:")
        print("1. JSON (already saved)")
        print("2. Text Summary")
        print("3. Both")
        print()
        
        choice = input("Select format (1-3): ").strip()
        
        if choice in ['2', '3']:
            # Generate text summary
            summary_text = self.generate_text_summary(report)
            if save_text("cost_optimization_summary.txt", summary_text):
                print("\n Text summary exported to outputs/cost_optimization_summary.txt")
        
        if choice in ['1', '3']:
            print("\n JSON report available at outputs/cost_optimization_report.json")
        
        print("\nAll files are in the 'outputs/' directory")
        input("\nPress Enter to continue...")
    
    def generate_text_summary(self, report):
        analysis = report.get('analysis', {})
        summary = report.get('summary', {})
        recommendations = report.get('recommendations', [])
        
        text = f"""
{'='*20}
CLOUD COST OPTIMIZATION REPORT
{'='*20}

Project: {report.get('project_name', 'Unknown')}
Generated: {report.get('generated_date', 'N/A')}

{'='*20}
COST ANALYSIS
{'='*20}

Total Monthly Cost:    {format_currency(analysis.get('total_monthly_cost', 0))}
Budget:                {format_currency(analysis.get('budget', 0))}
Budget Variance:       {format_currency(analysis.get('budget_variance', 0))}
Status:                {'OVER BUDGET' if analysis.get('is_over_budget', False) else 'UNDER BUDGET'}

Cost Breakdown by Service:
"""
        
        service_costs = analysis.get('service_costs', {})
        for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True):
            text += f"  - {service:20s} {format_currency(cost)}\n"
        
        text += f"""
{'='*20}
OPTIMIZATION SUMMARY
{'='*20}

Total Potential Savings:       {format_currency(summary.get('total_potential_savings', 0))}
Savings Percentage:            {summary.get('savings_percentage', 0):.1f}%
Total Recommendations:         {summary.get('recommendations_count', 0)}
High-Impact Recommendations:   {summary.get('high_impact_recommendations', 0)}

{'='*20}
DETAILED RECOMMENDATIONS
{'='*20}

"""
        
        for i, rec in enumerate(recommendations, 1):
            text += f"{i}. {rec.get('title', 'Unknown')}\n"
            text += f"   Service:           {rec.get('service', 'Unknown')}\n"
            text += f"   Type:              {rec.get('recommendation_type', 'Unknown')}\n"
            text += f"   Current Cost:      {format_currency(rec.get('current_cost', 0))}\n"
            text += f"   Potential Savings: {format_currency(rec.get('potential_savings', 0))}\n"
            text += f"   Implementation:    {rec.get('implementation_effort', 'Unknown')} effort, {rec.get('risk_level', 'Unknown')} risk\n"
            text += f"   Cloud Providers:   {', '.join(rec.get('cloud_providers', []))}\n"
            text += f"   \n   Description:\n   {rec.get('description', 'N/A')}\n"
            text += f"   \n   Implementation Steps:\n"
            for step in rec.get('steps', []):
                text += f"   - {step}\n"
            text += "\n"
        
        text += f"{'='*20}\nEND OF REPORT\n{'='*20}\n"
        
        return text
    

    def run(self):
        # Main CLI 
        while True:
            self.clear_screen()
            self.show_menu()

            choice = input("Select an options from (1-5)").strip()
            if choice == '1':
                self.enter_project_description()
            elif choice == '2':
                self.run_complete_analysis()
            elif choice == '3':
                self.view_recommendation()
            elif choice == '4':
                self.export_report()
            elif choice == '5':
                self.clear_screen()
                print("\n All the output are saved in the '/outputs' directory")
                sys.exit(0)
            else:
                print("Invalid Options. Please select 1-5")
                input("\n Press Enter to continue..")

def main():
    try:
        cli = CostOptimizer()
        cli.run()
    except KeyboardInterrupt:
        print("\n  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
        

