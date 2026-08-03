AI RESEARCH AGENT

Overview
AI Research Agent is an interactive web application built with Streamlit. It automates complex research tasks, runs critic evaluations, and generates comprehensive research reports that users can view in real time or download directly in Markdown format.

Key Features

Multi-Agent Workflow: Uses specialized AI agents to collect data and write reports.

Automated Evaluation: Runs critic evaluations to ensure research accuracy and quality.

One-Click Export: Easily download generated reports in .md format.

Interactive Dashboard: User-friendly web interface powered by Streamlit.

Project Structure

app.py: Main Streamlit dashboard and user interface logic.

agents.py: Definitions and workflow for the AI research agents.

tools.py: Custom research tools and API integrations.

requirements.txt: List of Python packages required to run the app.

Dockerfile: Container configuration for Google Cloud Run deployment.

Local Setup Instructions

Clone the repository:
git clone https://github.com/AjayShahare02/ai-research-agent.git
cd ai-research-agent

Create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate

Install required libraries:
pip install -r requirements.txt

Configure environment variables:
Create a file named .env in the main project directory and add your API keys:
GEMINI_API_KEY=your_api_key_here
TAVILY_API_KEY=your_api_key_here

Launch the Streamlit application:
streamlit run app.py

Deployment

Google Cloud Run:

Ensure your Dockerfile is present in the root directory.

Deploy directly via Google Cloud Console or gcloud CLI.

Add your environment variables in the Cloud Run container configuration settings.
