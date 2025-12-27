from llm_handler import LLMHandler
from utils import load_text, save_json, validate_project_profile

class ProfileExtractor:
    def __init__(self):
        self.llm = LLMHandler()
    
    def create_extraction_prompt(self,description):
        prompt = f"""You are a cloud infrastructure analyst. Extract a structured project profile from the given description.
        
Project Description:
{description}

Your task: Analyze the description and extract the following information into a JSON object:
- name: A concise project name (string)
- budget_inr_per_month: Monthly budget in Indian Rupees (number, extract from description or estimate if not mentioned)
- description: A brief 1-2 sentence summary (string)
- tech_stack: An object containing technologies mentioned (e.g., frontend, backend, database, hosting, proxy, etc.)
- non_functional_requirements: An array of requirements like scalability, monitoring, security, etc.

CRITICAL RULES:
1. Respond with ONLY a valid JSON object
2. No explanations, no markdown formatting, no code blocks
3. All field names must match exactly as specified
4. budget_inr_per_month must be a number (not a string)
5. If budget is not mentioned, estimate based on project scale (small: 3000-10000, medium: 10000-50000, large: 50000+)

Example output format:
{{
  "name": "Project Name",
  "budget_inr_per_month": 25000,
  "description": "Brief project summary",
  "tech_stack": {{
    "frontend": "react",
    "backend": "nodejs",
    "database": "postgresql",
    "hosting": "aws"
  }},
  "non_functional_requirements": ["scalability", "monitoring"]
}}

Now extract the profile from the description above. Respond with ONLY the JSON object:"""
        
        return prompt
    
    def extract_profile(self,description):
        print("Extracting project profile using LLM")

        prompt = self.create_extraction_prompt(description)
        profile = self.llm.call_llm_for_json(prompt,expected_type="object")

        if not profile:
            print("Failed to extract project profile")
            return None
        
        if not validate_project_profile(profile):
            print("Extracted profile is invalid")
            return None
        
        print("Project Profile extracted successfully")
        return profile
    
    def run(self):
        description = load_text("project_description.txt")
        if not description:
            print("\n Could not load project_description.txt")
            print("Please ensure the file exists in the outputs/directory")
            return False

        print(f"\n Project Description ({len(description)}) characters")
        print("-"*20)
        print(description[:500] + "..." if len(description) > 500 else "")
        print("-" * 20)

        profile = self.extract_profile(description)
        if not profile:
            return False 
        
        if save_json("project_profile.json", profile):
            print(f"\n Project: {profile.get('name', 'Unknown')}")
            print(f" Budget: ₹{profile.get('budget_inr_per_month', 0):,}/month")
            print(f" Tech Stack: {', '.join(profile.get('tech_stack', {}).values())}")
            return True
        
        return False
    
if __name__ == "__main__":
    extractor = ProfileExtractor()
    extractor.run()