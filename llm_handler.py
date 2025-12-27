import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class LLMHandler:
    def __init__(self):

        self.model_name = "mistral:7b-instruct-q4_0"
        
        try:
            self.llm = Ollama(
                model=self.model_name,
                temperature=0.3,
                base_url="http://localhost:11434",
                timeout=180,  
                num_predict=3000,  
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1
            )
            print(f" Initialized LangChain with {self.model_name}")
        except Exception as e:
            print(f" Error initializing Ollama: {str(e)}")
            print("\nMake sure Ollama is running:")
            print("1. Open terminal and run: ollama serve")
            print(f"2. Pull the model: ollama pull {self.model_name}")
            raise

        self.max_retries = 3

    def check_ollama_running(self):
        try:
            test_response = self.llm.invoke("Test")
            return True
        except Exception as e:
            print(f" Ollama not responding: {str(e)}")
            return False

    def call_llm(self, prompt, max_tokens=2000, temperature=0.3):
        try:
            print(f"Calling {self.model_name} via LangChain...")
            
            response = self.llm.invoke(prompt)
            return response
            
        except Exception as e:
            print(f"Error calling LLM: {str(e)}")
            return None

    def extract_json(self, text):
        if not text:
            return None
            
        text = text.strip()
        text = text.replace("```json", "").replace("```", "")
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            try:
                json_str = text[start_idx:end_idx + 1]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        start_idx = text.find('[')
        end_idx = text.rfind(']')
        if start_idx != -1 and end_idx != -1:
            try:
                json_str = text[start_idx:end_idx + 1]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        return None

    def call_llm_for_json(self, prompt, expected_type="object"):
        json_prompt = PromptTemplate(
            input_variables=["prompt"],
            template="{prompt}\n\nIMPORTANT: Respond with ONLY valid JSON. No explanations, no markdown, no code blocks. Just the raw JSON."
        )
        
        for attempt in range(self.max_retries):
            try:
                formatted_prompt = json_prompt.format(prompt=prompt)
                
                response_text = self.call_llm(formatted_prompt, max_tokens=3000)
                
                if not response_text:
                    print(f" Failed to get response. Attempt {attempt + 1}/{self.max_retries}")
                    continue
                
                json_data = self.extract_json(response_text)
                
                if json_data:
                    if expected_type == "object" and isinstance(json_data, dict):
                        print(" Successfully extracted JSON object")
                        return json_data
                    elif expected_type == "array" and isinstance(json_data, list):
                        print(" Successfully extracted JSON array")
                        return json_data
                    else:
                        print(f" Type mismatch: Expected {expected_type}, got {type(json_data).__name__}")
                else:
                    print(f" Could not extract valid JSON from response")
                
                if attempt < self.max_retries - 1:
                    print(f"Retrying with stricter instructions... ({attempt + 2}/{self.max_retries})")
                    prompt += "\n\nCRITICAL INSTRUCTION: You MUST respond with ONLY valid JSON format. Start immediately with { or [ character. No other text allowed."
                    
            except Exception as e:
                print(f" Error in attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    continue
        
        print("✗ All retry attempts exhausted")
        return None

    def test_connection(self):
        print("\n" + "="*60)
        print("Testing LangChain + Ollama Connection")
        print("="*60)
        
        try:
            print("\n1. Testing Ollama connectivity...")
            if not self.check_ollama_running():
                print(" Ollama is not running or not responding")
                print("\nSetup instructions:")
                print("1. Install Ollama from: https://ollama.ai/")
                print("2. Open a terminal and run: ollama serve")
                print(f"3. Pull the model: ollama pull {self.model_name}")
                print("4. Run this test again")
                return False
            
            print(" Ollama is running")
            
            print("\n2. Testing JSON generation...")
            test_prompt = '''Generate a simple JSON object with these fields:
- status: "ok"
- message: "LangChain working"
- model: "llama3"

Respond with ONLY the JSON object, nothing else.'''
            
            response = self.call_llm_for_json(test_prompt, expected_type="object")
            
            if response and isinstance(response, dict):
                print(" JSON extraction working!")
                print(f" Sample response: {json.dumps(response, indent=2)}")
                print("\n" + "="*60)
                print(" ALL TESTS PASSED - LangChain is ready!")
                print("="*60 + "\n")
                return True
            else:
                print(" JSON extraction failed")
                return False
                
        except Exception as e:
            print(f" Connection test failed: {str(e)}")
            return False

class ProjectProfile(BaseModel):
    name: str = Field(description="Project name")
    budget_inr_per_month: float = Field(description="Monthly budget in INR")
    description: str = Field(description="Project description")
    tech_stack: Dict[str, str] = Field(description="Technology stack")
    non_functional_requirements: List[str] = Field(description="Non-functional requirements", default=[])

class BillingRecord(BaseModel):
    month: str = Field(description="Month in YYYY-MM format")
    service: str = Field(description="Cloud service name")
    resource_id: str = Field(description="Resource identifier")
    region: str = Field(description="Cloud region")
    usage_type: str = Field(description="Usage type")
    usage_quantity: float = Field(description="Usage quantity")
    unit: str = Field(description="Unit of measurement")
    cost_inr: float = Field(description="Cost in INR")
    desc: str = Field(description="Description")

class Recommendation(BaseModel):
    title: str = Field(description="Recommendation title")
    service: str = Field(description="Service name")
    current_cost: float = Field(description="Current cost in INR")
    potential_savings: float = Field(description="Potential savings in INR")
    recommendation_type: str = Field(description="Type of recommendation")
    description: str = Field(description="Detailed description")
    implementation_effort: str = Field(description="Implementation effort level")
    risk_level: str = Field(description="Risk level")
    steps: List[str] = Field(description="Implementation steps")
    cloud_providers: List[str] = Field(description="Applicable cloud providers")


if __name__ == "__main__":
    handler = LLMHandler()
    handler.test_connection()