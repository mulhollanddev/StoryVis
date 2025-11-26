import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class StoryVisCrew:
    """StoryVis crew Híbrida"""
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    agents_config = os.path.join(base_path, 'config', 'agents.yaml')
    tasks_config = os.path.join(base_path, 'config', 'tasks.yaml')

    llm_fast = LLM(
        model=os.getenv("GROQ_MODEL"),
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("BASE_URL")
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
            config=self.agents_config['storyteller'],
            name="Storyteller",
            verbose=True,
            llm=self.llm_fast 
        )

    # --- TAREFAS NORMAIS (CRIAÇÃO) ---
    @task
    def develop_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['develop_code_task'],
            agent=self.dashboard_developer()
        )

    @task
    def create_narrative_task(self) -> Task:
        return Task(
            config=self.tasks_config['create_narrative_task'],
            agent=self.storyteller(),
            context=[self.develop_code_task()]
        )

    # --- NOVA TAREFA (ATUALIZAÇÃO) ---
    @task
    def append_chart_task(self) -> Task:
        return Task(
            config=self.tasks_config['append_chart_task'],
            agent=self.dashboard_developer() 
            # Reusamos o Developer, pois ele sabe codar
        )

    # --- CREW PADRÃO (GERAR DO ZERO) ---
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=[self.develop_code_task(), self.create_narrative_task()],
            process=Process.sequential,
            verbose=True,
            max_rpm=2,
            memory=False
        )

    # --- NOVA CREW (ATUALIZAR) ---
    def crew_update(self) -> Crew:
        return Crew(
            agents=[self.dashboard_developer()], # Só precisa do Dev
            tasks=[self.append_chart_task()],    # Só roda a tarefa de append
            process=Process.sequential,
            verbose=True,
            memory=False
        )