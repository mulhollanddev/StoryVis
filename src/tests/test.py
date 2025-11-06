from crewai import Agent, Crew, Process, Task, LLM
import os

BASE_URL = os.getenv("BASE_URL")

llm = LLM(
    model="ollama/gpt-oss:120b-cloud",
    base_url="http://localhost:11434",
    temperature=0.7
    )

print(llm.call("oi"))