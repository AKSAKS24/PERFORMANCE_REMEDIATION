import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.prompts import SYSTEM_PROMPT

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

MODEL_NAME = os.getenv("LLM_MODEL", "gpt-5")  # Set to 'gpt-5' when available

_llm = ChatOpenAI(
    model=MODEL_NAME,
    # temperature=0.1,
    openai_api_key=OPENAI_API_KEY,
)

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "System date (use exactly as-is for the required tag): {system_date}\n\nABAP source code to remediate:\n{code}"),
    ]
)

_chain = _prompt | _llm | StrOutputParser()

async def run_chain(system_date: str, code: str) -> str:
    return await _chain.ainvoke({"system_date": system_date, "code": code})