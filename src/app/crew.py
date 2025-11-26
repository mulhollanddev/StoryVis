import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class StoryVisCrew:
    """StoryVis crew Invertida (Code First -> Narrative Second)"""
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    agents_config = os.path.join(base_path, 'config', 'agents.yaml')
    tasks_config = os.path.join(base_path, 'config', 'tasks.yaml')

    llm_fast = LLM(
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    # --- AGENTES ---
    @agent
    def dashboard_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['dashboard_developer'],
            name="Dashboard Developer",
            verbose=True,
            llm=self.llm_fast
        )

    @agent
    def storyteller(self) -> Agent:
        return Agent(
            config=self.agents_config['storyteller'], # Pode manter a config antiga ou simplificar
            name="Storyteller",
            verbose=True,
            llm=self.llm_fast 
        )

    # --- TAREFAS (ORDEM INVERTIDA) ---

    # 1. Primeiro geramos o código
    @task
    def develop_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['develop_code_task'],
            agent=self.dashboard_developer()
            # Sem contexto, ele olha direto pro input do usuário
        )

    # 2. Depois analisamos o código gerado
    @task
    def create_narrative_task(self) -> Task:
        return Task(
            config=self.tasks_config['create_narrative_task'],
            agent=self.storyteller(),
            context=[self.develop_code_task()] # <--- Recebe o código aqui
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            max_rpm=2,
            memory=False
        )