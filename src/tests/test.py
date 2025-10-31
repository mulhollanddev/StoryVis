from crewai import Agent, Crew, Process, Task, LLM


llm = LLM(
            model="ollama/qwen3-coder:480b-cloud",
            base_url="http://localhost:11434",
            temperature=0.7
        )

print(llm)