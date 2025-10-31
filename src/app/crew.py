# src/app/crew.py
# -----------------
import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

# 1. O RAG agora usa 'Knowledge' (importado de 'crewai')
from crewai import Knowledge 

# 2. As Ferramentas (Tools) e Fontes (Sources) vêm de 'crewai_tools'
# 'KnowledgeBaseTool' foi substituída por 'RagTool'
from crewai_tools import FileReadTool, RagTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource


# Importa a ferramenta customizada
from .tools.StreamlitAltairChartsTools import StreamlitAltairChartsTools

# Importação dos modelos Pydantic
from .models import ChartOutput, AnalysisBrief, VizPlan


# --- Carregar Variáveis de Ambiente ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#pdf_tool = PDFKnowledgeSource(file_paths=["ChartStreamlit.md"])

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
            base_url="http://localhost:11434",
            api_key=OPENROUTER_API_KEY,
            temperature=0.7
        )
    elif request == "openai":
        llm = LLM(
            model="ollama/gpt-oss:120b-cloud",
            api_key=OPENAI_API_KEY,
            temperature=0.7
        )
    elif request == "ollama":
        llm = LLM(
            model="ollama/llama3",
            base_url="http://localhost:11434",
            temperature=0.7
        )
    else:
        raise ValueError(f"Modelo LLM desconhecido ou não configurado: {request}")
    
    return llm

@CrewBase
class StoryVisCrew:
    """Crew para o sistema StoryVis"""
    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks.yaml"

    def __init__(self, llm_choice: str = "gemini"):
        """
        Inicializa a crew com o LLM escolhido e configura as ferramentas.
        """
        self.llm = LLMRequest(llm_choice)
        
        self.file_read_tool = FileReadTool()
        
        pdf_path = "storytellingcomdados.pdf" 
        
        pdf_source = PDFKnowledgeSource(file_paths=[pdf_path])
        
        knowledge = Knowledge(
            sources=[pdf_source],
            collection_name="storyvis_rag_collection" 
        )
                        
        self.rag_tool = RagTool(knowledge=knowledge)
        
        self.altair_tool = StreamlitAltairChartsTools()


    # --- Agentes (Com ferramentas atualizadas) ---
    @agent
    def viz_manager(self) -> Agent:
        """Agente gerente que supervisiona todos os outros."""
        return Agent(
            config=self.agents_config["viz_manager"],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def input_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["input_analyst"],
            tools=[self.file_read_tool], # Correto
            llm=self.llm,
            verbose=True
        )

    @agent
    def viz_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["viz_planner"],
            tools=[self.rag_tool], # <--- CORRIGIDO
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def viz_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["viz_generator"],
            tools=[self.altair_tool], # Correto
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def viz_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config["viz_evaluator"],
            tools=[self.rag_tool], # <--- CORRIGIDO
            llm=self.llm,
            verbose=True,
            #output_pydantic=ChartOutput
        )

    # --- Tarefas ---
    @task
    def task_analyze_input(self) -> Task:
        return Task(
            config=self.tasks_config["task_analyze_input"],
            agent=self.input_analyst(),
            output_pydantic=AnalysisBrief
        )

    @task
    def task_plan_visualization(self) -> Task:
        return Task(
            config=self.tasks_config["task_plan_visualization"],
            agent=self.viz_planner(),
            context=[self.task_analyze_input()],
            output_pydantic=VizPlan
        )

    @task
    def task_generate_code(self) -> Task:
        return Task(
            config=self.tasks_config["task_generate_code"],
            agent=self.viz_generator(),
            context=[
                self.task_plan_visualization(),
                self.task_analyze_input() 
            ]
        )

    @task
    def task_evaluate_and_refine(self) -> Task:
        return Task(
            config=self.tasks_config["task_evaluate_and_refine"],
            agent=self.viz_evaluator(),
            context=[
                self.task_generate_code(),
                self.task_plan_visualization()
            ],
            # output_pydantic=ChartOutput
        )

    # --- Crew  ---
    @crew
    def crew(self) -> Crew:
        """Cria e configura a crew do StoryVis (modo hierárquico)."""
        return Crew(
            agents=[
                self.input_analyst(),
                self.viz_planner(),
                self.viz_generator(),
                self.viz_evaluator()
            ],
            tasks=[
                self.task_analyze_input(),
                self.task_plan_visualization(),
                self.task_generate_code(),
                self.task_evaluate_and_refine()
            ],
            process=Process.hierarchical,
            manager_llm=self.llm,        # o gerente usa o mesmo modelo
            manager_agent=self.viz_manager(),  # agente gerente que supervisiona
            verbose=True,
            #knowledge_sources=[pdf_tool]
        )

