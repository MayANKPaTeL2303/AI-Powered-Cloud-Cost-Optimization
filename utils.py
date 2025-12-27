import os
import json
from pathlib import Path

OUTPUT_DIR = "outputs"

def ensure_output_dir():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

def get_output_path(filename):
    ensure_output_dir()
    return os.path.join(OUTPUT_DIR,filename)

def save_text(filename, content):
    filepath = get_output_path(filename)
    try:
        with open(filepath,'w',encoding='utf-8') as f:
            f.write(content)
        print(f"Saved : {filepath}")
        return True
    except Exception as e:
        print(f"Error saving the {filepath}: {str(e)}")
        return False

def load_text(filename):
    filepath = get_output_path(filename)
    try:
        with open(filepath,'r',encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found")
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {str(e)}")

def save_json(filename,data):
    filepath = get_output_path(filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data,f,indent=2,ensure_ascii=False)
        print(f"Saved: {filepath}")
        return True
    except Exception as e:
        print(f"Error reading {filepath}: {str(e)}")
        return False

def load_json(filename):
    filepath = get_output_path(filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON in {filepath}")
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {str(e)}")
        return None
    
def validate_project_profile(profile):
    required_fields = ["name", "budget_inr_per_month", "description", "tech_stack"]

    if not isinstance(profile,dict):
        print(f"Profile must be JSON")
        return False
    
    for field in required_fields:
        if field not in profile:
            print(f"Missing required field: {field}")
            return False
        
    if not isinstance(profile["budget_inr_per_month"], (int, float)):
        print(" budget_inr_per_month must be a number")
        return False

    if not isinstance(profile["tech_stack"], dict):
        print("tech_stack must be an object")
        return False
    
    return True

def validate_billing_data(billing):
    if not isinstance(billing,list):
        print("Billing data must be array")
        return False
    
    if len(billing) < 12:
        print(f" Billing data should have at least 12 records, got {len(billing)}")
        return False
    
    required_fields = ["month", "service", "cost_inr"]

    for i, record in enumerate(billing):
        if not isinstance(record, dict):
            print(f"Record {i} is not a JSON object")
            return False
        
        for field in required_fields:
            if field not in record:
                print(f"Record {i} missing field: {field}")
                return False
    
    return True

def validate_cost_report(report):
    if not isinstance(report,dict):
        print(f"Report must be JSON object")
        return False

    required_fields = ["project_name", "analysis", "recommendations"]

    for field in required_fields:
        if field not in report:
            print(f"Missing required field: {field}")
            return False
        
    
    if not isinstance(report["recommendations"],list):
        print(f"Recommendation must be array/list")
        return False
    
    if len(report["recommendations"]) < 6:
        print(f"Length of the recommendations must be at least 6")
        return False

    return True

def format_currency(amount):
    return f"₹{amount:,.2f}"

def print_seperator():
    print("\n" + "="*10 + "\n")

def print_header(text):
    print("\n" + "=" * 20)
    print(f"{text}")
    print("="*10 + "\n")
        

    


