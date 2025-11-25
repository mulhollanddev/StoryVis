import os
from crewai import  LLM

groq_llm = LLM(
        model=os.getenv("GROQ_MODEL"), 
        temperature=0.1,
        base_url="https://api.groq.com/",
        api_key=os.getenv("GROQ_API_KEY")
    )

print(groq_llm)