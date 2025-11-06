# src/app/crew.py
import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

# Imports de Ferramentas (corrigidos)
from crewai import Knowledge 
from crewai_tools import FileReadTool, RagTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource


# Importa a ferramenta customizada (placeholder)
from .tools.StreamlitAltairChartsTools import StreamlitAltairChartsTools 

# --- IMPORTAÇÃO DOS NOVOS MODELOS Pydantic ---
from .models import ChartOutput, AnalysisBrief, DashboardPlan

# --- Carregar Variáveis de Ambiente ---
load_dotenv()
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY      = os.getenv("GOOGLE_API_KEY") 
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
BASE_URL            = os.getenv("BASE_URL")

# --- Caminhos Absolutos ---
_BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
_CONFIG_DIR         = os.path.join(_BASE_DIR, 'config')
AGENTS_CONFIG_PATH  = os.path.join(_CONFIG_DIR, 'agents.yaml')
TASKS_CONFIG_PATH   = os.path.join(_CONFIG_DIR, 'tasks.yaml')

# Recebe do front a LLM escolhida pelo participante
def LLMRequest(request: str) -> LLM:
    """Seleciona e configura o LLM com base na escolha do usuário."""
    if request == "gemini":
        llm = LLM(
            model="gemini/gemini-2.5-flash", 
            api_key=GEMINI_API_KEY,
            temperature=0.7
        )
    elif request == "deepseek":
        # deepseek-v3.1:671b-cloud
        llm = LLM(
            # model="openrouter/deepseek/deepseek-r1",
            # base_url="https://openrouter.ai/api/v1", deepseek-v3.1:671b-cloud
            model="ollama/deepseek-v3.1:671b-cloud",
            base_url=BASE_URL,
            temperature=0.7
        )
    elif request == "openai":
        llm = LLM(
            model="ollama/gpt-oss:120b-cloud",
            base_url="http://localhost:11434",
            temperature=0.7
        )
    elif request == "ollama":
        llm = LLM(
            model="ollama/llama3",
            base_url=BASE_URL,
            temperature=0.7
        )
    else:
        raise ValueError(f"Modelo LLM desconhecido ou não configurado: {request}")
    

    resp = request.get(f"http://localhost:11434/api/tags", timeout=3)
    print(">>> Resposta do servidor Ollama:", resp)
    return llm

@CrewBase
class StoryVisCrew:
    """Crew para o sistema StoryVis 2.0 (Hierárquico)"""
    agents_config = AGENTS_CONFIG_PATH
    tasks_config = TASKS_CONFIG_PATH

    def __init__(self, llm_choice: str = "gemini"):
        self.llm = LLMRequest(llm_choice)
        
        # Ferramenta para o Analista de Dados
        self.file_read_tool = FileReadTool()
        
        # Ferramenta para o Arquiteto (RAG Teórico)
        pdf_path = "storytellingcomdados.pdf" 
        pdf_source = PDFKnowledgeSource(file_paths=[pdf_path])
        knowledge_teorico = Knowledge(
            sources=[pdf_source],
            collection_name="storyvis_teoria_rag" 
        )
        self.rag_tool_teoria = RagTool(knowledge=knowledge_teorico)
        
        # Ferramenta para o Gerador (RAG Técnico)
        # (Idealmente, 'knowledge/altair_docs.pdf' ou similar)
        # Vamos usar a ferramenta placeholder por enquanto
        self.rag_tool_tecnica = StreamlitAltairChartsTools()


    # --- Agentes (Trabalhadores) ---
    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["data_analyst"],
            tools=[self.file_read_tool], 
            llm=self.llm,
            verbose=True
        )

    @agent
    def dashboard_architect(self) -> Agent:
        return Agent(
            config=self.agents_config["dashboard_architect"],
            tools=[self.rag_tool_teoria],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def viz_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["viz_generator"],
            tools=[self.rag_tool_tecnica],
            llm=self.llm,
            verbose=True,
        )
    
    @agent
    def narrative_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["narrative_generator"],
            tools=[], # Não precisa de ferramentas, só de contexto
            llm=self.llm,
            verbose=True
        )

    # --- Agente Gerente ---
    @agent
    def viz_manager(self) -> Agent:
        """Define o agente gerente do projeto."""
        return Agent(
            config=self.agents_config["viz_manager"],
            llm=self.llm,
            verbose=True
        )

    # --- Tarefas (SEM 'context' e com Pydantic) ---
    
    @task
    def task_analyze_data(self) -> Task:
        """Tarefa de análise de dados."""
        return Task(
            config=self.tasks_config["task_analyze_data"],
            agent=self.data_analyst(),
            output_pydantic=AnalysisBrief
        )

    @task
    def task_plan_dashboard(self) -> Task:
        """Tarefa de planejamento do dashboard."""
        return Task(
            config=self.tasks_config["task_plan_dashboard"],
            agent=self.dashboard_architect(),
            output_pydantic=DashboardPlan
            # 'context' é removido; o gerente vai passar o AnalysisBrief
        )

    @task
    def task_generate_viz_json(self) -> Task:
        """Tarefa de geração de JSON do Altair."""
        return Task(
            config=self.tasks_config["task_generate_viz_json"],
            agent=self.viz_generator()
            # 'context' é removido; o gerente vai passar o DashboardPlan
            # A saída é uma string JSON, então Pydantic não é necessário aqui,
            # mas sim no output final da crew.
        )

    @task
    def task_generate_narrative(self) -> Task:
        """Tarefa de geração de narrativa."""
        return Task(
            config=self.tasks_config["task_generate_narrative"],
            agent=self.narrative_generator()
            # 'context' é removido; o gerente vai passar o DashboardPlan
        )
        
    # --- Tarefa Final (Agregadora) ---
    # Precisamos de uma tarefa final para o gerente "forçar"
    # a montagem do ChartOutput Pydantic
    @task
    def task_assemble_output(self) -> Task:
        """
        Tarefa final, executada pelo gerente, para montar o ChartOutput.
        Esta tarefa recebe o JSON do viz_generator e a Narrativa do 
        narrative_generator e os combina no Pydantic final.
        """
        return Task(
            description="Montar o pacote final 'ChartOutput' para o usuário. "
                        "Combine o 'final_code' (a string JSON do Altair do viz_generator) "
                        "e o 'evaluation_report' (a string Markdown do narrative_generator).",
            expected_output="O objeto Pydantic 'ChartOutput' final e completo.",
            agent=self.viz_manager(),
            output_pydantic=ChartOutput
            # O gerente vai garantir que esta tarefa receba o contexto 
            # de task_generate_viz_json e task_generate_narrative
        )


    # --- Crew (MODO HIERÁRQUICO) ---
    @crew
    def crew(self) -> Crew:
        """Cria e configura a crew do StoryVis (modo hierárquico)."""
        return Crew(
            agents=[
                # A lista de 'agents' contém APENAS os trabalhadores
                self.data_analyst(),
                self.dashboard_architect(),
                self.viz_generator(),
                self.narrative_generator()
            ],
            tasks=[
                # A lista de 'tasks' contém todas as tarefas disponíveis
                self.task_analyze_data(),
                self.task_plan_dashboard(),
                self.task_generate_viz_json(),
                self.task_generate_narrative(),
                self.task_assemble_output() # A tarefa final de montagem
            ],
            process=Process.hierarchical,
            manager_llm=self.llm,
            manager_agent=self.viz_manager(), # O gerente supervisiona
            verbose=True
        )