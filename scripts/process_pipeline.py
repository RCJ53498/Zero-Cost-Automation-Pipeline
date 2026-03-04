import os
import sys
import json
import argparse
import requests
import re
from datetime import datetime

# Local Ollama endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # Ensure this model is pulled via `ollama pull llama3.2`

def check_ollama_running():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.ConnectionError:
        return False

def extract_with_ollama(transcript_text, previous_memo=None):
    if not check_ollama_running():
        print("MOCK MODE: Ollama not running on localhost:11434. Returning dummy JSON.", file=sys.stderr)
        return {
            "account_id": "dummy_id",
            "company_name": "Mock Company",
            "business_hours": {"days": "M-F", "start": "9:00 AM", "end": "5:00 PM", "timezone": "EST"},
            "office_address": "None mentioned",
            "services_supported": ["Example Service"],
            "emergency_definition": ["Fire", "Flood"],
            "emergency_routing_rules": {"behavior": "Transfer", "transfer_number": "555-0000", "fallback": "Take message"},
            "non_emergency_routing_rules": "Take message",
            "call_transfer_rules": {"timeout_seconds": 30, "retries": 1, "failure_message": "Sorry, unavailable."},
            "integration_constraints": "None",
            "after_hours_flow_summary": "Take message",
            "office_hours_flow_summary": "Standard greeting",
            "questions_or_unknowns": ["What is the specific address?"],
            "notes": "Mocked generation"
        }
        
    example_output = {
      "company_name": "string",
      "business_hours": {
        "days": "string",
        "start": "string",
        "end": "string",
        "timezone": "string"
      },
      "office_address": "string",
      "services_supported": ["string1", "string2"],
      "emergency_definition": ["string1"],
      "emergency_routing_rules": {
        "behavior": "string",
        "transfer_number": "string",
        "fallback": "string"
      },
      "non_emergency_routing_rules": "string",
      "call_transfer_rules": {
        "timeout_seconds": 30,
        "retries": 1,
        "failure_message": "string"
      },
      "integration_constraints": "string",
      "after_hours_flow_summary": "string",
      "office_hours_flow_summary": "string",
      "questions_or_unknowns": ["string1"],
      "notes": "string"
    }

    if previous_memo:
        prompt = f"""
        You are an AI configuration bot reading a client ONBOARDING call transcript.
        Update the following previous configuration (v1) based on the new information in the transcript.
        Return your answer AS A VALID JSON OBJECT ONLY matching the output schema provided below exactly. Do not include markdown code block syntax (like ```json), just the raw JSON object. Never invent or hallucinate data. If a detail is missing, omit the field and explicitly add a description of the missing detail to the `questions_or_unknowns` array. Specifically, extract any specific integration constraints (like "never create sprinkler jobs in ServiceTrade") into the `integration_constraints` field.
        
        Output Schema Format:
        {json.dumps(example_output, indent=2)}

        Previous V1 Config:
        {json.dumps(previous_memo)}
        
        Onboarding Transcript:
        {transcript_text}
        """
    else:
        prompt = f"""
        You are an AI configuration bot reading a client DEMO call transcript.
        Extract the configuration into a structured JSON Object.
        Return your answer AS A VALID JSON OBJECT ONLY matching the output schema provided below exactly. Do not include markdown code block syntax (like ```json), just the raw JSON object. Never invent or hallucinate data. If a detail is missing, omit the field and explicitly add a description of the missing detail to the `questions_or_unknowns` array. Specifically, extract any specific integration constraints into the `integration_constraints` field.
        
        Output Schema Format:
        {json.dumps(example_output, indent=2)}

        Demo Transcript:
        {transcript_text}
        """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",  # Changed from schema to lit 'json' to prevent 500 errors in llama.cpp grammar check
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        text_response = result.get('response', '{}').strip()
        
        # In case the model still outputs markdown backticks, strip them:
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        return json.loads(text_response.strip())
    except Exception as e:
        print(f"Error calling Ollama API: {e}", file=sys.stderr)
        return {"company_name": "API Error", "business_hours": {}}

def create_task_tracker_item(account_id, company_name, call_type):
    """
    Creates a task tracker item in Asana if ASANA_PAT and ASANA_WORKSPACE_ID are provided.
    Otherwise, mocks the task creation and logs it to console.
    """
    asana_pat = os.environ.get("ASANA_PAT", "").strip().strip('"').strip("'")
    workspace_id = os.environ.get("ASANA_WORKSPACE_ID", "").strip().strip('"').strip("'")
    
    if not asana_pat or not workspace_id:
        print(f"MOCK MODE: [Task Tracker] Successfully simulated Asana Task creation for Account {account_id} ({company_name}) - {call_type}")
        return
        
    url = "https://app.asana.com/api/1.0/tasks"
    headers = {
        "Authorization": f"Bearer {asana_pat}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    data = {
        "data": {
            "name": f"[{call_type.upper()}] Configure Clara for {company_name} (Acct: {account_id})",
            "notes": f"Automatically generated task from {call_type} pipeline.",
            "workspace": workspace_id,
            "assignee": "me"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 201:
            task_id = response.json().get("data", {}).get("gid")
            print(f"Successfully created Asana task: {task_id}")
        else:
            print(f"Failed to create Asana task: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error creating Asana task: {e}")

def generate_changes_with_ollama(v1_memo, v2_memo):
    if not check_ollama_running():
        return "# Changelog\n- Mocked changes applied (Ollama not running)."
        
    prompt = f"""
    You are a changelog generator. 
    Compare the following V1 and V2 configurations and generate a nicely formatted markdown changelog detailing exactly what changed, what was added, and what was removed.
    
    V1: {json.dumps(v1_memo)}
    
    V2: {json.dumps(v2_memo)}
    
    Format as:
    # Changelog
    
    ## Additions
    - ...
    ## Modifications
    - ...
    ## Notes
    - ...
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        return response.json().get('response', '')
    except Exception as e:
        return f"# Changelog\nError calling Ollama API: {e}"

def generate_retell_spec(memo, version="v1"):
    business_hours = memo.get("business_hours", {})
    bh_days = business_hours.get('days', 'Unknown')
    bh_start = business_hours.get('start', 'Unknown')
    bh_end = business_hours.get('end', 'Unknown')
    emerg_def = ", ".join(memo.get("emergency_definition", []) or []) or "Unknown"
    
    emerg_routing_rules = memo.get("emergency_routing_rules", {})
    if isinstance(emerg_routing_rules, dict):
        emerg_routing = emerg_routing_rules.get("transfer_number", "Unknown")
    else:
        emerg_routing = "Unknown"
        
    call_transfer_rules = memo.get("call_transfer_rules", {})
    if isinstance(call_transfer_rules, dict):
        timeout = call_transfer_rules.get("timeout_seconds", 30)
        fallback_msg = call_transfer_rules.get("failure_message", "Apologize and promise callback")
    else:
        timeout = 30
        fallback_msg = "Apologize and promise callback"
    
    system_prompt = f"""
You are Clara, the AI receptionist for {memo.get('company_name', 'our company')}.
Business Hours: {bh_days}, {bh_start} to {bh_end}.
Emergencies defined as: {emerg_def}.
Emergency transfer number: {emerg_routing}.

# Business Hours Flow:
- Greeting: "Thank you for calling {memo.get('company_name', 'us')}, this is Clara. How can I help you?"
- Ask purpose of the call.
- Collect caller's name and phone number.
- Based on the request, route or transfer appropriately.
- If transferring and it fails: apologize and say someone will call them back immediately.
- Confirm next steps.
- Ask: "Is there anything else I can help you with today?"
- Close call if no.

# After-Hours Flow:
- Greeting: "Thank you for calling {memo.get('company_name', 'us')} after hours, this is Clara."
- Ask purpose of the call.
- Confirm if it is an emergency ({emerg_def}).
- IF EMERGENCY: Collect name, number, and exact address immediately. Attempt transfer to {emerg_routing}.
- If transfer fails: Apologize, assure them a technician has been notified via text/emergency line and will follow up shortly.
- IF NON-EMERGENCY: Collect details, let them know the office is closed, and schedule/confirm follow-up during regular business hours.
- Ask: "Is there anything else?"
- Close call.

Constraints:
- You must NOT mention tools, function calls, or backend logic to the caller.
- {memo.get('integration_constraints', '')}
    """

    spec = {
        "agent_name": f"{memo.get('company_name', 'Unknown')} Receptionist {version}",
        "voice_style": "Friendly, professional, clear, fast-paced.",
        "system_prompt": system_prompt.strip(),
        "key_variables": {
            "timezone": business_hours.get("timezone", "Unknown"),
            "business_hours_start": bh_start,
            "business_hours_end": bh_end,
            "business_days": bh_days,
            "emergency_routing_number": emerg_routing
        },
        "tool_invocation_placeholders": ["transfer_call", "book_appointment", "send_notification"],
        "call_transfer_protocol": f"Timeout: {timeout}s",
        "fallback_protocol": fallback_msg,
        "version": version
    }
    return spec

def main():
    parser = argparse.ArgumentParser(description="Process transcript into Retell Spec")
    parser.add_argument("file_path", help="Path to transcript text file (e.g., demo_1.txt, onboarding_1.txt)")
    args = parser.parse_args()

    filename = os.path.basename(args.file_path)
    file_stem = os.path.splitext(filename)[0]
    
    # Parse type and id (e.g. demo_1 -> type=demo, id=1)
    match = re.match(r"(demo|onboarding)_(\d+)", file_stem)
    if not match:
        print(f"Error: filename {filename} does not match pattern demo_N or onboarding_N")
        sys.exit(1)
        
    call_type, account_id = match.groups()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "outputs", "accounts", account_id)
    
    with open(args.file_path, "r", encoding="utf-8") as f:
        transcript = f.read()
        
    if call_type == "demo":
        print(f"Processing Demo for Account {account_id}...")
        memo = extract_with_ollama(transcript)
        memo['account_id'] = account_id
        
        v1_dir = os.path.join(out_dir, "v1")
        os.makedirs(v1_dir, exist_ok=True)
        
        spec = generate_retell_spec(memo, version="v1")
        
        with open(os.path.join(v1_dir, "memo.json"), "w") as f:
            json.dump(memo, f, indent=2)
            
        with open(os.path.join(v1_dir, "retell_agent_spec.json"), "w") as f:
            json.dump(spec, f, indent=2)
            
        create_task_tracker_item(account_id, memo.get('company_name', 'Unknown'), "Demo")
        print(f"Successfully created v1 artifacts for account {account_id}")

    elif call_type == "onboarding":
        print(f"Processing Onboarding for Account {account_id}...")
        v1_dir = os.path.join(out_dir, "v1")
        v1_memo_path = os.path.join(v1_dir, "memo.json")
        
        v1_memo = {}
        if os.path.exists(v1_memo_path):
            with open(v1_memo_path, "r") as f:
                v1_memo = json.load(f)
        else:
            print(f"Warning: V1 memo not found for account {account_id}. Creating new one based entirely on onboarding.")
            
        v2_memo = extract_with_ollama(transcript, previous_memo=v1_memo)
        v2_memo['account_id'] = account_id
        
        v2_dir = os.path.join(out_dir, "v2")
        os.makedirs(v2_dir, exist_ok=True)
        
        spec = generate_retell_spec(v2_memo, version="v2")
        
        with open(os.path.join(v2_dir, "memo.json"), "w") as f:
            json.dump(v2_memo, f, indent=2)
            
        with open(os.path.join(v2_dir, "retell_agent_spec.json"), "w") as f:
            json.dump(spec, f, indent=2)
            
        changes = generate_changes_with_ollama(v1_memo, v2_memo)
        with open(os.path.join(v2_dir, "changes.md"), "w") as f:
            f.write(changes)
            
        create_task_tracker_item(account_id, v2_memo.get('company_name', 'Unknown'), "Onboarding Updates")
        print(f"Successfully created v2 artifacts for account {account_id}")

if __name__ == "__main__":
    main()
