import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class StoryVisCrew:
    """StoryVis crew Híbrida e Modular"""
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    agents_config = os.path.join(base_path, 'config', 'agents.yaml')
    tasks_config = os.path.join(base_path, 'config', 'tasks.yaml')

    llm_fast = LLM(
        model=os.getenv("GROQ_MODEL"),
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("BASE_URL")
    )

    # --- AGENTES (Carregados do YAML) ---
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

    @agent
    def math_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['math_analyst'],
            name="Math Analyst",
            verbose=True,
            llm=self.llm_fast
        )

    @agent
    def complex_artist(self) -> Agent:
        return Agent(
            config=self.agents_config['complex_artist'],
            name="Complex Artist",
            verbose=True,
            llm=self.llm_fast
        )

    # --- TAREFAS (Carregadas do YAML) ---

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
            context=[self.develop_code_task()] # Contexto dinâmico pode ser sobrescrito na crew
        )

    @task
    def append_chart_task(self) -> Task:
        return Task(
            config=self.tasks_config['append_chart_task'],
            agent=self.dashboard_developer()
        )

    @task
    def calculate_metrics_task(self) -> Task:
        return Task(
            config=self.tasks_config['calculate_metrics_task'],
            agent=self.math_analyst()
        )

    @task
    def complex_viz_task(self) -> Task:
        return Task(
            config=self.tasks_config['complex_viz_task'],
            agent=self.complex_artist()
        )

    # --- CREWS (DEFINIÇÃO DOS FLUXOS) ---

    # 1. Crew Padrão (Gerar do Zero Simples)
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.dashboard_developer(), self.storyteller()],
            tasks=[self.develop_code_task(), self.create_narrative_task()],
            process=Process.sequential,
            verbose=True,
            max_rpm=2,
            memory=False
        )

    # 2. Crew de Atualização (Adicionar Gráfico)
    def crew_update(self) -> Crew:
        return Crew(
            agents=[self.dashboard_developer()],
            tasks=[self.append_chart_task()],
            process=Process.sequential,
            verbose=True,
            memory=False
        )

    # 3. Crew de Cálculo (Só Números)
    def crew_calculation(self) -> Crew:
        return Crew(
            agents=[self.math_analyst()],
            tasks=[self.calculate_metrics_task()],
            process=Process.sequential,
            verbose=True,
            memory=False
        )

    # 4. Crew Complexa (Substitui o Dev Padrão pelo Artista)
    def crew_complex(self) -> Crew:
        # Aqui precisamos re-configurar o contexto da narrativa manualmente
        narrative_task = self.create_narrative_task()
        complex_task = self.complex_viz_task()
        narrative_task.context = [complex_task] # O narrador agora lê o código complexo

        return Crew(
            agents=[self.complex_artist(), self.storyteller()],
            tasks=[complex_task, narrative_task],
            process=Process.sequential,
            verbose=True,
            memory=False
        )