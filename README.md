# AI-Powered Cloud Cost Optimizer

An cloud cost optimization system that uses Large Language Models (LLMs) to analyze project requirements, generate synthetic billing data, and provide actionable multi-cloud cost optimization recommendations.

## Project Overview

This tool helps users optimize their cloud infrastructure costs by:
1. **Extracting structured project profiles** from plain-English descriptions using LLM
2. **Generating realistic synthetic cloud billing data** (12-20 records) based on project requirements
3. **Analyzing costs against budgets** with detailed breakdowns
4. **Providing multi-cloud optimization recommendations** (AWS, Azure, GCP, Open-Source alternatives)

## Tech Stack

- **Language**: Python
- **LLM Framework**: LangChain + Ollama
- **Model**: Mistral 7B Instruct (quantized)
- **Libraries**: 
  - `langchain` & `langchain-community` - LLM framework
  - `pydantic` - Data validation
  - `python-dotenv` - Environment variable management
  - `requests` - HTTP requests

## Prerequisites

### Software Requirements
1. **Python**
   ```bash
   python --version 
   ```

2. **Ollama** (Local LLM runtime)
   - Download from: https://ollama.ai/
   - Follow installation instructions for your OS

## Installation & Setup

### Step 1: Clone the Repository
```bash
git clone <your-github-repo-url>
cd AI-POWERED-CLOUD-OPTIMIZER
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install Ollama and Pull Model
```bash
ollama pull mistral:7b-instruct-q4_0
```

### Step 5: Start Ollama Server
**Keep this running in a separate terminal:**
```bash
ollama serve
```

### Step 6: Create Output Directory
```bash
mkdir outputs
```

## Usage

### Running the Application

1. **Ensure Ollama is running:**
   ```bash
   # In Terminal 1
   ollama serve
   ```

2. **Run the application:**
   ```bash
   # In Terminal 2
   python cost_optimizer.py
   ```

### Menu Options

####  Enter New Project Description
- Input your project details in plain English
- Include: project goals, budget, tech stack, requirements
- Type `END` on a new line when finished
- The description is saved to `outputs/project_description.txt`

**Example Input:**
```
Hi, I want to build a market analysis tool for e-commerce. 
The tool should track the highest-selling products each month. 
For the front end, I am using React, for the backend Node.js, 
and MongoDB for storing the data. I'll use Nginx as a proxy server 
and AWS for hosting. My monthly budget is 3000.
END
```

#### Run Complete Cost Analysis
Executes the full pipeline automatically:
1. **Profile Extraction**: Extracts structured data from description
2. **Billing Generation**: Creates synthetic billing records (12 records)
3. **Cost Analysis**: Analyzes costs and generates 6-10 recommendations

**Processing time**: 2-5 minutes total

#### View Recommendations
- Displays a summary of cost optimization recommendations
- Shows top 5 recommendations with:
  - Service being optimized
  - Current cost and potential savings
  - Implementation effort and risk level
  - Applicable cloud providers

#### Export Report
Export in multiple formats:
- **JSON** (detailed machine-readable format)
- **Text** (human-readable summary)
- **Both**

All files saved in `outputs/` directory

#### Exit
Safely exit the application

## Output Files

### 1. project_profile.json
Structured project information extracted from description.

**Example:**
```json
{
  "name": "Market Analysis Tool",
  "budget_inr_per_month": 3000,
  "description": "A tool to track highest-selling products each month",
  "tech_stack": {
    "frontend": "react",
    "backend": "nodejs",
    "database": "mongodb",
    "hosting": "aws",
    "proxy": "nginx"
  },
  "non_functional_requirements": ["scalability", "monitoring", "security"]
}
```

### 2. mock_billing.json
Synthetic cloud billing records (12-20 entries).

**Example:**
```json
[
  {
    "month": "2025-01",
    "service": "EC2",
    "resource_id": "i-web-01",
    "region": "ap-south-1",
    "usage_type": "t3.medium",
    "usage_quantity": 720,
    "unit": "hours",
    "cost_inr": 2500,
    "desc": "Web server"
  }
]
```

### 3. cost_optimization_report.json
Complete analysis with 6-10 recommendations.

**Structure:**
- `project_name`: Project identifier
- `analysis`: Cost breakdown and budget variance
- `recommendations`: Array of optimization suggestions
- `summary`: Total savings and impact metrics

### 4. cost_optimization_summary.txt
Human-readable text report with all details formatted for easy reading.

## Example Workflow

### Input (project_description.txt):
```
Hi, I want to build a market analysis tool for e-commerce. 
The tool should track the highest-selling products each month. 
For the front end, I am using React, for the backend Node.js, 
and MongoDB for storing the data. I'll use Nginx as a proxy server 
and AWS for hosting. My monthly budget is 3000.
```

### Generated Profile (project_profile.json):
```json
{
  "name": "Market Analysis Tool",
  "budget_inr_per_month": 3000,
  "tech_stack": {
    "frontend": "react",
    "backend": "nodejs",
    "database": "mongodb",
    "proxy": "nginx",
    "hosting": "aws"
  }
}
```

### Sample Recommendation:
```json
{
  "title": "Switch to Azure Kubernetes Service (AKS) for backend",
  "service": "backend",
  "current_cost": 3040,
  "potential_savings": 1520,
  "recommendation_type": "alternative_provider",
  "implementation_effort": "high",
  "risk_level": "medium",
  "cloud_providers": ["Azure"]
}
```

## System Architecture

```
┌─────────────────────────────────────────┐
│         User Input (CLI)                │
│    (Plain English Description)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Profile Extractor                  │
│   (LangChain + Mistral 7B)              │
│   Extracts: name, budget, tech_stack    │
└──────────────┬──────────────────────────┘
               │
               ▼ project_profile.json
┌─────────────────────────────────────────┐
│      Billing Generator                  │
│   (LangChain + Mistral 7B)              │
│   Generates: 12-20 billing records      │
└──────────────┬──────────────────────────┘
               │
               ▼ mock_billing.json
┌─────────────────────────────────────────┐
│      Cost Analyzer                      │
│   (LangChain + Mistral 7B)              │
│   Generates: 6-10 recommendations       │
└──────────────┬──────────────────────────┘
               │ 
               ▼ cost_optimization_report.json
┌─────────────────────────────────────────┐
│      Output (JSON + Text)               │
│   - Detailed report                     │
│   - Human-readable summary              │
└─────────────────────────────────────────┘
```

## Tools Used

- **OpenText** for the internship opportunity and project assignment
- **Claude** for AI-powered assistance for debugging
- **Ollama Team** for the excellent local LLM runtime
- **LangChain Community** for the powerful LLM framework
- **Mistral AI** for the open-source Mistral 7B model

---
