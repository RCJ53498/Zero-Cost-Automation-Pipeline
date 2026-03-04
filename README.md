# Clara Zero-Cost Automation Pipeline

## Project Overview

This assignment builds a zero-cost automation layer that takes conversational transcripts of demo and onboarding calls, extracts operations logic systematically, and turns them into highly structured, context-aware prompt templates (v1 and v2) for the Retell agent AI. 

To comply exactly with the "zero spend" limits and entirely prevent AI-Vendor API rate-limiting issues, this build delegates all parsing to a **local open-source hardware LLM (`llama3.2`) via Ollama**.

## Demonstration Video

Watch the end-to-end pipeline demonstration here: [Clara Pipeline Demo (Loom)](https://drive.google.com/file/d/1CY2x7lxrp4hRZs1J1y6U_92q01beVZdf/view?usp=drive_link)

### The Pipeline Architecture

- **Inputs**: Conversational transcripts from Demo (Pipeline A) and Onboarding (Pipeline B) calls. Stored locally in `data/`.
- **Extractor**: A heuristic Python module `scripts/process_pipeline.py`. It utilizes a local installation of **Ollama** running locally (on `localhost:11434`) to perform 100% free, private API extraction modeling without depending on paid endpoints. It enforces strict JSON schemas computationally.
- **Outputs**:
  - `outputs/accounts/<id>/v1`: The demo-derived assumptions and Retell Agent Specs. 
  - `outputs/accounts/<id>/v2`: The onboarding-confirmed rules and updated Retell Specs.
  - `changes.md`: Generates a changelog comparing `v1` and `v2`.
- **Orchestration**: An exported n8n workflow (`workflows/clara_n8n_workflow.json`) showing how this python inference orchestration engine plugs into standard low-code enterprise automation platforms.


## Data Flow

1. Transcripts are placed into the `data/` directory.
2. The orchestrator triggers `python scripts/process_pipeline.py <file>` or the batch scheduler `python scripts/run_all.py`.
3. The local Ollama model securely parses and extracts the variables mapped directly against our enforced JSON schema: Business Hours, Emergency rules, Transfer timeouts.
4. The extraction is parsed cleanly out, and piped automatically into the payload `generate_retell_spec` function which wraps this data into the Retell agent config.
5. The outputs are saved idempotently into `outputs/` representing clean separation between V1 concepts and V2 onboarding definitions.

## Setup Instructions

**1. Install Python Requirements**
Ensure you install the basic HTTP networking requirements.

**2. Install and Start Ollama**
You must install Ollama to provide the offline AI parsing functionality.
- **Windows**: `winget install Ollama.Ollama --accept-source-agreements`
- **Mac/Linux**: Install from `ollama.com` directly.
- Download the local parsing model in your terminal: `ollama pull llama3.2`

**3. Configure Task Tracker Integration (Optional)**
The pipeline automatically integrates with Asana to log task progress. To enable this, set the following environment variables. If left empty, the script gracefully falls back to mock logic and continues tracking tasks in the terminal entirely free.

- **Windows PowerShell**:
  ```powershell
  $env:ASANA_PAT="your-asana-personal-access-token"
  $env:ASANA_WORKSPACE_ID="your-workspace-id"
  ```
- **Linux/Mac**:
  ```bash
  export ASANA_PAT="your-asana-personal-access-token"
  export ASANA_WORKSPACE_ID="your-workspace-id"
  ```

**4. Run the Automaton Local Pipeline**
Ensure Ollama is running (`http://127.0.0.1:11434`).
```bash
python scripts/run_all.py
```
*(Processing runs completely offline based on local hardware speeds. The script takes about 1-2 minutes per transcript on a standard SSD-equipped desktop to extract schemas). If Ollama crashes or isn't installed, the pipeline safely downgrades into `MOCK MODE` static fallback loops to preserve process robustness.*


## Manual Retell Configuration

Because the Retell Voice free tier platform generally does not permit programmatic agent creation, follow these steps to manually configure your agent using the generated AI specs:

1. **Dashboard Login:** Open your [Retell Console](https://www.retellai.com/) and navigate to the **Agents** tab on the left sidebar.
2. **Create Agent:** Click the **Create Agent** button.
3. **Select Voice:** Choose a voice style that matches your company persona (e.g., a friendly ElevenLabs preset).
4. **Locate Your Spec:** On your local machine, open the updated pipeline file for your target account (e.g., `outputs/accounts/1/v2/retell_agent_spec.json`).
5. **Paste System Prompt:** Copy the exact string value of the `"system_prompt"` field from your JSON file. Paste this entirely into the **System Prompt** text box in the Retell UI.
6. **Tool Placeholders (Leave Blank):** Even though our JSON lists `"tool_invocation_placeholders"`, do not add explicit tools in the UI unless you have tied them to active webhooks. Our injected prompt hygiene natively forces the AI to securely collect data *without* trying to verbally trigger backend logic.
7. **Save & Test:** Save your agent and use the Retell Web Call testing interface to simulate a conversation!

## n8n Integration

To view the orchestrator scaffold layout in a real workflow scenario:
1. Run local n8n open source. Docker example: 
   `docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n docker.n8n.io/n8nio/n8n`
2. Launch `localhost:5678`, select **Workflows -> Import from File**.
3. Import `workflows/clara_n8n_workflow.json`. You will see our local `.py` scripts nested seamlessly as Execute Nodes to batch operations properly within the local OS environment safely.
4. **Important Path Configuration**: Double-click the **Execute Pipeline** node in n8n and change the `Command` path to match where you cloned this repository (e.g., `python C:/path/to/ZenTrades/scripts/run_all.py`).
