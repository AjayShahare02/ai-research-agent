import os
from dotenv import load_dotenv

# Try importing from newer/classic path, fallback to standard path
try:
    from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
except ImportError:
    from langchain.agents import AgentExecutor, create_openai_tools_agent

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from tools import scrape_url, web_search

load_dotenv()

# Setup OpenRouter LLM
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0,
)


def build_search_agent() -> AgentExecutor:
    """Creates the Search Agent for web querying."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert research agent. Use web_search to find accurate information.",
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    tools = [web_search]
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)


def build_reader_agent() -> AgentExecutor:
    """Creates the Reader Agent using BeautifulSoup scraping."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert reader. Pick the best URL and scrape it using scrape_url.",
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    tools = [scrape_url]
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)


# Writer Chain
writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured reports.",
        ),
        (
            "human",
            """Write a detailed research report.

Topic: {topic}
Research Gathered: {research}

Structure:
- Introduction
- Key Findings (min 3 points)
- Conclusion
- Sources""",
        ),
    ]
)
writer_chain = writer_prompt | llm | StrOutputParser()

# Critic Chain
critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp research critic. Review and score the report.",
        ),
        (
            "human",
            """Evaluate this report:

Report: {report}

Format:
Score: X/10
Strengths: ...
Areas to Improve: ...
Verdict: ...""",
        ),
    ]
)
critic_chain = critic_prompt | llm | StrOutputParser()