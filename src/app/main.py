import os
from crewai import Agent, Crew, Process, Task, LLM
from dotenv import load_dotenv

load_dotenv()


llm = LLM(
    model=os.getenv("GROQ_MODEL"),
    temperature=0.1,
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

